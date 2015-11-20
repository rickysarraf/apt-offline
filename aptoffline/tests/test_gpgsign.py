import unittest
from aptoffline.verifysig import VerifySignature
from aptoffline.tests.utils import resource_path


class TestVerifySignature (unittest.TestCase):

    def setUp(self):
        from aptoffline import logger
        logger.initialize_logger(verbose=True)

    def test_validsign(self):
        v = VerifySignature(resource_path(
            'signverify/keyring/debian-archive-jessie-automatic.gpg'))
        self.assertTrue(v.detached_sign_verify(resource_path(
            'signverify/signature.gpg'),
            resource_path('signverify/plain.txt')))

    def test_nonexistent_keyring(self):
        v = VerifySignature(resource_path(
            "signverify/keyring/non-existent.gpg"))
        self.assertFalse(v.detached_sign_verify(resource_path(
            'signverify/signature.gpg'), resource_path(
            'signverify/plain.txt')))

    def test_nonexistent_file(self):
        v = VerifySignature()
        self.assertFalse(v.detached_sign_verify(resource_path(
            'non-existent.txt'), resource_path('signverify/plain.txt')))
        self.assertFalse(v.detached_sign_verify(resource_path(
            'signverify/signature.gpg'), resource_path(
                'signverify/non-existent')))
