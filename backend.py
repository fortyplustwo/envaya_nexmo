from rapidsms.backends.base import BackendBase
from rapidsms.backends.http.views import GenericHttpBackendView
from rapidsms.router import receive
from nexmo.libpynexmo.nexmomessage import NexmoMessage
from django.http import HttpResponse, HttpResponseBadRequest
from .forms import EnvayaSMSIncomingForm
import pprint
import json
import logging

class NexmoOutgoingBackend(BackendBase):
    '''
    This is a Nexmo-based backend for RapidSMS which handles the delivery of messages.
    It deals only with the outgoing message cycle.
    '''

    logger = logging.getLogger('envaya_nexmo.backend.NexmoOutgoingBackend')

    def configure(self, api_key=None, api_secret=None, sender_name='myNexmo', **kwargs):
        if api_key is None or api_secret is None:
            self.logger.exception("Nexmo's API Key or API Secret not supplied!")
            raise ImplementationError("Cannot work without Nexmo API key and API secret")
        else:
            self.api_key = api_key
            self.api_secret = api_secret
            self.sender_name = sender_name

        '''Handles specific configuration for this Backend'''
        super(NexmoOutgoingBackend, self).configure(**kwargs)

    def send_via_nexmo(self, to, message):
        '''
        This is where we use the libnexmo to construct and send a message via Nexmo API
        '''
        params = {
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'type': 'text',
            'from': self.sender_name,
            'to': to,
            'text': message.encode('utf-8'),
        }

        sms = NexmoMessage(params)
        response = sms.send_request()
        self.logger.debug("Nexmo response: %s" % response)
        return response

    #TODO: We need a way to somehow understand and make available the response sent by Nexmo API
    #Currently the response variable given by __send_via_nexmo is in no way available to the sending app,
    #because of the way routing works in RapidSMS (routers just tell whether or not message was sent to the backend for delivery)

    def send(self, id_, text, identities, context = {}):
        '''
        This handles the actual part of outgoing message cycle.
        This method is what is called by the router from RapidSMS
        '''
        self.logger.debug("id is %s" % id_)
        self.logger.debug("text is %s" % text)
        self.logger.debug("identities is %s" % type(identities))
        self.logger.debug("context is %s " % context)

        for i in identities:
            self.logger.debug("SMSing '%s' to '%s' via nexmo" % (text, i))
            self.logger.info("Sending SMS via Nexmo")
            self.send_via_nexmo(i, text)

    @property
    def model(self):
        """
        The model attribute is the RapidSMS model instance with this
        backend name. A new backend will automatically be created if
        one doesn't exist upon accessing this attribute.
        """
        from rapidsms.models import Backend
        backend, _ = Backend.objects.get_or_create(name=self.name)
        return backend

class EnvayaSMSIncomingBackend(GenericHttpBackendView):
    '''
    This is an EnvayaSMS-based backend for RapidSMS which handles the receipt of messages.
    It handles only the incoming message cycle.

    It is actually an HTTP Backend for the EnvayaSMS Android App (http://sms.envaya.org)
    '''

    logger = logging.getLogger('envaya_nexmo.backend.EnvayaSMSIncomingBackend')

    params = {
            #ref: http://sms.envaya.org/serverapi/

            #our name               : name passed by the envaya phone

            'identity_name'         : 'from',         #who sent the message?
            'text_name'             : 'message',      #what was the message?
#            'envaya_phone_number'   : 'phone_number', #which envaya phone forwarded us the msg?
#            'envaya_phone_log'      : 'log',          #any message log fwded by the envaya phone
#            'envaya_phone_connection': 'network',     #how is the envaya phone connected to our server?
#            'envaya_phone_version'  : 'version',      #version of the envaya software installed
#            'envaya_phone_now'      : 'now',          #the value of now (unix epoch) on the phone
#            'envaya_phone_power'    : 'power',        #The current power source of the Android phone
#            'envaya_phone_battery'  : 'battery',      #What is the source of the battery?
            }

    form_class =  EnvayaSMSIncomingForm

    def form_valid(self, form):
        """
        If the form validated successfully, passes the message on to the
        router for processing.
        """
        data = form.get_incoming_data()
        self.logger.debug("data that we got is %s" % data)

        if data['action'] == 'incoming':
            receive(text = data['text'], connection = data['connection'])
            self.logger.info("Incoming message forwarded to router successfully!")

        elif data['action'] == 'outgoing':
            self.logger.info("No outgoing message to forward to EnvayaSMS Android app!")

        return HttpResponse(json.dumps({'events': data['events']}), content_type='application/json')

    def form_invalid(self, form):
        """
        If the form failed to validate, logs the errors and returns a bad
        response to the client.
        """

        self.logger.error("%s data:" % self.request.method)
        self.logger.error(pprint.pformat(form.data))
        errors = dict((k, v[0]) for k, v in form.errors.items())
        self.logger.error(unicode(errors))
        if form.non_field_errors():
            self.logger.error(form.non_field_errors())
        return HttpResponseBadRequest('form failed to validate')
