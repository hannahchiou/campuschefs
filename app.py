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

        
# You will probably not need the routes below, but they are here
# just in case. Please delete them if you are not using them

@app.route('/discover', methods=['GET'])
def discover():
    # Connect to the database
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    # Get search term if any
    search_term = request.args.get('search', '')

    # Create SQL query with filtering if there's a search term
    if search_term:
        query = """
            select p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price
            from post as p
            where p.title like %s or p.tags like %s or p.price like %s
        """
        search_pattern = f"%{search_term}%"
        curs.execute(query, (search_pattern, search_pattern, search_pattern))
    else:
        # Get all posts
        curs.execute("select p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price from post p")

    posts = curs.fetchall()

    # Optionally, add pagination here if necessary
    conn.close()

    return render_template('discover.html', posts=posts)


@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html',
                               page_title='Form to collect username')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   page_title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

# This route displays all the data from the submitted form onto the rendered page
# It's unlikely you will ever need anything like this in your own applications, so
# you should probably delete this handler

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               page_title='Display of Form Data',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               page_title='Display of Form Data',
                               method=request.method,
                               form_data=request.form)
    else:
        raise Exception('this cannot happen')  

# This route shows how to render a page with a form on it.

@app.route('/testform/')
def testform():
    # these forms go to the formecho route
    return render_template('testform.html',
                           page_title='Page with two Forms')



if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'campuschefs_db' 
    print(f'will connect to {db_to_use}')
    dbi.conf(db_to_use)
    app.debug = True
    app.run('0.0.0.0',port)
