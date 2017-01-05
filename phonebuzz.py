from flask import Flask, abort, render_template, request
from functools import wraps
from twilio import twiml
from twilio.rest import TwilioRestClient
from twilio.util import RequestValidator
from os import environ

app = Flask(__name__)

def validate_twilio(func):
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

@app.route('/phase2', methods=['GET'])
def number_submission():
    return render_template("phase2.html")

@app.route('/phase2', methods=['POST'])
def call_with_prompt():
    client = TwilioRestClient(environ['TWILIO_SID'], environ['TWILIO_AUTH'])

    client.calls.create(url=request.url[:-1] + '1', to=request.form['phone_number'],
                        from_="+12406247052")


if __name__ == "__main__":
    app.run()
