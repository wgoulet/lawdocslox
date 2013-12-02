import os
import base64
import binascii
import sys
import io
import zipfile
import tempfile
import requests
import subprocess
import collections
import json
import Pyro4
from Crypto.Cipher import AES
from Crypto import Random

def chunkfile(filename,blocksize=16,skipchunk=0):
    print "Chunking file %s" % filename
    with open(filename,"rb") as f:
        if(skipchunk):
            f.seek(blocksize)
        while True:
            chunk = f.read(blocksize)
            if chunk:
                yield chunk
            else:
                break

infile = sys.argv[1]
outfile = sys.argv[2]
finalfile = sys.argv[3]
iface = sys.argv[4]
bfirmid = base64.b64encode("jen loves")
bclientid = base64.b64encode("walter")

if iface=='pyro':
    kfact = Pyro4.Proxy("PYRONAME:keyobjfactory")
    encrkey = kfact.getkey(bfirmid,bclientid)
    # Jython key generator returns raw bytes so
    # no need to decode it from base64
    bkey = encrkey.encode('raw_unicode_escape')
    print "Got key %s" % base64.b64encode(bkey)
else:
    r = requests.get("http://localhost:8080/keyserv/key/%s/%s" % (bfirmid,bclientid))
    keyobj = r.json()
    encrkey = keyobj['key']
    bkey = binascii.a2b_base64(encrkey)
    print "Got key %s" % base64.b64encode(bkey)

key = bkey[0:32]
#key = b'Sixteen byte key'
try:
	print "Starting encryption"
	# Setup our AES cipher
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(key,AES.MODE_CFB,iv)
	print "Cipher created with iv %s" % binascii.hexlify(iv)
except:
	raise

print "File ready: %s" % outfile
# Basic protocol; we will add IV used for encrypting file to the
# first block of the file
f = open(outfile,"wb")
f.write(iv)
for chunk in chunkfile(infile):
       f.write(cipher.encrypt(chunk))

f.flush()
f.close()

# Since we add the IV as the first block of the encrypted file,
# open the file and read this value first. When we are starting
# our decrypt operation, tell chunkfile to skip past the first
# chunk which contains the IV

f = open(outfile,"rb")
iv = f.read(AES.block_size)
f.close()
print "Got iv %s from file" % binascii.hexlify(iv)
cipher = AES.new(key,AES.MODE_CFB,iv)

f = open(finalfile,"wb")
for chunk in chunkfile(outfile,skipchunk=1):
    f.write(cipher.decrypt(chunk))

f.flush()
f.close()

