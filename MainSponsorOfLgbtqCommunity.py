import tkinter as tk
from tkinter import messagebox, filedialog, ttk, PhotoImage
from pygments.lexers import q
from tkscrolledframe import ScrolledFrame
import requests
import json
import base64
from PIL import Image, ImageTk
import io
import urllib3
import math
import random


urllib3.disable_warnings()


SERVER_URL = "http://127.0.0.1:5000"
root = tk.Tk()
USERNAME = None
PASSWORD = None


def clear_all_inside_frame(frame):
    # Iterate through every widget inside the frame
    for widget in frame.winfo_children():
        widget.destroy()

def goto(func, args=[]):
    clear_all_inside_frame(root)
    func(*args).pack()#(side=tk.NSEW, fill=tk.BOTH, expand=True)

def checkLogin(username, password):
    data={'username': username, 'password': password}
    json_data = json.dumps(data)

    answer = requests.post(SERVER_URL+'/login', data=json_data, headers={'Content-Type': 'application/json'}, verify=False)

    if answer.text == 'True':
        #global USERNAME, PASSWORD
        #USERNAME = username
        #PASSWORD = password
        return True
    else:
        return answer

def createNewUser(username, password, pol, nomermami, razmer):
    data={'username': username, 'password': password, 'pol': pol, 'momnum': nomermami, 'razmer': razmer}
    json_data = json.dumps(data)


    answer = requests.post(SERVER_URL+'/createNewUser2', data=json_data, headers={'Content-Type': 'application/json'}, verify=False)

    if answer.text == 'True':
        global USERNAME, PASSWORD
        USERNAME = username
        PASSWORD = password
        return True
    else:
        return answer

def createNewUserWrap(username, password, pol, nomermami, razmer):
    created=createNewUser(username, password, pol, nomermami, razmer)
    #print(created.text)
    if created==True:
        goto(main)
    else:
        goto(register, args=[created.text])

def checkLoginWrap(username, password):
    answer=checkLogin(username, password)
    if answer==True:
        global USERNAME, PASSWORD
        USERNAME = username
        PASSWORD = password
        saveData(USERNAME, PASSWORD)
        goto(main)
    else:
        goto(login, args=[answer.text])

def onStart():
    global USERNAME, PASSWORD
    file=open('clientData.json', 'r')

    #print(len(file.read()))
    if len(file.read())==0:#if file is empty write none to it
        file = open('clientData.json', 'w')
        file.write(json.dumps({'username': 'Tm9uZQ==', 'password': 'Tm9uZQ=='}))
        file.close()
        #print("sadfsdf")

    file=open('clientData.json', 'r')
    data=json.load(file)
    USERNAME=base64.b64decode(data['username']).decode()
    PASSWORD=base64.b64decode(data['password']).decode()
    #print(USERNAME)
    #print(PASSWORD)

def saveData(username,password):
    json.dump({'username': base64.b64encode(username.encode('utf-8')).decode(), 'password': base64.b64encode(password.encode('utf-8')).decode()}, open('clientData.json', 'w'))

def selectFile():
    filePath=filedialog.askopenfilename(title="Select a file", filetypes=[('photo files', ('*.png', '*.jpg', '*.jpeg'))])

    if filePath:
        return filePath
    return None

def selectFileWrap():
    filePath=selectFile()
    if filePath is None:
        return
    goto(create2, args=['Image', filePath])

def makeImagePost(filePath, title):
    if filePath is None:
        messagebox.showerror("Error", "Please select a file")
        return
    allowedFiletypes=['png', 'jpg', 'jpeg']
    #print(filePath.lower().split('.')[-1] )
    if filePath.lower().split('.')[-1] not in allowedFiletypes:
        messagebox.showerror("Error", "Incorrect file type")
        return
    image = open(filePath, 'rb').read()
    size= Image.open(filePath).size
    data={'postType': 'image', 'username': USERNAME, 'password': PASSWORD, 'title': title, 'file': base64.b64encode(image).decode(), 'fileTitle': filePath.split('/')[-1], 'size': size}
    json_data = json.dumps(data)
    #print(json_data)
    response = requests.post(SERVER_URL+'/newPost', data=json_data, headers={'Content-Type': 'application/json'}, verify=False)
    if response.text == 'True':
        messagebox.showinfo("Success", "Posted successfully")
        goto(create2, args=['text'])
    else:
        messagebox.showerror("Error", "Failed to post")
        goto(create2, args=['Image', response.text])

def makeTextPost(title, text):
    data={'postType': 'text', 'title': title, 'text': text, 'username': USERNAME, 'password': PASSWORD}
    json_data = json.dumps(data)

    answer = requests.post(SERVER_URL+'/newPost', data=json_data, headers={'Content-Type': 'application/json'}, verify=False)
    print(answer.text)
    if answer.text == 'True':
        messagebox.showinfo("Success", "Posted successfully")
        goto(create2, ['Text'])

def logout():
    saveData('None', 'None')
    goto(welcome)

def getSubscribes():
    data={'username': USERNAME, 'password': PASSWORD}
    answer = requests.get(SERVER_URL+'/getSubscribes', json=data ,headers={'Content-Type': 'application/json'}, verify=False)
    #print(answer.text)
    if answer.text != 'invalid credentials':
        subscribes=json.loads(answer.text)
        return subscribes

    else:
        return []

def getUsers():
    answer=requests.get(SERVER_URL+'/getUsers', verify=False)#, headers={'Content-Type': 'application/json'})

def requestSearch(prompt):
    data=json.dumps({'search': prompt})

    answer = requests.post(SERVER_URL+'/searchUsers', data=data, headers={'Content-Type': 'application/json'}, verify=False)
    #print(answer.text)
    return json.loads(answer.text)

def getDataAboutOtherUser(username):
    data=json.dumps({'username': username, 'selfUsername': USERNAME, 'selfPassword': PASSWORD})
    answer = requests.get(SERVER_URL+'/getPublicUserData', json=data, headers={'Content-Type': 'application/json'}, verify=False)
    #print(answer.text)
    return json.loads(answer.text)

def subscribe(subscribeTo, subscribe=True):
    data={'username': USERNAME, 'password': PASSWORD, 'subscribeTo': subscribeTo, 'subscribe':subscribe}

    answer = requests.post(SERVER_URL+'/subscribe', json=data, headers={'Content-Type': 'application/json'}, verify=False)

    if answer.text == 'True':
        return True
    else:
        return answer

def getlast10Posts(username, page=0):
    data=json.dumps({'username': username, 'page': page})
    #print(data)
    answer = requests.get(SERVER_URL+'/getLast10Posts', json=data, headers={'Content-Type': 'application/json'}, verify=False)

    json_data = json.loads(answer.text)
    return json_data

#tkinter windows
def welcome():
    frame1 = ttk.Frame(root)

    label = ttk.Label(frame1, text="Welcome to FurryFans")
    label.grid(row=0, column=0)

    loginButton = ttk.Button(frame1, text="Login", command=lambda: goto(login))
    loginButton.grid(row=1, column=0)

    registerButton = ttk.Button(frame1, text="Register", command=lambda: goto(register))
    registerButton.grid(row=2, column=0)

    return frame1

def login(*args):
    frame=ttk.Frame(root)

    backButton = ttk.Button(frame, text="Back", command=lambda: goto(welcome))
    backButton.grid(row=0, column=0)

    login = ttk.Label(frame, text="Login")
    login.grid(row=0, column=1)

    usernameLabel = ttk.Label(frame, text="Username")
    usernameLabel.grid(row=1, column=0)

    usernameEntry = ttk.Entry(frame, width=40)
    usernameEntry.grid(row=1, column=1)

    passwordLabel = ttk.Label(frame, text="Password")
    passwordLabel.grid(row=2, column=0)

    passwordEntry = ttk.Entry(frame, width=40)
    passwordEntry.grid(row=2, column=1)

    errorLabel = ttk.Label(frame, text=args[0] if len(args) else "")
    errorLabel.grid(row=3, column=0)

    submitButton = ttk.Button(frame, text="Login", command=lambda: checkLoginWrap(usernameEntry.get(), passwordEntry.get()))
    submitButton.grid(row=4, column=0)
    submitButton.grid(row=3, column=1)

    return frame

def register(*args):
    frame = ttk.Frame(root)

    backButton = ttk.Button(frame, text="Back", command=lambda: goto(welcome))
    backButton.grid(row=0, column=0)

    registerLabel = ttk.Label(frame, text="Register")
    registerLabel.grid(row=0, column=1)

    usernameLabel = ttk.Label(frame, text="Username")
    usernameLabel.grid(row=1, column=0)

    usernameEntry = ttk.Entry(frame, width=40)
    usernameEntry.grid(row=1, column=1)

    passwordLabel = ttk.Label(frame, text="Password")
    passwordLabel.grid(row=2, column=0)

    passwordEntry = ttk.Entry(frame, width=40)
    passwordEntry.grid(row=2, column=1)

    polLabel = ttk.Label(frame, text="Pol")
    polLabel.grid(row=3, column=0)

    polEntry = ttk.Entry(frame, width=40)
    polEntry.grid(row=3, column=1)

    nomerMamiLabel = ttk.Label(frame, text="Nomer Mami")
    nomerMamiLabel.grid(row=4, column=0)

    nomerMamiEntry = ttk.Entry(frame, width=40)
    nomerMamiEntry.grid(row=4, column=1)

    razmerLabel = ttk.Label(frame, text="Razmer")
    razmerLabel.grid(row=5, column=0)

    razmerEntry = ttk.Entry(frame, width=40)
    razmerEntry.grid(row=5, column=1)

    errorLabel = ttk.Label(frame, text=args[0] if len(args) == 1 else "")
    errorLabel.grid(row=6, column=0)

    submitButton = ttk.Button(frame, text="Register", command=lambda: createNewUserWrap(
        usernameEntry.get(), passwordEntry.get(), polEntry.get(), nomerMamiEntry.get(), razmerEntry.get()))
    submitButton.grid(row=6, column=1)

    return frame

def main():
    #if not checkLogin(USERNAME, PASSWORD):
        #goto(login)
        #return tk.Frame(root)
        #pass
    mainFrame = tk.Frame(root)

    furryFansLabel = tk.Label(mainFrame, text="FurryFans")
    furryFansLabel.grid(row=0, column=0)

    welcomeBackText = tk.Label(mainFrame, text="Welcome back, "+str(USERNAME))
    welcomeBackText.grid(row=1, column=0)

    createButton=tk.Button(mainFrame, text="Make post", command=lambda: goto(create2, ['Text']))
    createButton.grid(row=2, column=0)

    subscribesButton=tk.Button(mainFrame, text="Subscribes", command=lambda: goto(subscribes))
    subscribesButton.grid(row=3, column=0)

    accountButton = tk.Button(mainFrame, text="account", command=lambda: goto(account))
    accountButton.grid(row=4, column=0)

    searchButton = tk.Button(mainFrame, text="Search", command=lambda: goto(search))
    searchButton.grid(row=5, column=0)

    freeSpinButton = tk.Button(mainFrame, text="Free Spin!!!", command=lambda: goto(freeSpin))
    freeSpinButton.grid(row=6, column=0)


    return mainFrame

def create2(*args):
    frame = tk.Frame(root)

    backButton = tk.Button(frame, text="Back", command=lambda: goto(main))
    backButton.grid(row=0, column=0)

    textTypeButton = tk.Button(frame, text="Text post type", command=lambda: goto(create2, ['Text']))
    textTypeButton.grid(row=1, column=0)

    textTypeButton = tk.Button(frame, text="Image post type", command=lambda: goto(create2, ['Image']))
    textTypeButton.grid(row=1, column=1, sticky=tk.W)

    if args[0]=='Text':
        titleLabel = tk.Label(frame, text="Title: ")
        titleLabel.grid(row=2, column=0)

        titleInput = tk.Entry(frame, width=40)
        titleInput.grid(row=2, column=1)

        textLabel = tk.Label(frame, text="Text: ")
        textLabel.grid(row=3, column=0)

        textInput = tk.Entry(frame, width=40)
        textInput.grid(row=3, column=1)

        uploadButton = tk.Button(frame, text="Make post", command=lambda: makeTextPost(titleInput.get(), textInput.get()))
        uploadButton.grid(row=4, column=1)


    elif args[0]=='Image':
        filePathLabel = tk.Label(frame, text=f"File path: {args[1] if len(args) > 1 else ''}")
        filePathLabel.grid(row=2, column=0)

        selectFileButton = tk.Button(frame, text="Upload file", command=lambda: selectFileWrap())
        selectFileButton.grid(row=2, column=1)

        titleLabel = tk.Label(frame, text="Title: ")
        titleLabel.grid(row=3, column=0)

        titleInput = tk.Entry(frame, width=40)
        titleInput.grid(row=3, column=1)



        uploadButton = tk.Button(frame, text="Make post", command=lambda: makeImagePost(args[1] if len(args)>1 else '' ,titleInput.get()))
        uploadButton.grid(row=4, column=1)









    return frame

def account():
    frame = tk.Frame(root)

    backButton = tk.Button(frame, text="Back", command=lambda: goto(main))
    backButton.grid(row=0, column=0)

    name = tk.Label(frame, text="Name: "+USERNAME)
    name.grid(row=1, column=0)

    logoutButton = tk.Button(frame, text="Logout", command=lambda: logout())
    logoutButton.grid(row=1, column=1)

    return frame

def subscribes():
    frame = tk.Frame(root)

    backButton = tk.Button(frame, text="Back", command=lambda: goto(main))
    backButton.grid(row=0, column=0)

    subs=getSubscribes()
    #print(subs)
    for index, sub in enumerate(subs):
        tk.Button(frame, command=lambda s=sub: goto(viewSomeone, [s, [subscribes]]), text=sub).grid(row=index, column=1)

    if len(subs)==0:
        lbl=tk.Label(frame, text="No subscribes")
        lbl.grid(row=0, column=1)


    return frame

def search(*args):
    #args format
    #0 is data from search
    #1 is input string

    frame = tk.Frame(root)
    #print(args)
    backButton = tk.Button(frame, text="Back", command=lambda: goto(main))
    backButton.grid(row=0, column=0)

    inputString = tk.Entry(frame, width=40)
    inputString.grid(row=0, column=1)

    inputString.insert(0, args[1] if len(args) >1 else "")

    searchButton = tk.Button(frame, text="Search", command=lambda: goto(search, [requestSearch(inputString.get()), inputString.get()]))
    searchButton.grid(row=0, column=2)

    #print(args[0] if len(args) >0 else None)
    if len(args)==0:
        searchResults=[]
    elif len(args)==1:
        searchResults=args[0]

    for i, result in enumerate(args[0] if len(args) >0 else []):
        tk.Button(
            frame,
            text=str(result[1]),
            command=lambda res=result: goto(viewSomeone, [res[1], [search ,[args[0], inputString.get()]]])
        ).grid(row=i + 1, column=1)
        #print(result)

    return frame

def viewSomeone(*args):
    #how aegs are suppost to be given
    # 0 is username of person to view
    # 1 is a list for back button
    #   0 is name of function to go back
    #   1 list for args which will be given to 0

    if len(args) == 0:
        goto(main)
    #print('args', args)

    frame = tk.Frame(root)
    data=getDataAboutOtherUser(args[0])


    backButton = tk.Button(frame, text="Back", command=lambda: goto(args[1][0], args[1][1] if len(args[1])>1 else []))
    backButton.grid(row=0, column=0)

    usernameLabel = tk.Label(frame, text="Username: "+args[0])
    usernameLabel.grid(row=0, column=1)

    subscribers = tk.Label(frame, text="Subscribers: "+ str(data[2]))
    subscribers.grid(row=0, column=2)

    polLabel = tk.Label(frame, text="Pol: "+data[0][0])
    polLabel.grid(row=1, column=1)

    nomerMamiLabel = tk.Label(frame, text="Nomer Mami: "+data[0][1])
    nomerMamiLabel.grid(row=2, column=1)

    razmerLabel = tk.Label(frame, text="Razmer: "+data[0][2])
    razmerLabel.grid(row=3, column=1)

    def subscribeAndUpdate():
        if data[1]!='True':
            subscribe(args[0])
        else:
            subscribe(args[0], False)
        goto(viewSomeone, args)

    subscribeButton = tk.Button(frame, text="Subscribe" if data[1]!='True' else 'Unsubscribe', command=subscribeAndUpdate)#lambda: subscribe(args[0]) if data[1]!='True' else subscribe(args[0], False))
    subscribeButton.grid(row=1, column=2)


    posts=getlast10Posts(args[0])


    sf = ScrolledFrame(frame, width=640, height=480)
    sf.grid(row=4, column=0, columnspan=3)#, side="top", expand=1, fill="both")

    sf.bind_arrow_keys(frame)
    sf.bind_scroll_wheel(frame)

    #postsFrame = tk.Frame(frame)
    postsFrame = sf.display_widget(tk.Frame)

    for index, encriptedPost in enumerate(posts):
        postFrame = tk.Frame(postsFrame)

        post=json.loads(base64.b64decode(encriptedPost[0]).decode('utf-8'))

        titleLabel = tk.Label(postFrame, text=post['title'])
        titleLabel.config(font=("Arial", 25))
        titleLabel.grid(row=0, column=2, sticky=tk.W)
        print(post.keys())

        if post['postType']=='text':
            textPost = tk.Text(postFrame, width=40, height=10)
            textPost.insert(tk.INSERT, post['text'])
            textPost.config(state=tk.DISABLED)
            textPost.grid(row=1, column=2, sticky=tk.W)


        elif post['postType'] == 'image':

            image_bytes = base64.b64decode(post['file'])
            image = Image.open(io.BytesIO(image_bytes))
            imageSize = image.size
            widthMult = imageSize[0]/200
            #print(imageSize)
            #print(widthMult)


            image = image.resize((200, int(imageSize[1]/widthMult)), Image.LANCZOS)
            img = ImageTk.PhotoImage(image)
            panel = tk.Label(postFrame, image=img)
            panel.image = img
            panel.grid(row=2, column=2, sticky=tk.W)
        postFrame.grid(row=index, column=0, sticky="nw")
    #postsFrame.grid(row=4, column=1)


    return frame

def freeSpin():
    frame = tk.Frame(root)

    backButton = tk.Button(frame, text="Back", command=lambda: goto(main))
    backButton.grid(row=0, column=0)

    canvas = tk.Canvas(frame, width=300, height=300, bg="white")
    canvas.grid(row=1, column=0, columnspan=3)

    # Roulette parameters
    segments = 12
    angle_step = 360 / segments
    colors = ["red", "black"]

    # Draw wheel
    for i in range(segments):
        canvas.create_arc(
            10, 10, 290, 290,
            start=i * angle_step,
            extent=angle_step,
            fill=colors[i % 2],
            outline="white"
        )

    # Pointer (triangle)
    pointer = canvas.create_polygon(
        150, 10, 140, 40, 160, 40,
        fill="gold"
    )

    # Draw circle center
    canvas.create_oval(135,135,165,165,fill="black")

    # Spin animation + result
    def spin():
        total_angle = random.randint(360*4, 360*7)  # 4–7 spins
        step = 15  # degrees per update
        current = 0

        def do_spin():
            nonlocal current
            if current < total_angle:
                current += step
                canvas.delete("pointer_rot")

                # rotate pointer around center
                ang = math.radians(current)
                cx, cy = 150, 150
                px1, py1 = 150, 10   # original coords
                px2, py2 = 140, 40
                px3, py3 = 160, 40

                def rot(x, y):
                    x -= cx
                    y -= cy
                    xr = x*math.cos(ang) - y*math.sin(ang)
                    yr = x*math.sin(ang) + y*math.cos(ang)
                    return xr + cx, yr + cy

                p1 = rot(px1, py1)
                p2 = rot(px2, py2)
                p3 = rot(px3, py3)

                canvas.create_polygon(
                    *p1, *p2, *p3,
                    fill="gold", tag="pointer_rot"
                )

                canvas.after(10, do_spin)
            else:
                # compute result
                final_angle = current % 360
                segment = int((final_angle // angle_step)) % segments
                print("Winning segment:", segment)

        do_spin()

    spinButton = tk.Button(frame, text="Spin", command=spin)
    spinButton.grid(row=2, column=1)

    return frame

onStart()
if checkLogin(USERNAME, PASSWORD)==True:
    main().pack()#expand = True)
else:
    welcome().pack()#expand = True)

#welcome().pack()
#main().pack(anchor=tk.N)
root.geometry("800x600")
root.mainloop()