# helper functions
import cs304dbi as dbi

# inserts a new recipe into the database
def insertRecipe(conn, uid, title, cover_photo, serving_size, 
                 prep_time, cook_time, text_descrip, steps, tags, price):
    curs = dbi.cursor(conn)
    curs.execute('''insert into post(uid, title, cover_photo, serving_size, prep_time, 
                 cook_time, text_descrip, steps, tags, price)
                 values (%s,%s,%s,%s,%s,%s,%s)''',
                 [uid,title,cover_photo,serving_size,prep_time,cook_time,
                    text_descrip, steps, tags, price])
    conn.commit()

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
    curs = dbi.cursor(conn)
    sql = '''
        SELECT *
        FROM post
        WHERE pid = %s
    '''
    curs.execute(sql,[pid])
    return curs.fetchone()



if __name__ == '__main__':
    dbi.conf('campuschefs_db')
    conn = dbi.connect()