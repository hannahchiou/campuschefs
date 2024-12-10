# helper functions
import cs304dbi as dbi
import pymysql #for integrityError error checking


# insert new user info and password into the database
# when they first register just set username and password 
def insertUser(conn, username, passwd, name):
    try: 
        curs = dbi.cursor(conn)
        curs.execute('''INSERT INTO user(username, password, name) VALUES(%s,%s,%s)''',
                     [username, passwd, name])
        conn.commit()
        return {"success": True, "message": "User inserted successfully."}
    except pymysql.IntegrityError:
        return {"success": False, "message": "Username already exists. Please choose a different username."}
    except Exception as err:
        return {"success": False, "message": f"Something went wrong: {repr(err)}"}
    
def getRecipesByUser(conn, uid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT pid, title, cover_photo, text_descrip 
                    FROM post 
                    WHERE uid = %s''', [uid])
    return curs.fetchall()

# get a uid, name and password password given username
def getUser(conn, username):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT uid, name, password FROM user WHERE username = %s''',[username])
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
    Returns all information from a given recipe post
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
    Returns all ingredients from a given recipe post
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''
          SELECT * 
          FROM ingredient
          WHERE pid = %s'''
    curs.execute(sql,[pid])
    return curs.fetchall()

# def deletePost(conn,pid):
#     curs = dbi.dict_cursor(conn)
#     sql = '''
#         DELETE FROM ingredient
#         WHERE pid = %s
#     '''
#     curs.execute(sql, [pid])
#     conn.commit()  # Commit the deletion of dependent rows

#     # Now delete the post from the 'post' table
#     sql = '''
#         DELETE FROM post
#         WHERE pid = %s
#     '''
#     curs.execute(sql, [pid])
#     conn.commit()  # Commit the deletion of the post

def deletePost(conn, pid):
    curs = dbi.dict_cursor(conn)
    sql = '''
        DELETE FROM post
        WHERE pid = %s
    '''
    curs.execute(sql, [pid])
    conn.commit()  # Commit the deletion

def deleteIngredients(conn,pid):
    curs = dbi.dict_cursor(conn)
    sql = '''
    DELETE from ingredient
    WHERE pid = %s
    '''
    curs.execute(sql,[pid])
    conn.commit()

def updateRecipe(conn, pid, title, cover_photo, serving_size, 
                 prep_time, cook_time, total_time, text_descrip, steps, tags, price):
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
    curs = dbi.cursor(conn)
    print(f"SQL Parameters: pid={pid}, name={name}, quantity={quantity}, measurement={measurement}")
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

if __name__ == '__main__':
    dbi.conf('campuschefs_db')
    conn = dbi.connect()