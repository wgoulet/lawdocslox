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


bfirmid = base64.b64encode('walter')
bclientid = base64.b64encode('jen')
iv = "test"
secret = "1234"
keysize = 200

print bfirmid
print bclientid


d = SHA256Digest()
d.update(bfirmid,0,len(bfirmid))
d.update(bclientid,0,len(bclientid))

# Since BouncyCastle expects to dump output to a writeable
# byte array, we have to create a PyArray object to store
# output from the SHA256Digest object
dval = zeros(d.getDigestSize(),'b')
d.doFinal(dval,0)
print dval
print binascii.hexlify(dval.tostring())

kg = KDF2BytesGenerator(d)
kp = KDFParameters(iv,secret)
kg.init(kp)
kval = zeros(keysize,'b')
kg.generateBytes(kval,0,len(kval))
print  base64.b64encode(kval.tostring())
