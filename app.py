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
    username = request.cookies.get('username', 'Guest')
    uid = request.cookies.get('uid', 1)
    return render_template('main.html', username=username, uid = uid, 
                           page_title = 'home page')

@app.route('/setcookie')
def set_cookie():
    response = make_response("Cookie is set")
    response.set_cookie('username', 'Guest')  # Replace with your username
    response.set_cookie('uid', 1)
    return response

import datetime

@app.route('/recipeform/', methods = ['GET','POST'])
def recipeform():
    if request.method == 'GET':
        return render_template('recipeform.html')
    
    if request.method == 'POST':
         # Get basic form data
        title = request.form.get('title')
        prep_time = int(request.form.get('prep-time', 0))
        cook_time = int(request.form.get('cook-time', 0))
        total_time = prep_time + cook_time
        price = request.form.get('price')
        size = request.form.get('size')
        tags = request.form.getlist('tags')
        description = request.form.get('description')
        steps = request.form.get('steps')

        # Get the current date and time
        now = datetime.now()
        # Format it into 'month-day-year'
        date = now.strftime("%m-%d-%Y")

         # Collect ingredients
        ingredients = []
        index = 0
        while True:
            # Dynamically access each row of ingredients
            quantity = request.form.get(f'ingredients[{index}][quantity]')
            measurement = request.form.get(f'ingredients[{index}][measurement]')
            name = request.form.get(f'ingredients[{index}][name]')
            if not name:  # Stop when no more ingredient names are provided
                break
            ingredients.append({
                'quantity': quantity,
                'measurement': measurement,
                'name': name
            })
            index += 1
    
            return render_template('recipepost.html', title=title, date=date, 
                           prep_time=prep_time, cook_time=cook_time, 
                           total_time=total_time, price=price, size=size, 
                           tags=tags, description=description, 
                           steps=steps, ingredients=ingredients)

# recipe post
@app.route('/recipepost/<post_id>', methods = ['GET'])
def recipepost(post_id):
    if request.method == 'GET':
        return render_template('recipepost.html')
    
@app.route('/select/<string:filter>/<string:specific_tag> ', methods=['GET', 'POST'])
def select():
    conn1 = dbi.connect()
    curs = dbi.dict_cursor(conn1)
    if request.method == 'POST':
        selected_filter = request.form.get('filter-type')
        selected_value = None

        if selected_filter == "season":
            selected_value = request.form.get('season')
            return redirect(url_for('main.html'))
        
        elif selected_filter == "course":
            selected_value = request.form.get('course')
            
        elif selected_filter == "dietary":
            selected_value = request.form.get('dietary')
            
        elif selected_filter == "convenience":
            selected_value = request.form.get('convenience')


        

# TO DO: update recipe form with form filled out. make new html page for update recipe form
# route here
#@app.route('/updatepost/<post_id',methods = ['GET','POST'])

# TO DO: discover board --> GET render discover board page html, POST search 
# route here
        
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
            select p.pid, p.cover_photo, p.text_descrip, p.tags, p.price
            from post as p
            where p.title like %s or p.tags like %s or p.price like %s
        """
        search_pattern = f"%{search_term}%"
        curs.execute(query, (search_pattern, search_pattern, search_pattern))
    else:
        # Get all posts
        curs.execute("select p.pid, p.cover_photo, p.text_descrip, p.tags, p.price from post p")

    posts = curs.fetchall()

    # Optionally, add pagination here if necessary
    conn.close()

    return render_template('discover.html', posts=posts)

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
