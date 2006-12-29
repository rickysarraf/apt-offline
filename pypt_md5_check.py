import md5, os, array

#INFO: This class isn't being used.
# I think I've found the much simpler way to get my job accomplished
class HMAC_MD5:
    # keyed MD5 message authentication
    # This CLASS code has been taken from http://effbot.org
    # Those people are great. :-)


    def __init__(self, key):
        if len(key) > 64:
            key = md5.new(key).digest()
        ipad = array.array("B", [0x36] * 64)
        opad = array.array("B", [0x5C] * 64)
        for i in range(len(key)):
            ipad[i] = ipad[i] ^ ord(key[i])
            opad[i] = opad[i] ^ ord(key[i])
        self.ipad = md5.md5(ipad.tostring())
        self.opad = md5.md5(opad.tostring())

    def digest(self, data):
        ipad = self.ipad.copy()
        opad = self.opad.copy()
        ipad.update(data)
        opad.update(ipad.digest())
        return opad.digest()
        
        
    
def md5_string(data):
    
    hash = md5.new()
    hash.update(data.read())
    return hash.hexdigest() 
    
def md5_check(file, checksum, path=None):
    #global md5check_bool
    #if pypt_variables.md5check_bool:
    #if pypt_variables.options.disable_md5check == True:
    #    return
    #    print "The argument was passed"
    if path is None:
        path = os.curdir
    os.chdir(path)
    data = open(file, 'rb')
    #local = md5_string(data)
    if checksum == md5_string(data):
        return True