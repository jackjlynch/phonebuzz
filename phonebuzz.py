from flask import Flask
from flask import request
from twilio import twiml

app = Flask(__name__)

def fizzbuzz(maximum):
    results = ''
    for i in range(maximum + 1):
        if i % 3 == 0 and i % 5 == 0:
            results += "fizz buzz"
        elif i % 3 == 0:
            results += "fizz"
        elif i % 5 == 0:
            results += "buzz"
        else:
            results += str(i)
    return results

@app.route('/phase1', methods=['GET', 'POST'])
def generate_twiml():
    response = twiml.Response()
    if len(request.data) > 0:
        response.say(fizzbuzz(int(request.data)))
    else:
        response.say("Please enter a number followed by the pound sign")
        response.gather()

    return str(response)

if __name__ == "__main__":
    app.run()
