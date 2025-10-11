import flask
import sqlite3
import hashlib

app = flask.Flask(__name__)

with sqlite3.connect('database.db') as db:
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    pol TEXT,
    NOMERMAMI TEXT,
    RAZMER TEXT
    )
    ''')
    db.commit()
with sqlite3.connect('database.db') as db:
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    data TEXT
    )
    ''')
    db.commit()


def checkLogin(username, password):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''SELECT * FROM users WHERE username = "{username}" AND password = "{hashlib.sha1(password.encode('utf-8')).hexdigest()}"''')
        if len(cursor.fetchall())==1:
            return True
        return False

@app.route('/createNewUser/<username>/<password>/<pol>/<nomer_mami>/<razmer>')
def createNewUser(username, password, pol, nomer_mami, razmer):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''
        SELECT * FROM users WHERE username = "{username}"''')
        if cursor.fetchall() != []:
            return 'False'

    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''
        INSERT INTO users ('username', 'password', 'pol', 'NOMERMAMI', 'RAZMER') VALUES("{username}", "{hashlib.sha1(password.encode('utf-8')).hexdigest()}", "{pol}"," {nomer_mami}", "{razmer}")
        ''')
        db.commit()
    return 'True'

@app.route('/newPost/<username>/<password>/<data>')
def newPost(username, password, data):
    if not checkLogin(username, password):
        return 'False'

    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''INSERT INTO posts ('username', 'data') VALUES("{username}", "{data}")''')
        db.commit()

    return 'True'

@app.route('/login/<username>/<password>')
def login(username, password):
    if not checkLogin(username, password):
        return 'False'
    return 'True'

@app.route('/getPosts/<username>')
def getPosts(username):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''SELECT * FROM posts WHERE username = "{username}"''')
        return cursor.fetchall()


app.run(host='0.0.0.0', port=8080)