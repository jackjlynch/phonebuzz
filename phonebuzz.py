from flask import Flask
from flask import request
from twilio import twiml

app = Flask(__name__)

def fizzbuzz(maximum):
    results = ''
    for i in range(1, maximum + 1):
        if i % 3 == 0 and i % 5 == 0:
            results += "fizz buzz"
        elif i % 3 == 0:
            results += "fizz"
        elif i % 5 == 0:
            results += "buzz"
        else:
            results += str(i)
    return results

@app.route('/phase1_response', methods=['GET', 'POST'])
def read_fizzbuzz():
    response = twiml.Response()
    response.say(fizzbuzz(int(request.values['Digits'])))
    return str(response)

@app.route('/phase1', methods=['GET', 'POST'])
def generate_twiml():
    response = twiml.Response()
    with response.gather(action='phase1_response') as gather:
        gather.say("Please enter a number followed by the pound sign")
    return str(response)

if __name__ == "__main__":
    app.run()
