#envaya_nexmo

Custom RapidSMS backend using Nexmo for Outgoing and EnvayaSMS for incoming message cycles.

Installation
============

Check out http://rapidsms.readthedocs.org/en/latest/main/installation.html for how to install RapidSMS.

Then, in your project directory:

```
$ git clone https://knightsamar@bitbucket.org/knightsamar/envaya_nexmo.git
```
In `settings.py` put:

Add `"envaya_nexmo"` to the list `INSTALLED_APPS`.

Add the following to `INSTALLED_BACKENDS`:

```
    'envaya_nexmo': {
        "ENGINE"    : 'envaya_nexmo.backend.NexmoOutgoingBackend', #Register only the outgoing backend
        "api_key"   : 'API_KEY', #you will get this from Nexmo
        "api_secret": 'API_SECRET', #you will get this from Nexmo
        "sender_name" : 'HEWE', #check your local telecom regulator on whether you can use a custom shortcode
    }
```

In `urls.py` put:

```
urlpatterns = patterns('',
    (r'^envaya_nexmo/', include('envaya_nexmo.urls')),
)
```

Finally, set up EnvayaSMS on an Android phone. See http://sms.envaya.org/install/ for how to install EnvayaSMS on a real phone, or http://sms.envaya.org/test/ for how to test on your local machine. EnvayaSMS has some great documentation on how to further set up EnvayaSMS.

Once you have EnvayaSMS running, set URL to point to the `http://YOUR.SERVER.IP.ADDRESS:PORT/envaya_nexmo/`

And now enjoy receiving SMSes through EnvayaSMS and sending them through Nexmo!

Setting up logging
==================

This is an optional step. Setting up logging properly, will help you set troubleshoot any issues. 

To setup the logger, add the following to your `settings.py` in the  LOGGING section.

```
        'envaya_nexmo' : {
            'handlers' : ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
```

This will direct all the logger messages to rapidsms-debug.log (or the relevant file configured in the handlers dictionary in your LOGGING settings.

How does it work?
=================

There are 4 players in the whole scene:

1. EnvayaSMS Django app for RapidSMS (this application!)
1. Your RapidSMS app (which also includes RapidSMS itself)
1. EnvayaSMS Android app (which runs on the phone)
1. Nexmo API (libpynexmo)

####Outgoing message cycle

The outgoing message cycle works as follows:

1. Message is received by the `send` method of the NexmoOutgoingBackend from `backend.py`
1. The message is sent to the Nexmo REST API using the libpynexmo backend.

####Incoming message cycle

The incoming message cycle works as follows:

1. Message is received by the EnvayaSMS Android app.
1. The message is then forwarded to the EnvayaSMS Django app at the URL configured in the Android app, which is actually a view implementation of EnvayaSMSBackendView (and a form behind it) from `views.py`
1. The EnvayaSMS Django app validates it and sends it to the router for further processing.
