import unittest
import os
from aptoffline import verifysig


class TestVerifySignature (unittest.TestCase):
        
    def test_detached_sign_verify(self):
        test_file_path = os.path.dirname(__file__)
        v = verifysig.VerifySignature(os.path.join(
            test_file_path,
            'resources/signverify/keyring/debian-archive-jessie-automatic.gpg'))
        self.assertTrue(v.detached_sign_verify(os.path.join(test_file_path,
                                                            'resources/signverify/signature.gpg'),
                                               os.path.join(test_file_path,
                                                            'resources/signverify/plain.txt'))) 
