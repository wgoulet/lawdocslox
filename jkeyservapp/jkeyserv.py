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
        self.iv = "test"
        self.secret = "1234"
        self.keysize = 32

    def getkey(self,bid,cid):
        bfirmid = base64.b64encode(bid)
        bclientid = base64.b64encode(cid)
        iv = "test"
        secret = "1234"
        keysize = 32



        d = SHA256Digest()
        d.update(bfirmid,0,len(bfirmid))
        d.update(bclientid,0,len(bclientid))

        # Since BouncyCastle expects to dump output to a writeable
        # byte array, we have to create a PyArray object to store
        # output from the SHA256Digest object
        dval = zeros(d.getDigestSize(),'b')
        d.doFinal(dval,0)
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
    kval = k.getkey("walter","jen")
    #print  base64.b64encode(bytearray(kval))
    print type(kval)
    print  base64.b64encode(kval)
    Pyro4.config.LOGWIRE = True
    Pyro4.Daemon.serveSimple(
        {
            k: "keyobjfactory"
        },
        ns = False)

if __name__=="__main__":
    main()
