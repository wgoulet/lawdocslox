from org.bouncycastle.crypto.prng import ThreadedSeedGenerator
from org.bouncycastle.crypto.prng import DigestRandomGenerator 
from org.bouncycastle.crypto.digests import SHA256Digest
from org.bouncycastle.crypto.params import KDFParameters
from org.bouncycastle.crypto.generators import KDF2BytesGenerator 
from jarray import array, zeros
import os
import base64
import binascii
import io
import Pyro4



class KeyObjFactory(object):
    def __init__(self):
        self.iv = "461/tOh/0Gw9PKtGSBER0ekashdzDtzNlMpxdNHUip44aNYfL8EdpjMEj/VZAgp+ss0l/vrh8FNyjR50J53UeamPJTYl7jqH1Ydr7w70vpuuwBMEHNQAthEvzWx1gtjASPnkZalWEgp3QC0MeuCMqqL67bAMHbNWBhq1r8DE9yvvUM013UoRSjR1sEaZu7HDN1VcdnFDiUIvbNY4R70lFvv/btg8VLUsus665dcq2bkC7VHFWPICpAs4y0CLpgZtwN6LdZcJNgY="
        self.secret = "i love jen!!"
        self.keysize = 32

    def getkey(self,bid,cid):
        iv = "test"
        secret = "1234"
        keysize = 32



        d = SHA256Digest()
        d.update(bid,0,len(bid))
        d.update(cid,0,len(cid))
        d.finish()
        #print binascii.hexlify(dval.tostring())

        kg = KDF2BytesGenerator(d)
        kp = KDFParameters(iv,secret)
        kg.init(kp)
        kval = zeros(keysize,'b')
        kg.generateBytes(kval,0,len(kval))
        #print binascii.hexlify(kval.tostring())
        print binascii.hexlify(kval.tostring())
        print  base64.b64encode(kval.tostring())
        return kval.tostring()


def main():
    k = KeyObjFactory()
    #kval = k.getkey(base64.b64encode("walter"),base64.b64encode("jen"))
    #print  base64.b64encode(bytearray(kval))
    #print type(kval)
    #print  base64.b64encode(kval)
    Pyro4.config.LOGWIRE = True
    Pyro4.Daemon.serveSimple(
        {
            k: "keyobjfactory"
        },
        ns = True)

if __name__=="__main__":
    main()
