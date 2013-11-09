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
import ConfigParser
from tempfile import TemporaryFile
from dropbox.client import DropboxClient,DropboxOAuth2Flow
from Crypto.Cipher import AES
from Crypto import Random
from flask import Flask,render_template,request,redirect,url_for,send_from_directory,session,g,Response
from werkzeug import secure_filename

app = Flask(__name__)
config = ConfigParser.ConfigParser()
config.read('./ldl.cfg')
app.config['CFG_FILE'] = './ldl.cfg'
app.config['UPLOAD_FOLDER'] = config.get('Environment','upload_folder')
app.config['APP_KEY'] = config.get('Credentials','dropbox_app_key')
app.config['APP_SECRET'] = config.get('Credentials','dropbox_app_secret')
app.config['SECRET_KEY'] ='testing'


@app.route('/test')
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

@app.route('/')
def linkDropbox():
    print  "Got to /"
    if 'user' not in session:
        print 'redirecting'
        return redirect('/dropboxlogin')
    print "getting access token"
    try:
        access_token = config.get('Credentials','access_token')
        print "got access token"
        return render_template('index.html',needlink='false')
    except:
        return render_template('index.html',needlink='true')

@app.route('/dropboxlogin',methods=['GET', 'POST'])
def dropboxLogin():
    error = None
    print request.method
    if request.method == 'POST':
        username = request.form['username']
        print request.form
        if username:
            print "About to set username %s" % username
            session['user'] = username
            print "Set username %s" % username
            config.set('Credentials','user',username)
            print "Saved username %s to config" % username
            with open(app.config['CFG_FILE'],"wb") as cfg:
                config.write(cfg)
            return redirect('/')
        else:
            print ('You must provide a username!')
    print 'rendering template'
    return render_template('login.html')

@app.route('/dropbox-auth-start')
def dropboxAuthStart():
    print session
    if 'user' not in session:
        abort(403)
    print "redirecting user to get auth flow"
    return redirect(getAuthFlow().start())

def getAuthFlow():
    print "starting auth flow"
    redirect_uri = 'http://localhost:8008/dropbox-auth-finish'#url_for('dropbox_auth_finish',_external=True)
    print redirect_uri
    try:
        flow = DropboxOAuth2Flow(app.config['APP_KEY'],app.config['APP_SECRET'],
            redirect_uri,session,'dropbox-auth-csrf-token')
        print flow
        return flow
    except Exception as e:
        print e
        raise

@app.route('/dropbox-auth-finish')
def dropboxAuthFinish():
    username = session.get('user')
    if username is None:
        abort(403)
    try:
        access_token, user_id, url_state = getAuthFlow().finish(request.args)
    except DropboxOAuth2Flow.BadRequestException, e:
        abort(400)
    except DropboxOAuth2Flow.BadStateException, e:
        abort(400)
    except DropboxOAuth2Flow.CsrfException, e:
        abort(403)
    except DropboxOAuth2Flow.NotApprovedException, e:
        print('Not approved?  Why not, bro?')
        return redirect('/')
    except DropboxOAuth2Flow.ProviderException, e:
        app.logger.exception("Auth error" + e)
        abort(403)
    config.set('Credentials','access_token',access_token)
    with open(app.config['CFG_FILE'],"wb") as cfg:
        config.write(cfg)
    return redirect('/uploadfiles')
    
@app.route('/uploadfiles')
def uploadFiles():
    return render_template('fileupload.html')

@app.route('/encrypt',methods=['POST'])
def encryptfile():
    if request.method == 'POST':
        infile = request.files['infile']
        bfirmid = base64.b64encode(request.form.get('firmid'))
        bclientid = base64.b64encode(request.form.get('clientid'))
        result = savefile(infile,infile.filename,bfirmid,bclientid)
        return render_template('showencrypt.html',filename=result['path'],key="not available", \
             bclientid=bclientid,bfirmid=bfirmid)

        
def savefile(fd,fname,bfirmid,bclientid):
    # Encrypt each chunk from fd as it is read into a 
    # tmpfile which will be uploaded to Dropbox using
    # the given filename. 
    r = requests.get("http://ubuntu:8084/keyserv/key/%s/%s" % (bfirmid,bclientid))
    print "http://ubuntu:8084/keyserv/key/%s/%s" % (bfirmid,bclientid)
    keyobj = r.json()
    encrkey = keyobj['key']
    print "Got key %s" % encrkey
    # Carve out a 32byte/256 bit key from the keyserver
    # but convert base64 back to binary first
    bkey = binascii.a2b_base64(encrkey)
    key = bkey[0:32]

    try:
        print "Starting encryption"
        # Setup our AES cipher
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key,AES.MODE_CFB,iv)        
        #cipher = XORCipher.new(key)        
        print "Cipher created using iv %s" % binascii.hexlify(iv)
    except:
        raise

    try:
        f = TemporaryFile()
        f.write(iv)         
   
        for chunk in chunkfd(fd,blocksize=4194304):
            f.write(cipher.encrypt(chunk))

        f.flush()
        f.seek(0,os.SEEK_END)
        fsize = f.tell()
        f.seek(0)

    except Exception as e:
        print e

    print "Getting ready for Dropbox upload"
    # Get a Dropbox uploader
    try:
        access_token = config.get('Credentials','access_token')
        dclient = DropboxClient(access_token)
        uploader = dclient.get_chunked_uploader(f,fsize)

        while uploader.offset < fsize:
            try:
                upload = uploader.upload_chunked()
            except Exception as e:
                print e
    except Exception as e:
        print e
    
    f.close()
    
    return uploader.finish(secure_filename("/%s_encr" % fname))    

@app.route("/decrypt",methods=['POST'])
def decryptfile():        
    print "Decrypting file"
    # To avoid writing plaintext to any files, copy the response
    # data from Dropbox directly into a read/write in memory buffer
    if request.method == 'POST':
        infile = request.form['filename']
        bfirmid = base64.b64encode(request.form.get('firmid'))
        bclientid = base64.b64encode(request.form.get('clientid'))
        try:
            access_token = config.get('Credentials','access_token')
            dclient = DropboxClient(access_token)
            print "Requesting /%s" % infile
            httpresp = dclient.get_file("/%s" % infile)
            instream = io.BytesIO()
            inbuf = io.BufferedRandom(instream)
            inbuf.write(httpresp.read())
            inbuf.flush()
            inbuf.seek(0)
            result = getfile(inbuf,bfirmid,bclientid)
            print "done with getfile"
            
            result.seek(0,os.SEEK_END)
            print "Got %d bytes" % result.tell()
            result.seek(0)
            # Copy the decrypted data into a HTTP response object
            # to be returned to the user
            print "getting ready to return to response object"

            return Response(chunkfd(result,blocksize=4096),
                mimetype='application/octet-stream')
            
        except Exception as e:
            print e

def getfile(fd,bfirmid,bclientid):
    if request.method == 'POST':
        outstream = io.BytesIO()
        outbuf = io.BufferedRandom(outstream) 
        r = requests.get("http://ubuntu:8084/keyserv/key/%s/%s" % (bfirmid,bclientid))
        print "http://ubuntu:8084/keyserv/key/%s/%s" % (bfirmid,bclientid)
        keyobj = r.json()
        encrkey = keyobj['key']
        print "Got key %s" % encrkey
        # Carve out a 32byte/256 bit key from the keyserver
        # but convert base64 back to binary first
        bkey = binascii.a2b_base64(encrkey)
        key = bkey[0:32]

        # Get IV from file
        iv = fd.read(AES.block_size)
         
        print "Creating cipher"
        # Setup our AES cipher
        cipher = AES.new(key,AES.MODE_CFB,iv)        
        print "Cipher created using iv %s" % binascii.hexlify(iv)
        if (fd.closed):
            print "Handle closed"
        else:
            print "Handle open"
        for chunk in chunkfd(fd,ivsize=AES.block_size):
            outbuf.write(cipher.decrypt(chunk))

        outbuf.flush()

        return outbuf            


         
def chunkfd(inbuf,ivsize=16,blocksize=16,skipiv=0):
    if(skipiv):
        inbuf.seek(ivsize)
    while True:
        chunk = inbuf.read(blocksize)
        if chunk:
          yield chunk
        else:
          break

def chunkfile(filename,ivsize=16,blocksize=16,skipiv=0):
    print "Chunking file %s" % filename
    with open(filename,"rb") as f:
        if(skipiv):
            f.seek(ivsize)
        while True:
            chunk = f.read(blocksize)
            if chunk:
                yield chunk
            else:
                break
                



@app.route('/viewfiles',methods=['POST'])
def showFiles():
    if request.method == 'POST':
        try:
            # get a chunked DropBox uploader
            # Get the Dropbox client we stored earlier
            access_token = config.get('Credentials','access_token')
            dclient = DropboxClient(access_token)
            contents = dclient.metadata("/")['contents']
            flist = []
            for i in contents:
                flist.append(i['path'])
            return render_template('viewfiles.html',filelist=flist)
        except Exception as e:
            print e


if __name__ == '__main__':
    app.run(host="localhost",port=8008)
