from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import secrets

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html', # put in html for home page
                           page_title='Main Page')

import datetime

@app.route('/recipeform/', methods = ['GET','POST'])
def recipeform():
    if request.method == 'GET':
        return render_template('recipeform.html')
    if request.method == 'POST':
        # TO DO: Flash message if a required field is missing 
        time =  datetime.now()

# recipe post
# update recipe form with form filled out. make new html page for update recipe form
# discover board --> GET render discover board page html, POST search 

        

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    # set this local variable to 'wmdb' or your personal or team db
    #db_to_use = cs304dbi 
   # print(f'will connect to {db_to_use}')
    #dbi.conf(db_to_use)
    app.debug = True
    app.run('0.0.0.0',port)
