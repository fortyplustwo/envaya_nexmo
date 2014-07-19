from rapidsms.backends.base import BackendBase
from nexmo.libpynexmo.nexmomessage import NexmoMessage
import logging

logger = logging.getLogger('envaya_nexmo.backend.NexmoOutgoingBackend')

class NexmoOutgoingBackend(BackendBase):
    '''
    This is a Nexmo-based backend for RapidSMS which handles the delivery of messages.
    It deals only with outgoing message cycle.
    '''

    def configure(self, api_key=None, api_secret=None, sender_name='myNexmo', **kwargs):
        if api_key is None or api_secret is None:
            logger.exception("Nexmo's API Key or API Secret not supplied!")
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
            'type': 'unicode',
            'from': self.sender_name,
            'to': to,
            'text': message.encode('utf-8'),
        }

        sms = NexmoMessage(params)
        response = sms.send_request()
        logger.debug("Nexmo response: %s" % response)
        return response

    #TODO: We need a way to somehow understand and make available the response sent by Nexmo API
    #Currently the response variable given by __send_via_nexmo is in no way available to the sending app,
    #because of the way routing works in RapidSMS (routers just tell whether or not message was sent to the backend for delivery)

    def send(self, id_, text, identities, context = {}):
        '''
        This handles the actual part of outgoing message cycle.
        '''
        logger.debug("id is %s" % id_)
        logger.debug("text is %s" % text)
        logger.debug("identities is %s" % type(identities))
        logger.debug("context is %s " % context)


        for i in identities:
            logger.debug("SMSing '%s' to '%s' via nexmo" % (text, i))
            logger.info("Sending SMS via Nexmo")
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
