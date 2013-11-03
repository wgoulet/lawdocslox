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
from flask import Flask,render_template,request,redirect,url_for
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_object(__name__)
UPLOAD_FOLDER = '/var/www/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def showHello():
    # connect to test URL on tested app and show result
    print "about to connect"
    r = requests.get("http://ubuntu:8084/keyserv/ragnar") 
    print r.status_code
    if r.status_code != 200:
        return "Error; REST service unreachable"
    else:
        obj = r.json()
        return render_template('showTest.html',lastName=obj['lastName'],
            firstName=obj['firstName'])

@app.route('/uploadfiles')
def uploadFiles():
    return render_template('fileupload.html')

@app.route('/encrypt',methods=['POST'])
def encryptfile():
    if request.method == 'POST':
        infile = request.form.get('filename')
        bfirmid = request.form.get('bfirmid')
        bclientid = request.form.get('bclientid')
        path = os.path.join(app.config['UPLOAD_FOLDER'],infile)
        # Get an encryption key from the key server
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
            cipher = AES.new(key,AES.MODE_CTR,iv)        
            #cipher = XORCipher.new(key)        
            print "Cipher created"
        except:
            raise

        # Open file in staging area, encrypt it and save it to disk with
        # different filename
        encrfilename = "%s_encr" % infile
        epath = os.path.join(app.config['UPLOAD_FOLDER'],encrfilename)
        print "File ready: %s" % epath
        f = open(epath,"wb")
        for chunk in chunkfile(path):
            print chunk
            t = cipher.encrypt(chunk)
            #print binascii.a2b_base64(cipher.encrypt(chunk))
            #f.write(cipher.encrypt(chunk))
            #f.write(chunk)

        f.flush()
        f.close()
        return render_template('showencrypt.html',filename=encrfilename,key=encrkey)
        
        
         
def chunkfile(filename,blocksize=16):
    print "Chunking file %s" % filename
    with open(filename,"rb") as f:
        while True:
            chunk = f.read(blocksize)
            if chunk:
                yield chunk
            else:
                break
                



@app.route('/viewfiles',methods=['POST'])
def showFiles():
    print request.method
    if request.method == 'POST':
        infile = request.files['infile']
        print "Saving file %s" % infile.filename
        fname = secure_filename(infile.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'],fname)
        infile.save(path)
        firmid = request.form.get('firmid')
        clientid = request.form.get('clientid')
        print "Got firm %s and client %s" % (firmid,clientid)
        bfirmid = base64.b64encode(firmid)
        bclientid = base64.b64encode(clientid)
        print "Got bfirm %s and bclient %s" % (bfirmid,bclientid)
        return render_template('saveresult.html',filename=fname,bfirmid=bfirmid, \
            bclientid=bclientid)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8008)
