import unittest
from aptoffline import verifysig
from aptoffline.tests.utils import resource_path


class TestVerifySignature (unittest.TestCase):

    def setUp(self):
        from aptoffline import logger
        logger.initialize_logger(verbose=True)

    def test_detached_sign_verify(self):
        v = verifysig.VerifySignature(resource_path(
            'signverify/keyring/debian-archive-jessie-automatic.gpg'))
        self.assertTrue(v.detached_sign_verify(resource_path(
            'signverify/signature.gpg'),
            resource_path('signverify/plain.txt')))
