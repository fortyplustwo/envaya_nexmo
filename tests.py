from django.test import TestCase

class NexmoOutgoingBackendTest(TestCase):

    def test_sending_sms(self):
        """
        Tests that SMS-es are actually sent using the Nexmo outgoing backend.
        """
        try:
            from django.conf import settings
        except ImportError:
            self.fail(msg="No TEST_NUMBER found in settings!")

        from rapidsms.router import send
        from rapidsms.models import Connection, Backend
        from random import randint

        b = Backend.objects.get_or_create(name='envaya_nexmo')[0]
        c = Connection.objects.get_or_create(identity = settings.TEST_NUMBER, backend = b)[0]
        msg = "Hey, this is a test message from NexmoOutgoingBackendTest! \n Your Lucky number is %s" % (randint(1,42))

        send(msg,[c])
        print "Cannot actually verify whether the message was sent or not because of the limitations of rapdisms framework :-/"
