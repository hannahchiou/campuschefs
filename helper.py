# helper functions
import cs304dbi as dbi

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

def getpost(conn,pid):
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

if __name__ == '__main__':
    dbi.conf('campuschefs_db')
    conn = dbi.connect()