from flask import Flask
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
    response.say("Please enter a number")

    return str(response)

if __name__ == "__main__":
    app.run()
