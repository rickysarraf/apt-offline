import gnupg
import os

class VerifySignature :
    default_path = ['/etc/apt/trusted.gpg.d', '/usr/share/keyring']

    def __init__(self, keyring=None):
        keyring_files = []
        if not keyring:
            for path in self.default_path:
                if os.path.exists(path):
                    for key in os.listdir(path):
                        # Add verbose logging
                        keyring_files.append(os.path.join(path, key))
        else:
            keyring_files = keyring

        self.gpg = gnupg.GPG(keyring=keyring_files,
                             options='--ignore-time-conflict')

    def is_valid(self, verified_data):
        if verified_data.username and not verified_data.key_status:
            return True
        return False
    
    def detached_sign_verify (self,  signature_file, signed_file):
        if not os.access(signature_file, os.F_OK):
            #log.err("{} is bad. Can't proceed".format(sign_file))
            return False
        if not os.access(signed_file, os.F_OK):
            #log.err("{} is bad. Can't proceed.".format(signed_file))
            return False

        with open(signature_file,"rb") as sfp:
            verified = self.gpg.verify_file(sfp, signed_file)
            if self.is_valid(verified):
                # TODO: log verification information
                return True

        return False
