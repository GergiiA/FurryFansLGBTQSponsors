import base64
import rapidfuzz
import flask
from flask import request
import sqlite3
import hashlib
import json
from flask_apscheduler import APScheduler

app = flask.Flask(__name__)



with sqlite3.connect('database.db') as db:
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    pol TEXT,
    NOMERMAMI TEXT,
    RAZMER TEXT,
    data TEXT
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

def updateUserList():
    global userList
    #print("Updating user list")
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute('''
        select id, username from users
        ''')
        userList = cursor.fetchall()
        #print(userList)

@app.route('/createNewUser2', methods=['POST'])
def createNewUser2():
    data = request.get_json(force=True)
    #data=json.loads(json_data)
    print(data)
    print(data['username'])

    for key, value in data.items():
        print(key, value)
        if value == '':
            return 'All data must be filled in'

    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''
         SELECT * FROM users WHERE username = "{data['username'].lower()}"''')
        if cursor.fetchall() != []:
            return 'Username already exists'

    userData = base64.b64encode(json.dumps({'subscribes':[], 'subscribers': 0}).encode('utf-8')).decode('utf-8')

    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''
         INSERT INTO users ('username', 'password', 'pol', 'NOMERMAMI', 'RAZMER', 'data') VALUES("{data['username']}", "{hashlib.sha1(data['password'].encode('utf-8')).hexdigest()}", "{data['pol']}"," {data['momnum']}", "{data['razmer']}", "{userData}")
         ''')
        db.commit()
    return 'True'

@app.route('/newPost/', methods=['POST'])
def newPost():
    jsonData = request.get_json(force=True)
    if not checkLogin(jsonData['username'], jsonData['password']):
        return 'Wrong credentials'

    if jsonData['postType']=='image':
        if len(jsonData['file']) > 64000000:
            return 'File too big'

        data = base64.b64encode(json.dumps({'postType': 'image' ,'title': jsonData['title'], 'fileTitle':jsonData['fileTitle'], 'file': jsonData['file'], 'size': jsonData['size']}).encode('utf-8')).decode('utf-8')

        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            #print(f'''INSERT INTO posts ('username', 'data') VALUES("{jsonData['username']}", "{data}")''')
            cursor.execute(f'''INSERT INTO posts ('username', 'data') VALUES("{jsonData['username']}", "{data}")''')
            db.commit()

        return 'True'

    elif jsonData['postType']=='text':
        data = base64.b64encode(json.dumps(
            {'postType': 'text', 'title': jsonData['title'], 'text': jsonData['text']}).encode('utf-8')).decode('utf-8')

        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            print(f'''INSERT INTO posts ('username', 'data') VALUES("{jsonData['username']}", "{data}")''')
            cursor.execute(f'''INSERT INTO posts ('username', 'data') VALUES("{jsonData['username']}", "{data}")''')
            db.commit()

        return 'True'

@app.route('/login/', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if not checkLogin(username, password):
        return 'Username or password\n is incorrect'
    return 'True'

@app.route('/getPosts/<username>')
def getPosts(username):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''SELECT * FROM posts WHERE username = "{username}"''')
        return cursor.fetchall()

@app.route('/getSubscribes')
def getSubscribes():
    data=request.get_json(force=True)

    if not checkLogin(data['username'], data['password']):
        return 'invalid credentials'

    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''SELECT data FROM users WHERE username = "{data['username']}"''')
        userdata = json.loads(base64.b64decode(cursor.fetchall()[0][0]).decode('utf-8'))
    #print(userdata)
    return userdata['subscribes']

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json(force=True)
    print(data)
    if not checkLogin(data['username'], data['password']):
        return 'invalid credentials'

    with sqlite3.connect('database.db') as db:
        print(f'''SELECT data FROM users WHERE username = "{data['username']}"''')
        cursor = db.cursor()
        cursor.execute(f'''SELECT data FROM users WHERE username = "{data['username']}"''')
        userdata = json.loads(base64.b64decode(cursor.fetchall()[0][0]).decode('utf-8'))
        print(userdata)

        if data['subscribe'] == True:
            if data['subscribeTo'] not in userdata['subscribes']:
                print('subscribed')
                userdata['subscribes'].append(data['subscribeTo'])
        elif data['subscribe'] == False:
            if data['subscribeTo'] in userdata['subscribes']:
                userdata['subscribes'].remove(data['subscribeTo'])

        #print(f'''UPDATE users SET data = "{base64.b64encode(json.dumps(userdata).encode('utf-8')).decode('utf-8')}" WHERE username = "{data['username']}"''')
        cursor.execute(f'''UPDATE users SET data = "{base64.b64encode(json.dumps(userdata).encode('utf-8')).decode('utf-8')}" WHERE username = "{data['username']}"''')#adding new data about who user is subscribed to database

        cursor.execute(f'''SELECT data FROM users WHERE username = "{data['subscribeTo']}"''')
        userdata = json.loads(base64.b64decode(cursor.fetchall()[0][0]).decode('utf-8'))
        if 'subscribers' not in userdata.keys():
            userdata['subscribers'] = 0
        userdata['subscribers']= userdata['subscribers']+1 if data['subscribe'] else userdata['subscribers']-1
        #print(userdata)
        encoded = base64.b64encode(json.dumps(userdata).encode('utf-8')).decode('utf-8')
        #print(encoded)

        cursor.execute(f'''UPDATE users SET data="{encoded}" WHERE username = "{data['subscribeTo']}"''')

        return 'True'

@app.route('/searchUsers/', methods=['POST'])
def searchUsers():
    global userList
    search = request.get_json(force=True)['search']
    bestResults = sorted(userList, key=lambda tupl: rapidfuzz.fuzz.ratio(search, tupl[1]), reverse=True)[:10]

    return json.dumps(bestResults)

@app.route('/getPublicUserData/', methods=['GET'])
def getPublicUserData():
    data=json.loads(request.get_json(force=True))

    username = data['username']

    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''SELECT pol, NOMERMAMI, RAZMER, data FROM users WHERE username = "{username}"''')
        userdata = cursor.fetchall()

    #print(data)
    selfUsername = data['selfUsername']
    selfPassword = data['selfPassword']

    if checkLogin(selfUsername, selfPassword):
        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            cursor.execute(f'''SELECT data FROM users WHERE username = "{selfUsername}"''')
            selfUserdata = json.loads(base64.b64decode(cursor.fetchall()[0][0]).decode('utf-8'))
            if username in selfUserdata['subscribes']:
                userdata.append('True')
            else:
                userdata.append('False')
    #print(userdata)
    subCount = json.loads(base64.b64decode(userdata[0][3].encode('utf-8')).decode('utf-8'))['subscribers']
    userdata.append(subCount)

    return json.dumps(userdata)

@app.route('/getLast10Posts/', methods=['GET'])
def getLast10Posts():
    data=json.loads(request.get_json(force=True))
    print(data)

    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''
        SELECT data FROM posts WHERE username = "{data["username"]}" ORDER BY id LIMIT 10 OFFSET {data['page']}
        ''')
        postsData = cursor.fetchall()#json.loads(base64.b64decode(cursor.fetchall()[0][0]).decode('utf-8'))

        #print(postsData)
        #print(len(postsData))
    return json.dumps(postsData)


updateUserList()

scheduler = APScheduler()
scheduler.add_job(func=updateUserList, trigger='interval', seconds=5, id='updateUserList')
scheduler.start()
app.run()#host='0.0.0.0', port=8080, )#debug=True)