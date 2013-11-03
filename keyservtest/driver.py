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
from Crypto.Cipher import AES
from Crypto import Random

def chunkfile(filename,blocksize=16):
    print "Chunking file %s" % filename
    with open(filename,"rb") as f:
        while True:
            chunk = f.read(blocksize)
            if chunk:
                yield chunk
            else:
                break

infile = sys.argv[1]
outfile = sys.argv[2]
bfirmid = base64.b64encode("i love jen")
bclientid = base64.b64encode("12345")

r = requests.get("http://ubuntu:8084/keyserv/key/%s/%s" % (bfirmid,bclientid))
keyobj = r.json()
encrkey = keyobj['key']
print "Got key %s" % encrkey
# Carve out a 32byte/256 bit key from the keyserver
# but convert base64 back to binary first
bkey = binascii.a2b_base64(encrkey)
key = bkey[0:32]
#key = b'Sixteen byte key'
try:
	print "Starting encryption"
	# Setup our AES cipher
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(key,AES.MODE_CFB,iv)
	#cipher = XORCipher.new(key)        
	print "Cipher created"
except:
	raise

print "File ready: %s" % outfile
f = open(outfile,"wb")
for chunk in chunkfile(infile):
	#print chunk
	#t = cipher.encrypt(chunk)
            #print binascii.a2b_base64(cipher.encrypt(chunk))
       f.write(cipher.encrypt(chunk))
            #f.write(chunk)

f.flush()
f.close()



