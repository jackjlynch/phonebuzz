# Phonebuzz

Running Phonebuzz
------------------
Requirements:
* Python 3
* Redis server
```
pip install -r requirements.txt
celery -A phonebuzz.celery worker &
python phonebuzz.py
```
Alternatively, `heroku local` will also launch phonebuzz if you have heroku installed.
The following environment variables must be set:
* REDIS_URL: the url of the redis server
* TWILIO_AUTH: your Twilio auth key
* TWILIO_NUMBER: the Twilio number to call from in phases 2, 3 and 4
* TWILIO_SID: your Twilio sid
* TWILIO_URL: the url of the TwiML for the phase 2 and 3 calls
* TWILIO_URL_LOGGED: the url of the TwiML for the phase 4 call

The Phonebuzz phases are accessible at:

1. (240) 624-7052
2. https://pacific-atoll-20313.herokuapp.com/phase2
3. https://pacific-atoll-20313.herokuapp.com/phase3
4. https://pacific-atoll-20313.herokuapp.com/phase4


Current limitations/to do (due to limited time):
-----------------
* Phase 4 isn't functional as is. In order for it to work, the current logging system should be replaced with a database.
* There is no input validation for the forms
* Tests should be added
* There is currently not much error handling
