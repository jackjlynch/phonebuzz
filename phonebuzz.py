from flask import Flask, abort, redirect, render_template, request, url_for
from functools import wraps
from twilio import twiml
from twilio.rest import TwilioRestClient
from twilio.util import RequestValidator
from os import environ
from celery import Celery
from datetime import datetime

def make_celery(app):
    """Initialize a celery instance for delayed tasks"""
    celery = Celery('phonebuzz', backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

# create the flask app
app = Flask(__name__)
app.config.update(
    CELERY_RESULT_BACKEND=environ['REDIS_URL'],
    CELERY_BROKER_URL=environ['REDIS_URL']
)

celery = make_celery(app)

def validate_twilio(func):
    """Validate twilio headers"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(environ['TWILIO_AUTH'])

        # verify that the twilio headers are signed
        if validator.validate(request.url, request.form,
                              request.headers.get('X-TWILIO-SIGNATURE', '')):
            return func(*args, **kwargs)
        return abort(403)
    return decorated_function

def fizzbuzz(maximum):
    """Generate a string of fizz buzz up to and including the maximum"""
    results = ''
    for i in range(1, maximum + 1):
        if i % 3 == 0 and i % 5 == 0:
            results += "fizz buzz "
        elif i % 3 == 0:
            results += "fizz "
        elif i % 5 == 0:
            results += "buzz "
        else:
            results += str(i) + ' '
    return results

def redirect_url(default='phase1'):
    """Get the url of the previous page"""
    return request.args.get('next') or request.referrer or url_for(default)

@app.route('/phase1_response', methods=['GET', 'POST'])
@validate_twilio
def read_fizzbuzz():
    response = twiml.Response()
    response.say(fizzbuzz(int(request.values['Digits'])))
    return str(response)

@app.route('/phase1', methods=['GET', 'POST'])
@validate_twilio
def generate_twiml():
    response = twiml.Response()
    with response.gather(action='phase1_response') as gather:
        gather.say("Please enter a number followed by the pound sign")
    return str(response)

@celery.task()
def call_with_prompt(number):
    """Call the given phone number and read it the fizzbuzz prompt"""
    client = TwilioRestClient(environ['TWILIO_SID'], environ['TWILIO_AUTH'])

    client.calls.create(url=environ['TWILIO_URL'], to=number,
                        from_=environ['TWILIO_NUMBER'])

@app.route('/phase2', methods=['GET'])
def number_submission():
    return render_template("phase2.html")

@app.route('/phase2', methods=['POST'])
def handle_phase2_form():
    call_with_prompt(request.form['phone_number'])

    return redirect(redirect_url())

@app.route('/phase3', methods=['GET'])
def number_submission_with_delay():
    return render_template("phase3.html")

@app.route('/phase3', methods=['POST'])
def delayed_call():
    call_with_prompt.apply_async((request.form['phone_number'],), countdown=int(request.form['seconds']))

    return redirect(redirect_url())

#
# phase 4
#

# just going to keep the call history simply in memory
# as opposed to a more complicated db setup
call_history = {}

@app.route('/phase4_response', methods=['GET', 'POST'])
@validate_twilio
def read_fizzbuzz_logged():
    response = twiml.Response()
    response.say(fizzbuzz(int(request.values['Digits'])))
    print(str(call_history))
    call_history[request.form['CallSid']].fizzbuzz = request.values['Digits']
    return str(response)

@app.route('/phase4_call', methods=['GET', 'POST'])
@validate_twilio
def generate_twiml_logged():
    response = twiml.Response()
    with response.gather(action='phase4_response') as gather:
        gather.say("Please enter a number followed by the pound sign")
    return str(response)

@celery.task()
def call_with_logged_prompt(number):
    """Call the given phone number and read it the fizzbuzz prompt"""
    client = TwilioRestClient(environ['TWILIO_SID'], environ['TWILIO_AUTH'])

    call = client.calls.create(url=environ['TWILIO_URL_LOGGED'], to=number,
                               from_=environ['TWILIO_NUMBER'])
    return call.sid

@app.route('/phase4', methods=['GET'])
def history_page():
    return render_template("phase4.html", call_history=call_history)

@app.route('/phase4', methods=['POST'])
def logged_call():
    task = call_with_logged_prompt.apply_async((request.form['phone_number'],),
                                               countdown=int(request.form['seconds']))
    sid = task.get()
    call_history[sid] = {'phone_number': request.form['phone_number']}
    call_history[sid]['time'] = str(datetime.now())
    call_history[sid]['delay'] = request.form['seconds']

    return redirect(redirect_url())

if __name__ == "__main__":
    app.run()
