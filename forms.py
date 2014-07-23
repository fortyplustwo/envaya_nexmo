from django import forms
from rapidsms.backends.http.forms import BaseHttpForm
import logging

logger = logging.getLogger('envaya_nexmo.forms.EnvayaSMSIncomingForm')

class EnvayaSMSIncomingForm(BaseHttpForm):
    '''handles validation and cleaning up of incoming message'''

    def __init__(self, *args, **kwargs):
        """
        Saves the identify (phone number) and text field names on self, calls
        super(), and then adds the required fields.
        """
        # defaults to "text" and "identity"
   
        self.text_name = kwargs.pop('text_name', 'text')
        self.identity_name = kwargs.pop('identity_name', 'identity')
         
        super(EnvayaSMSIncomingForm, self).__init__(*args, **kwargs)
        
        #The following two fields are non-mandatory because actions other than 'incoming' won't have them.
        self.fields[self.text_name] = forms.CharField(required=False)
        self.fields[self.identity_name] = forms.CharField(required=False)

        self.fields['phone_number'] = forms.CharField() #which envaya phone forwarded us the msg?
        self.fields['action'] = forms.CharField() #what is the action?

    def get_incoming_data(self):
        """
        Returns the connection and text for this message, based on the field
        names passed to __init__().
        """

        fields = self.cleaned_data.copy()
        action = self.cleaned_data['action']
        
        logger.debug("Fields that we got are %s" % fields)

        return_data = {}

        #determine our further PoA based on the action varible passed by envaya phone
        return_data['action'] = action
        return_data['events'] = {}

        if action == 'incoming':
            logger.info("We have an incoming message!")

            return_data['text']        = self.cleaned_data[self.text_name]
            return_data['connection']  = self.lookup_connections([self.cleaned_data[self.identity_name]])[0]
            return_data['from_phone']  = self.cleaned_data['phone_number']

        elif action == 'outgoing':

            logger.info("Received a poll for outgoing message!")
            return_data['events'] = [{'event': 'log', 'message': "We do not deliver outgoing messages via EnvayaSMS Android app!"}]

        elif action == 'test':
            logger.info("Received a test connection request!")
            return_data['events'] = [{'event': 'log', 'message': "Alpha to Charlie: This software by FortyPlusTwo-Hewe rocks! :)"}]

        elif action == 'send_status':
            logger.error("NOT IMPLEMENTED: send_status action")

        elif action == 'device_status':
            logger.error("NOT IMPLEMENTED: device_status action")

        elif action == 'forward_sent':
            logger.error("NOT IMPLEMENTED: forward_status action")

        elif action == 'amqp_started':
            logger.error("NOT IMPLEMENTED: amqp_status action")

        else:
            logger.exception("UNSUPPORTED ACTION %s requested by EnvayaSMS Android app" % action)
            raise NotImplementedError("Action %s not implemented!" % action)

        return return_data
