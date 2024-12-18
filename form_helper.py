'''
Functions to make inserting and updating forms less repetitive. 
Hannah Chiou
'''

from flask import (Flask, url_for, request)
from werkzeug.utils import secure_filename

app = Flask(__name__)

import os

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

def get_form_info():
    '''
    Gets all form information and returns it. 
    '''
    title = request.form.get('title')
    # Handles prep time, sets to 0 if prep time is negative
    prep_time_str = request.form.get('prep-time', '')
    prep_time = max(0, int(prep_time_str) if prep_time_str else 0)

    # Handle cook time, sets to 0 if cook time is negative
    cook_time_str = request.form.get('cook-time', '')
    cook_time = max(0, int(cook_time_str) if cook_time_str else 0)

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

    return title, photo_url,size, prep_time,cook_time,total_time, description,steps,tags,price

