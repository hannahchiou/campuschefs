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
    Our homepage. Gets username information from our session
    '''
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template('main.html', username=username,
                           page_title = 'home page')

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


@app.route('/register/', methods = ['GET','POST'])
def register():
    '''
    Registers a new account.
    '''
    if request.method == "GET":
        return render_template('register.html',  page_title = 'registration page')  # Show the register  page
    conn = dbi.connect()
    name = request.form.get('name')
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    if password1 != password2:
        flash('Please enter matching passwords.')
        return redirect( url_for('register'))
    email = request.form.get('email')
    school = request.form.get('school')
    
    # Hash the password
    hashed = bcrypt.hashpw(password1.encode('utf-8'),
                          bcrypt.gensalt())
    stored = hashed.decode('utf-8')

    # Call the helper function to insert the new user
    result = helper.insertUser(conn, username, stored, name, email, school)

    if result["success"]:
        flash("Your profile has been created. Please log in now")
        return redirect(url_for('login'))
    else:
        flash(result["message"])
        return redirect(url_for('register'))

@app.route('/login/', methods=['GET','POST'])
def login():
    '''
    Logs in existing users.
    '''
    if request.method == "GET":
        return render_template('login.html',  page_title = 'login page')  # Show the login page
    
    username = request.form.get('username')
    password = request.form.get('password1')

    conn = dbi.connect()
    result = helper.getUserInfo(conn, username)
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
        # print(f"Your username is: {session['username']}, and your UID is: {session['uid']}, and your login status is: {session['logged_in']}")
        # session['visits'] = 1
        return redirect(url_for('index'))
    else: 
        flash('Login incorrect. Please try again or register')
        return redirect(url_for('index'))
    
@app.route('/logout/')
def logout():
    '''
    Logs a user out and removes session information.
    '''
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
    Displays our recipe form HTML (see templates folder) for them to fill out 

    For POST: collects the form information, inserts it into our SQL database,
    and displays it as a recipe post. Redirects users to the recipe post once it 
    is successfully inserted. 
    '''
    conn = dbi.connect()

    if request.method == 'GET':
        return render_template('recipeform.html', page_title = "Form Page")
    
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
                            uid = session.get('uid'), 
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
        post_owner_id = post['uid']
        current_user = session.get('uid')
        ingredients = helper.getIngredients(conn, post_id)

        if not post: 
            flash('''The recipe you requested is not in the database.
                  Please reenter the information.''')
            return redirect(url_for('index'))

        photo_url = post['cover_photo']
        if isinstance(photo_url, bytes):
            photo_url = photo_url.decode('utf-8')

        return render_template('recipepost.html',
                               username= helper.getUser_byID(conn,post['uid'])['username'],
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
                               photo_url = photo_url,
                               is_owner = (current_user == post_owner_id))
    
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
        current_user = session.get('uid')
        if recipe['uid'] == current_user: 
            ingredients = helper.getIngredients(conn,post_id)
            id = post_id 
        
            return render_template('updatepost.html',
                               post_title = "Update Post",
                               post_id = id,
                               title=recipe['title'],
                               size = recipe['serving_size'],
                               cover_photo=recipe['cover_photo'],
                               prep_time=recipe['prep_time'],
                               cook_time=recipe['cook_time'],
                               ingredients=ingredients,
                               steps=recipe['steps'],
                               description=recipe['text_descrip'])
        else: 
            flash('you do not have access to update this post')
            return redirect(url_for('index'))
    
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



@app.route('/discover', methods=['GET'])
def discover():
    '''
    For GET: uses a helper function to retrieve all posts in the database. 
    Also handles cases when users use the search bar. Uses another function to retrieve 
    all post with the search key in the title. It also handles when users choose to 
    filter the posts by tags and redirects the user to the select route. 
    '''
    conn = dbi.connect()
    search_query = request.args.get('search')  # Search query from URL
    tag_filter = request.args.get('tag')       # Tag filter from URL

    # If search query exists, filter by search
    if search_query:
        retrieve_posts = helper.get_search(conn, search_query)
    # If tag filter exists, filter by tag
    elif tag_filter:
        retrieve_posts = helper.sort_by_tag(conn, tag_filter)
    else:
        retrieve_posts = helper.get_posts(conn)  # Default to all posts

    # For decoding byte-like objects
    posts = [
        {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()}
        for row in retrieve_posts
    ]
    return render_template('discover.html', page_title="Discover Recipes", posts=posts)
    
@app.route('/select/<string:tag>', methods=['GET'])
def select(tag):
    '''
    Still integrated within the discover page ==> gets all posts that 
    have the selected tag the user choose to filter by
    '''
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    # Retrieve posts based on the selected tag
    post_dict = helper.sort_by_tag(conn, tag)
    posts = [
        {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()}
        for row in post_dict
    ]

    conn.close()

    return render_template('discover.html', page_title="Discover Page", posts=posts)

#This is our profile route, it takes information from the session to form the front end. It does this by taking the 
#the username in the session and then performing a query to retrieve all post made by that user .
@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':

        conn = dbi.connect()
        username = session.get('username')
        user_dict = helper.getUserInfo(conn, username)
        user = {
            'name': user_dict['name'],
            'username': username,
            'school': user_dict['school']
        }
        user_recipes = helper.getRecipesByUser(conn, user_dict['uid'])
        #user_recipes = helper.get_posts(conn) # displays all post for now since posts are not linked to uid 
        #The usage of v.decode decodes the image bytes.
        recipes = [
            {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()}
            for row in user_recipes
            ]
        return render_template('profile.html',page_title="Profile Page", user=user, recipes=recipes)
    if request.method == 'POST':
        return redirect(url_for('logout'))

@app.route('/like_post/<int:pid>', methods=['POST'])
def like_post_route(pid):
    uid = session.get('uid')  # Get current user ID
    if not uid:
        return jsonify({'error': 'User not logged in'}), 401

    conn = dbi.connect()  # Connect to the database
    action, like_count = toggle_like(conn, uid, pid)  # Use helper function to toggle like status

    return jsonify({
        'action': action,  # 'liked' or 'unliked'
        'like_count': like_count  # The updated like count after toggling
    })

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
