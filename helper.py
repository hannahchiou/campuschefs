# helper functions
import cs304dbi as dbi
import pymysql #for integrityError error checking
from flask import request


# insert new user info and password into the database
# when they first register just set username and password 
def insertUser(conn, username, passwd, name, email, school):
    try: 
        curs = dbi.cursor(conn)
        curs.execute('''INSERT INTO user(username, password, name, email_addr, school) 
                     VALUES(%s,%s,%s,%s,%s)''',
                     [username, passwd, name, email, school])
        conn.commit()
        return {"success": True, "message": "User inserted successfully."}
    except pymysql.IntegrityError:
        return {"success": False, "message": "Username already exists. Please choose a different username."}
    except Exception as err:
        return {"success": False, "message": f"Something went wrong: {repr(err)}"}


#given a uid- get all the post made by that user/uid   
def getRecipesByUser(conn, uid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT pid, title, cover_photo, text_descrip 
                    FROM post 
                    WHERE uid = %s''', [uid])
    return curs.fetchall()
#given a uid- get all the post made by that user/uid   
def getlikedRecipesByUser(conn, uid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT p.pid, p.title, p.cover_photo, p.text_descrip 
                    FROM post as p inner join likes as l on p.pid = l.pid
                    WHERE l.uid = %s''', [uid])
    return curs.fetchall()

# get a uid, name and password password given username
def getUserInfo(conn, username):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT uid, name, password, school FROM user WHERE username = %s''',[username])
    return curs.fetchone()

#get username by using the id 
def getUser_byID(conn, uid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT username FROM user WHERE uid = %s''',[uid])
    return curs.fetchone()


# inserts a new recipe into the database
def insertRecipe(conn, uid, post_date, title, cover_photo, serving_size, 
                 prep_time, cook_time, total_time, text_descrip, steps, tags, price):
    curs = dbi.cursor(conn)
    curs.execute('''insert into post(uid, post_date, title, cover_photo, serving_size, prep_time, 
                 cook_time, total_time, text_descrip, steps, price, tags)
                 values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                 [uid,post_date,title,cover_photo,serving_size,prep_time,cook_time,total_time,
                    text_descrip, steps, price, tags])
    conn.commit()
    return curs.lastrowid 

# insert the ingredients for the recipe
def insertIngredients(conn, pid, name, quantity, measurement):
    curs = dbi.cursor(conn)
    curs.execute('''insert into ingredient(pid, name, quantity, measurement) 
                 values (%s, %s, %s, %s)''', [pid, name, quantity, measurement]) 
    conn.commit()

def getPost(conn,pid):
    '''
    Returns all information from a given recipe post.
    SELECT * is relevant here because we are displaying
    all information about a recipe on the front end. 
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''
        SELECT *
        FROM post
        WHERE pid = %s
    '''
    curs.execute(sql,[pid])
    return curs.fetchone()

def getIngredients(conn,pid):
    '''
    Returns all ingredients from a given recipe post.
    SELECT * is relevant here because we are displaying
    all information about each ingredient on the front end recipe. 
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''
          SELECT * 
          FROM ingredient
          WHERE pid = %s'''
    curs.execute(sql,[pid])
    return curs.fetchall()

def deletePost(conn, pid):
    '''
    Deletes a post and all information (eg. recipes)
    associated with it (tables set up with CASCADE).
    '''
    curs = dbi.dict_cursor(conn)
    
    # First, delete associated likes for this post
    curs.execute('DELETE FROM likes WHERE pid = %s', [pid])

    # Then delete the comments
    curs.execute('DELETE FROM comment WHERE pid = %s', [pid])
    
    # Then delete the post
    curs.execute('DELETE FROM post WHERE pid = %s', [pid])
    conn.commit()

def deleteIngredients(conn,pid):
    '''
    Deletes all ingredients; used for deleting
    and reinserting ingredients during update.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''
    DELETE from ingredient
    WHERE pid = %s
    '''
    curs.execute(sql,[pid])
    conn.commit()

def updateRecipe(conn, pid, title, cover_photo, serving_size, 
                 prep_time, cook_time, total_time, text_descrip, steps, tags, price):
    '''
    Updates all information from a recipe.
    '''
    curs = dbi.cursor(conn)
    sql = '''
        UPDATE post
        SET 
            title = %s,
            cover_photo = %s,
            serving_size = %s,
            prep_time = %s,
            cook_time = %s,
            total_time = %s, 
            text_descrip = %s,
            steps = %s,
            tags = %s,
            price = %s
        WHERE pid = %s
    '''
    curs.execute(sql,[title,cover_photo,serving_size,prep_time,
                      cook_time,total_time,text_descrip,steps,
                      tags,price,pid])
    conn.commit()

def updateIngredients(conn, pid, name, quantity, measurement):
    '''
    Updates one ingredient for a given recipe, used in a loop
    to update all ingredients in app.py.
    '''
    curs = dbi.cursor(conn)
    sql = '''
        UPDATE ingredient
        SET 
            name = %s,
            quantity = %s,
            measurement = %s
        WHERE pid = %s 
    '''
    curs.execute(sql, [name, quantity, measurement, pid])
    conn.commit()

    
def get_posts(conn):
    '''
    Gets posts' ID, title, cover photo, description (if applicable),
    tags and price and orders all posts by ascending title
    '''
    curs = dbi.dict_cursor(conn)
    sql = """
        SELECT p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price
        FROM post AS p
        ORDER BY p.title ASC
    """
    curs.execute(sql)
    conn.commit()
    return curs.fetchall()

#this function takes in a search key and retrieves each post that has that search key anywhere in the title
def get_search(conn,search):
    curs = dbi.dict_cursor(conn)
    sql = """
        SELECT p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price
        FROM post AS p
        where p.title LIKE %s
        ORDER BY p.title ASC
    """
    curs.execute(sql, ['%' + search + '%'])
    conn.commit()
    return curs.fetchall()

#this function takes in a tag and filters and retrieves all posts that have that tag
def sort_by_tag(conn, tag):
    curs = dbi.dict_cursor(conn)
    sql = """
        SELECT p.pid, p.title, p.cover_photo, p.text_descrip, p.tags, p.price
        FROM post AS p
        WHERE p.tags LIKE %s
    """
    curs.execute(sql,['%'+ tag + '%'])
    conn.commit()
    return curs.fetchall()

# Combined helper function to like or unlike a post and return the updated like count
def toggle_like(conn, uid, pid):
    """Toggle the like status for a given post."""
    cursor = conn.cursor()
    
    # Check if the user has already liked the post
    cursor.execute('SELECT COUNT(*) FROM likes WHERE uid = ? AND pid = ?', (uid, pid))
    already_liked = cursor.fetchone()[0] > 0

    if already_liked:
        # If already liked, un-like the post
        cursor.execute('DELETE FROM likes WHERE uid = ? AND pid = ?', (uid, pid))
        action = 'unliked'
    else:
        # If not liked, add the like
        cursor.execute('INSERT INTO likes (uid, pid) VALUES (?, ?)', (uid, pid))
        action = 'liked'

    # Get the updated like count
    cursor.execute('SELECT COUNT(*) FROM likes WHERE pid = ?', (pid,))
    like_count = cursor.fetchone()[0]
    
    conn.commit()  # Commit the transaction
    return action, like_count

def insert(conn,post_id):
    '''
    Helper function to reduce repetition. Gets each row of ingredients from form and inserts it
    into the ingredients table
    '''
    index = 0
    while True:
        # Dynamically access each row of ingredients
        quantity = request.form.get(f'ingredients[{index}][quantity]')
        measurement = request.form.get(f'ingredients[{index}][measurement]')
        name = request.form.get(f'ingredients[{index}][name]')
        if not name:  # Stop when no more ingredient names are provided
            break
        insertIngredients(conn, 
                            pid = post_id,
                            name = name,
                            quantity = quantity,
                            measurement = measurement)
        index += 1

def getComments(conn, post_id):
    """
    Fetches all comments for a given recipe post.
    """
    curs = dbi.dict_cursor(conn)
    
    # Fetch all comments for the given post
    sql_comments = '''
        SELECT c.comment_id, c.uid, c.content, u.username
        FROM comment c
        JOIN user u ON c.uid = u.uid
        WHERE c.pid = %s
        ORDER BY c.comment_id ASC;
    '''
    curs.execute(sql_comments, [post_id])
    comments = curs.fetchall()

    return comments


def addComment(conn, post_id, user_id, content):
    """
    Adds a comment to a recipe post.
    """
    curs = dbi.cursor(conn)
    
    # Insert the comment into the comment table
    sql_insert_comment = '''
        INSERT INTO comment (uid, pid, content)
        VALUES (%s, %s, %s)
    '''
    curs.execute(sql_insert_comment, [user_id, post_id, content])
    conn.commit()
    
    # Get the ID of the newly inserted comment
    comment_id = curs.lastrowid
    
    return comment_id  # Return the ID of the newly created comment

def addLike(conn, uid, post_id):
    """
    Adds a like to the likes table, avoiding duplicates.
    """
    try:
        curs = dbi.cursor(conn)
        # Insert into likes table, ignoring duplicates
        sql_add_like = '''
            INSERT IGNORE INTO likes (uid, pid)
            VALUES (%s, %s)
        '''
        curs.execute(sql_add_like, [uid, post_id])
        conn.commit()
    except Exception as e:
        raise Exception(f"Error adding like: {e}")

def incrementLikeCount(conn, post_id):
    """
    Increments the like count for a specific post.
    """
    try:
        curs = dbi.cursor(conn)
        # Increment the like count for the given post
        sql_increment_like = '''
            UPDATE post
            SET like_count = like_count + 1
            WHERE pid = %s
        '''
        curs.execute(sql_increment_like, [post_id])
        conn.commit()

        # Fetch the updated like count
        sql_get_like_count = '''
            SELECT like_count
            FROM post
            WHERE pid = %s
        '''
        curs.execute(sql_get_like_count, [post_id])
        result = curs.fetchone()
        if result:
            return result[0]  # Return the updated like count
        else:
            raise Exception("Post not found after incrementing like count")
    except Exception as e:
        raise Exception(f"Error incrementing like count: {e}")

def getLikeCount(conn, post_id):
    """
    Fetches the like count for a specific post.
    """
    try:
        curs = dbi.dict_cursor(conn)
        sql_get_like_count = '''
            SELECT like_count
            FROM post
            WHERE pid = %s
        '''
        curs.execute(sql_get_like_count, [post_id])
        result = curs.fetchone()
        if result:
            return result['like_count']
        else:
            raise Exception("Post not found")
    except Exception as e:
        raise Exception(f"Error fetching like count: {e}")


def addLike(conn, uid, post_id):
    """
    Adds a like to the likes table, avoiding duplicates.
    """
    try:
        curs = dbi.cursor(conn)
        # Insert into likes table, ignoring duplicates
        sql_add_like = '''
            INSERT IGNORE INTO likes (uid, pid)
            VALUES (%s, %s)
        '''
        curs.execute(sql_add_like, [uid, post_id])
        conn.commit()
    except Exception as e:
        raise Exception(f"Error adding like: {e}")

def incrementLikeCount(conn, post_id):
    """
    Increments the like count for a specific post.
    """
    try:
        curs = dbi.cursor(conn)
        # Increment the like count for the given post
        sql_increment_like = '''
            UPDATE post
            SET like_count = like_count + 1
            WHERE pid = %s
        '''
        curs.execute(sql_increment_like, [post_id])
        conn.commit()

        # Fetch the updated like count
        sql_get_like_count = '''
            SELECT like_count
            FROM post
            WHERE pid = %s
        '''
        curs.execute(sql_get_like_count, [post_id])
        result = curs.fetchone()
        if result:
            return result[0]  # Return the updated like count
        else:
            raise Exception("Post not found after incrementing like count")
    except Exception as e:
        raise Exception(f"Error incrementing like count: {e}")

def getLikeCount(conn, post_id):
    """
    Fetches the like count for a specific post.
    """
    try:
        curs = dbi.dict_cursor(conn)
        sql_get_like_count = '''
            SELECT like_count
            FROM post
            WHERE pid = %s
        '''
        curs.execute(sql_get_like_count, [post_id])
        result = curs.fetchone()
        if result:
            return result['like_count']
        else:
            raise Exception("Post not found")
    except Exception as e:
        raise Exception(f"Error fetching like count: {e}")



if __name__ == '__main__':
    dbi.conf('campuschefs_db')
    conn = dbi.connect()