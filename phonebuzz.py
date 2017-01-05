from flask import Flask, abort, request
from functools import wraps
from twilio import twiml
from twilio.util import RequestValidator
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.txt')


def validate_twilio(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(config['Twilio']['AuthToken'])

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

if __name__ == "__main__":
    app.run()
