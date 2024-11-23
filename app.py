from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
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

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/recipeform/', methods = ['GET','POST'])
def recipeform():
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
        # convert tags to a comma separated string for SET
        if isinstance(tags, list):
            tags = ','.join(tags)
        description = request.form.get('description')
        steps = request.form.get('steps')

        # Get the current date and time
        currentDate = datetime.datetime.now()
        # Format it into 'month-day-year'
        # post_date = currentDate.strftime("%m-%d-%Y")
        
        # format into datetime format for inserting into database
        post_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

        file = request.files.get('cover-photo')
        photo_url = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            photo_url = url_for('static', filename=f'uploads/{filename}')

        # get the post id
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
        
        print(last_insert)
        
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
        print(f"last insert pid is: {last_insert}")
        # redirect to recipe/post_id
        return redirect(url_for('recipepost', post_id = last_insert))
    
# recipe post
@app.route('/recipepost/<post_id>', methods = ['GET'])
def recipepost(post_id):
    if request.method == 'GET':
        conn = dbi.connect()
        post = helper.getpost(conn, post_id)
        ingredients = helper.getIngredients(conn, post_id)

        if not post: 
            flash('''The recipe you requested is not in the database.
                  Please reenter the information.''')
            return redirect(url_for('index'))
        print(f"The link is: {post['cover_photo']}")

        photo_url = post['cover_photo']
        # decode photo if it is in binary
        if isinstance(photo_url, bytes):
            photo_url = photo_url.decode('utf-8')

        return render_template('recipepost.html',
                               username = request.cookies.get('uid'),
                               title = post['title'],
                               date = post['post_date'],
                               prep_time = post['prep_time'],
                               cook_time = post['cook_time'],
                               total_time = post['total_time'],
                               price = post['price'], size = post['serving_size'],
                               tags = post['tags'], 
                               description = post['text_descrip'], 
                               steps = post['steps'],
                               ingredients = ingredients,
                               photo_url = photo_url)

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
