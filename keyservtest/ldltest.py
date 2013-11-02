import os
import sys
import io
import zipfile
import tempfile
import requests
import subprocess
import collections
import json
from flask import Flask,render_template,request,redirect,url_for
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_object(__name__)


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
        #return "Lastname: %s Firsname %s" % (obj['lastName'],obj['firstName'])
        return render_template('showTest.html',lastName=obj['lastName'],
            firstName=obj['firstName'])
    #return "hello world"


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8008)
