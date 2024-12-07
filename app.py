from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
from PIL import Image
import bcrypt
import os
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi
import datetime
import helper

import secrets

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    ''''
    Our homepage. This page will eventually get the cookie information from 
    our users (just 'Guest' right now for draft purposes)
    '''
    
    username = request.cookies.get('username', 'Guest')
    uid = request.cookies.get('uid', 1)
    return render_template('main.html', username=username, uid = uid, 
                           page_title = 'home page')

@app.route('/setcookie')
def set_cookie():
    '''
    Sets cookie with username and uid information. Will be expanded
    on in future versions
    '''
    username = 'Guest User' 
    uid = 1  

    # Set the cookies with username and uid
    response = make_response("Cookies have been set!")
    response.set_cookie('username', username)
    response.set_cookie('uid', str(uid))  

    return response

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    '''
    Checks that the file is a png, jpg, jpeg, or gif, so it 
    can be properly rendered on our html page.
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# route creating an account
@app.route('/register/', methods = ['GET','POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')  # Show the register  page
    conn = dbi.connect()
    name = request.form.get('name')
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    if password1 != password2:
        flash('Please enter matching passwords.')
        return redirect( url_for('register'))
    
    # Hash the password
    hashed = bcrypt.hashpw(password1.encode('utf-8'),
                          bcrypt.gensalt())
    stored = hashed.decode('utf-8')

    # Call the helper function to insert the new user
    result = helper.insertUser(conn, username, stored, name)

    if result["success"]:
        flash(result["message"])
        return redirect(url_for('login'))
    else:
        flash(result["message"])
        return redirect(url_for('register'))

#route for logging in
@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')  # Show the login page
    
    username = request.form.get('username')
    password = request.form.get('password')
    conn = dbi.connect()
    result = helper.getUser(conn, username)
    if result is None:
        flash('Login incorrect, please try again or register.')
        return redirect(url_for('login'))
    storedPass = result['password']
    # encode and decode passwords to check if they match
    hashed = bcrypt.hashpw(password.encode('utf-8'), storedPass.encode('utf-8'))
    hashed_string = hashed.decode('utf-8')
    if hashed_string == storedPass:
    # is this %s necessary; probably not
        flash('Successfully logged in as %s' % username)
        session['username'] = username
        session['uid'] = result['uid']
        session['logged_in'] = True
        print(f"Your username is: {session['username']}, and your UID is: {session['uid']}, and your login status is: {session['logged_in']}")
        # session['visits'] = 1
        return redirect(url_for('index'))
    else: 
        flash('Login incorrect. Please try again or register')
        return redirect(url_for('index'))
    
@app.route('/logout/')
def logout():
    print(f"Your username is: {session['username']}, and your UID is: {session['uid']}, and your login status is: {session['logged_in']}")
    if 'username' in session:
        username = session['username']
        session.pop('username')
        session.pop('uid')
        session.pop('logged_in')
        flash('You have been successfully logged out')
        return redirect(url_for('index'))
    else: 
        flash('You are not logged in. Please login or register')
        return redirect(url_for('index'))
    
@app.route('/recipeform/', methods = ['GET','POST'])
def recipeform():
    '''
    For GET: assumes that this is the first time a user is posting their recipe.
    Displays our recipe form HTM (see templates folder) for them to fill out 

    For POST: collects the form information, inserts it into our SQL database,
    and displays it as a recipe post. Redirects users to the recipe post once it 
    is successfully inserted. 
    '''
    conn = dbi.connect()

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
        # Convert tags to a comma separated string for SET
        if isinstance(tags, list):
            tags = ','.join(tags)
        description = request.form.get('description')
        steps = request.form.get('steps')
        
        # format into datetime format for inserting into database
        post_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


        # Uploading our image and saving the photo url to be inserted 
        # on the HTML page
        file = request.files.get('cover-photo')
        photo_url = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            photo_url = url_for('static', filename=f'uploads/{filename}')

        # Inserts the recipe if it is valid; gets the post id to render the post
        # in post form 
        last_insert = helper.insertRecipe(conn, 
                            uid = request.cookies.get('uid'), 
                            post_date = post_date,
                            title = title,
                            cover_photo = photo_url,
                            serving_size = size,
                            prep_time = prep_time,
                            cook_time = cook_time,
                            total_time = total_time,
                            text_descrip = description,
                            steps = steps,
                            tags = tags,
                            price = price)
            
         # Collect ingredients
        index = 0
        while True:
            # Dynamically access each row of ingredients
            quantity = request.form.get(f'ingredients[{index}][quantity]')
            measurement = request.form.get(f'ingredients[{index}][measurement]')
            name = request.form.get(f'ingredients[{index}][name]')
            if not name:  # Stop when no more ingredient names are provided
                break
            helper.insertIngredients(conn, 
                                pid = last_insert,
                                name = name,
                                quantity = quantity,
                                measurement = measurement)
            index += 1
        
        # Redirect to recipe/post_id
        flash('Your recipe has been successfully inserted into CampusChefs!')
        return redirect(url_for('recipepost', post_id = last_insert))
    
@app.route('/recipepost/<post_id>', methods = ['GET','POST'])
def recipepost(post_id):
    '''
    For GET: displays the post information, if the post id is valid.

    For POST: a user can either update or delete their post. If DELETE
    is chosen, the post is deleted and a message is flashed. If UPDATE
    is chosen, the user is redirected to the update page. 
    '''
    conn = dbi.connect()

    if request.method == 'GET':
        post = helper.getPost(conn, post_id)
        ingredients = helper.getIngredients(conn, post_id)
        print(ingredients)

        if not post: 
            flash('''The recipe you requested is not in the database.
                  Please reenter the information.''')
            return redirect(url_for('index'))

        photo_url = post['cover_photo']
        if isinstance(photo_url, bytes):
            photo_url = photo_url.decode('utf-8')

        return render_template('recipepost.html',
                               username=request.cookies.get('username', 'Guest'), 
                               title = post['title'],
                               date = post['post_date'],
                               prep_time = post['prep_time'],
                               cook_time = post['cook_time'],
                               total_time = post['total_time'],
                               price = post['price'], size = post['serving_size'],
                               tags = post['tags'], 
                               description = post['text_descrip'], 
                               steps = post['steps'].split('\n'),
                               ingredients = ingredients,
                               photo_url = photo_url)
    
    if request.method == 'POST':
        response = request.form.get('submit')
        # check what the button chosen is
        if response == "update":
            return redirect(url_for('updatepost',post_id = post_id))

        if response == "delete":
            helper.deletePost(conn,post_id)
            flash('Your post has been successfully deleted.')
            return redirect(url_for('index'))

@app.route('/updatepost/<post_id>',methods = ['GET','POST'])
def updatepost(post_id):
    '''
    For GET: displays a form similar to the original recipe form post,
    but some of the fields are autopopulated with the previous information,
    similar to CRUD.

    For POST: updates the recipe and ingredient information in the backend 
    and redirects the user to the recipe post with the new information.
    '''
    conn = dbi.connect()
    if request.method == 'GET':
        # Autopopulate update form with previous info, similar to CRUD
        recipe = helper.getPost(conn,post_id)
        ingredients = helper.getIngredients(conn,post_id)
        print('this post id is' + post_id)
        id = post_id 
        print(id)

        return render_template('updatepost.html',
                               post_id = id,
                               title=recipe['title'],
                               cover_photo=recipe['cover_photo'],
                               prep_time=recipe['prep_time'],
                               cook_time=recipe['cook_time'],
                               ingredients=ingredients,
                               steps=recipe['steps'],
                               description=recipe['text_descrip'])
    
    if request.method == 'POST':
         # Get basic form data
        title = request.form.get('title')
        prep_time = int(request.form.get('prep-time', 0))
        cook_time = int(request.form.get('cook-time', 0))
        total_time = prep_time + cook_time
        price = request.form.get('price')
        size = request.form.get('size')
        tags = request.form.getlist('tags')
        # convert tags to a comma separated string for SET
        if isinstance(tags, list):
            tags = ','.join(tags)
        description = request.form.get('description')
        steps = request.form.get('steps')

        file = request.files.get('cover-photo')
        photo_url = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            photo_url = url_for('static', filename=f'uploads/{filename}')

        # update the recipes
        helper.updateRecipe(conn,post_id,title,photo_url,size,
                            prep_time,cook_time,total_time,
                            description,steps,tags,price)
        
        # updates ingredients by deleting all ingredients and inserting 
        # the ingredients entered in the update form
        helper.deleteIngredients(conn,post_id)
        index = 0
        while True:
            # Dynamically access each row of ingredients
            quantity = request.form.get(f'ingredients[{index}][quantity]')
            measurement = request.form.get(f'ingredients[{index}][measurement]')
            name = request.form.get(f'ingredients[{index}][name]')
            if not name:  # Stop when no more ingredient names are provided
                break
            helper.insertIngredients(conn, 
                                pid = post_id,
                                name = name,
                                quantity = quantity,
                                measurement = measurement)
            index += 1

        flash('Your recipe has been successfully updated.')
        return redirect(url_for('recipepost', post_id=post_id))


# Discover board --> GET render discover board page html, POST search    
# this route uses a helper function to retrieve all posts in the database. This function also handles 
# when users use the search bar and then uses another function to retrieve all post with the search key in the title
# It also handles when users choose to filter the posts by tags and redirects the user to the select route. 
@app.route('/discover', methods=['GET','POST'])
def discover():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    # Retrieve all posts for the initial discover page
    retrieve_posts = helper.get_posts(conn)
    posts = [
        {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()}
        for row in retrieve_posts
    ] 
    #Since the dictionary of posts contains a bytes object (the cover photo) this converts this into a str object using UTF-8 encoding


    #conn.close()

    if request.method == 'GET':
        search = request.args.get('search')
        if search: 
            
            retrieve_posts = helper.get_search(conn,search)
            posts = [
            {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()}
            for row in retrieve_posts
            ]
            return render_template('discover.html', posts=posts)

        else: 
            return render_template('discover.html', posts=posts)

    # If a POST request, handle the tag selection
    if request.method == 'POST':
        tag = request.form.get('tag')
        return redirect(url_for('select', tag=tag))

#Still integrated within the discover page ==> gets alls posts that have the selected tag the user choose to filter by
@app.route('/select/<string:tag>', methods=['GET'])
def select(tag):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    # Retrieve posts based on the selected tag
    post_dict = helper.sort_by_tag(conn, tag)
    posts = [
        {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()}
        for row in post_dict
    ]

    conn.close()

    return render_template('discover.html', posts=posts)


# @app.route('/discover', methods=['GET', 'POST'])
# def discover():
#     # Connect to the database
#     conn = dbi.connect()
#     curs = dbi.dict_cursor(conn)

#     query = """SELECT p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price FROM post AS p"""
#     params = []

#     # Handle search functionality
#     if request.method == 'GET':
#         search_term = str(request.args.get('search', '') or '')
#         if search_term:
#             query = """
#                 SELECT p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price
#                 FROM post AS p
#                 WHERE p.title LIKE %s OR p.tags LIKE %s OR p.price LIKE %s
#             """
#             search_pattern = f"%{search_term}%"
#             params = [search_pattern, search_pattern, search_pattern]

#     elif request.method == 'POST':
#         tag = request.form.get('tag')  
#         if tag:
#             query = """
#                 SELECT p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price
#                 FROM post AS p
#                 WHERE p.tags LIKE %s
#             """
#             params = [f"%{tag}%"]

#     curs.execute(query, params)
#     posts = [
#         {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()}
#         for row in curs.fetchall()
#     ]

#     conn.close()
#     return render_template('discover.html', posts=posts)


@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

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
