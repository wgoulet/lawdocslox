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
from flask import Flask,render_template,request,redirect,url_for,send_from_directory,session,g
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
  #  if(config.get('Credentials','access_token') is not None):
    print "getting access token"
    try:
        access_token = config.get('Credentials','access_token')
        print "got access token"
  #  else:
  #      access_token = 
    #if access_token is not None:
        #client = DropboxClient(access_token)
        #account_info = client.account_info()
        #real_name = account_info["display_name"] 
        #g.set('dclient',client)
        return render_template('index.html',needlink='false')
    except:
        return render_template('index.html',needlink='true')

@app.route('/dropboxlogin',methods=['GET', 'POST'])
def dropboxLogin():
    error = None
    print request.method
    if request.method == 'POST':
        username = request.form['username']
        if username:
            print "About to set username %s" % username
            session['user'] = username
            print "Set username %s" % username
            config.set('Credentials','user',username)
            print "Saved username %s to config" % username
            with open(app.config['CFG_FILE'],"wb") as cfg:
                config.write(cfg)
            #flash('You were logged in')
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
        infile = request.form.get('filename')
        bfirmid = request.form.get('bfirmid')
        bclientid = request.form.get('bclientid')
        path = os.path.join(app.config['upload_folder'],infile)
        # Get an encryption key from the key server
        r = requests.get("http://ubuntu:8084/keyserv/key/%s/%s" % (bfirmid,bclientid))
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

        # Open file in staging area, encrypt it and save it to disk with
        # different filename
        encrfilename = "%s_encr" % infile
        epath = os.path.join(app.config['UPLOAD_FOLDER'],encrfilename)
        print "File ready: %s" % epath
        f = open(epath,"wb")
        f.write(iv)
        for chunk in chunkfile(path):
            #print chunk
            #t = cipher.encrypt(chunk)
            #print binascii.a2b_base64(cipher.encrypt(chunk))
            f.write(cipher.encrypt(chunk))
            #f.write(chunk)

        f.flush()
        f.close()
        return render_template('showencrypt.html',filename=encrfilename,key=encrkey, \
             bclientid=bclientid,bfirmid=bfirmid)
        
@app.route("/decrypt",methods=['POST'])
def decryptfile():        
    print "Decrypting file"
    if request.method == 'POST':
        infile = request.form.get('filename')
        bfirmid = request.form.get('bfirmid')
        bclientid = request.form.get('bclientid')
        path = os.path.join(app.config['UPLOAD_FOLDER'],infile)
        print "Got params %s %s %s" % (infile,bfirmid,bclientid)
        # Get an encryption key from the key server
        r = requests.get("http://ubuntu:8084/keyserv/key/%s/%s" % (bfirmid,bclientid))
        keyobj = r.json()
        encrkey = keyobj['key']
        print "Got decryption key %s" % encrkey
        # Carve out a 32byte/256 bit key from the keyserver
        # but convert base64 back to binary first
        bkey = binascii.a2b_base64(encrkey)
        key = bkey[0:32]

        # Get IV from file
        f = open(path,"rb")
        iv = f.read(AES.block_size)
        f.close()

        try:
            print "Creating cipher"
            # Setup our AES cipher
            cipher = AES.new(key,AES.MODE_CFB,iv)        
            print "Cipher created using iv %s" % binascii.hexlify(iv)
        except:
            raise

        # Open encrypted file in staging area, decrypt it and save it to disk with
        # different filename
        decrfilename = "%s_clear" % infile
        epath = os.path.join(app.config['UPLOAD_FOLDER'],decrfilename)
        print "File ready: %s" % epath
        f = open(epath,"wb")
        for chunk in chunkfile(path,skipchunk=1):
            f.write(cipher.decrypt(chunk))
        
        f.flush()
        f.close()

        return render_template("showfile.html",filename=decrfilename)
        #return "File %s in folder %s" % (decrfilename,app.config['UPLOAD_FOLDER'])


@app.route('/download',methods=['POST'])
def uploaded_file():
    if request.method == 'POST':
        filename = request.form.get('filename')
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
         
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
                



@app.route('/viewfiles',methods=['POST'])
def showFiles():
    print request.method
    if request.method == 'POST':
        
        infile = request.files['infile']
        fd = infile.stream
        #with fd:
        #    print fd.read()
        try:
            fd.seek(0,os.SEEK_END)
            fdsize = fd.tell()
            print "file size is %d" % fdsize
            fd.seek(0)
            # get a chunked DropBox uploader
            # Get the Dropbox client we stored earlier
            access_token = config.get('Credentials','access_token')
            dclient = DropboxClient(access_token)
            uploader = dclient.get_chunked_uploader(fd,fdsize)
            print "Saving file %s to dropbox" % infile.filename
            while uploader.offset < fdsize:
                try:
                    upload = uploader.upload_chunked()
                except Exception as e:
                    print e
            uploader.finish(secure_filename("/%s" % infile))
        except Exception as e:
            print e
        fname = secure_filename(infile.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'],fname)
        #infile.save(path)
        firmid = request.form.get('firmid')
        clientid = request.form.get('clientid')
        print "Got firm %s and client %s" % (firmid,clientid)
        bfirmid = base64.b64encode(firmid)
        bclientid = base64.b64encode(clientid)
        print "Got bfirm %s and bclient %s" % (bfirmid,bclientid)
        return render_template('saveresult.html',filename=fname,bfirmid=bfirmid, \
            bclientid=bclientid)


if __name__ == '__main__':
    app.run(host="localhost",port=8008)
