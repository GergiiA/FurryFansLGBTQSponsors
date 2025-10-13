import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import json
import base64


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

    answer = requests.post(SERVER_URL+'/login', data=json_data, headers={'Content-Type': 'application/json'})

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


    answer = requests.post(SERVER_URL+'/createNewUser2', data=json_data, headers={'Content-Type': 'application/json'})

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
    if len(file.read())==0:#if file is empty write none to it
        #file = open('clientData.json', 'w')
        #file.write(json.dumps({'username': 'Tm9uZQ==', 'password': 'Tm9uZQ=='}))
        #file.close()
        saveData('Tm9uZQ==', 'Tm9uZQ==')

    file = open('clientData.json', 'r')
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
    goto(create, args=[filePath])

def makePost(filePath, title):
    if filePath is None:
        messagebox.showerror("Error", "Please select a file")
        return
    allowedFiletypes=['.png', '.jpg', 'jpeg']
    if filePath.lower().split('.')[-1] not in allowedFiletypes:
        messagebox.showerror("Error", "Incorrect file type")
        return
    image = open(filePath, 'rb').read()

    data={'username': USERNAME, 'password': PASSWORD, 'title': title, 'file': base64.b64encode(image).decode(), 'fileTitle': filePath.split('/')[-1]}
    json_data = json.dumps(data)
    #print(json_data)
    response = requests.post(SERVER_URL+'/newPost', data=json_data, headers={'Content-Type': 'application/json'})
    if response.text == 'True':
        messagebox.showinfo("Success", "Posted successfully")
        goto(create)
    else:
        messagebox.showerror("Error", "Failed to post")
        goto(create, args=['', response.text])

def logout():
    saveData('None', 'None')
    goto(welcome)

def getSubscribes():
    data={'username': USERNAME, 'password': PASSWORD}
    answer = requests.get(SERVER_URL+'/getSubscribes', json=data ,headers={'Content-Type': 'application/json'})
    #print(answer.text)
    if answer.text != 'invalid credentials':
        subscribes=json.loads(answer.text)
        return subscribes

    else:
        return []

def getUsers():
    answer=requests.get(SERVER_URL+'/getUsers')#, headers={'Content-Type': 'application/json'})

def requestSearch(prompt):
    data=json.dumps({'search': prompt})

    answer = requests.post(SERVER_URL+'/searchUsers', data=data, headers={'Content-Type': 'application/json'})
    print(answer.text)
    return json.loads(answer.text)

def getDataAboutOtherUser(username):
    data={'username': username}
    answer = requests.get(SERVER_URL+'/getPublicUserData', json=data, headers={'Content-Type': 'application/json'})
    print(answer.text)
    return json.loads(answer.text)

#tkinter windows
def welcome():
    frame1 = tk.Frame(root)

    label = tk.Label(frame1, text="Welcome to FurryFans")
    label.grid(row=0, column=0)

    loginButton = tk.Button(frame1, text="Login", command=lambda: goto(login))
    loginButton.grid(row=1, column=0)

    registerButton = tk.Button(frame1, text="Register", command=lambda: goto(register))
    registerButton.grid(row=2, column=0)

    return frame1

def login(*args):
    frame=tk.Frame(root)

    backButton = tk.Button(frame, text="Back", command=lambda: goto(welcome))
    backButton.grid(row=0, column=0)

    login = tk.Label(frame, text="Login")
    login.grid(row=0, column=1)

    usernameLabel = tk.Label(frame, text="Username")
    usernameLabel.grid(row=1, column=0)

    usernameEntry = tk.Entry(frame, width=40)
    usernameEntry.grid(row=1, column=1)

    passwordLabel = tk.Label(frame, text="Password")
    passwordLabel.grid(row=2, column=0)

    passwordEntry = tk.Entry(frame, width=40)
    passwordEntry.grid(row=2, column=1)

    errorLabel = tk.Label(frame, text=args[0] if len(args) else "")
    errorLabel.grid(row=3, column=0)

    submitButton = tk.Button(frame, text="Login", command=lambda: checkLoginWrap(usernameEntry.get(), passwordEntry.get()))
    submitButton.grid(row=4, column=0)
    submitButton.grid(row=3, column=1)

    return frame

def register(*args):
    frame = tk.Frame(root)

    backButton = tk.Button(frame, text="Back", command=lambda: goto(welcome))
    backButton.grid(row=0, column=0)

    registerLabel = tk.Label(frame, text="Register")
    registerLabel.grid(row=0, column=1)

    usernameLabel = tk.Label(frame, text="Username")
    usernameLabel.grid(row=1, column=0)

    usernameEntry = tk.Entry(frame, width=40)
    usernameEntry.grid(row=1, column=1)

    passwordLabel = tk.Label(frame, text="Password")
    passwordLabel.grid(row=2, column=0)

    passwordEntry = tk.Entry(frame, width=40)
    passwordEntry.grid(row=2, column=1)

    polLabel = tk.Label(frame, text="Pol")
    polLabel.grid(row=3, column=0)

    polEntry = tk.Entry(frame, width=40)
    polEntry.grid(row=3, column=1)

    nomerMamiLabel = tk.Label(frame, text="Nomer Mami")
    nomerMamiLabel.grid(row=4, column=0)

    nomerMamiEntry = tk.Entry(frame, width=40)
    nomerMamiEntry.grid(row=4, column=1)

    razmerLabel = tk.Label(frame, text="Razmer")
    razmerLabel.grid(row=5, column=0)

    razmerEntry = tk.Entry(frame, width=40)
    razmerEntry.grid(row=5, column=1)

    errorLabel = tk.Label(frame, text=args[0] if len(args) == 1 else "")
    errorLabel.grid(row=6, column=0)

    submitButton = tk.Button(frame, text="Register", command=lambda: createNewUserWrap(
        usernameEntry.get(), passwordEntry.get(), polEntry.get(), nomerMamiEntry.get(), razmerEntry.get()))
    submitButton.grid(row=6, column=1)

    return frame

def main():
    if not checkLogin(USERNAME, PASSWORD):
        #goto(login)
        #return tk.Frame(root)
        pass
    mainFrame = tk.Frame(root)

    furryFansLabel = tk.Label(mainFrame, text="FurryFans")
    furryFansLabel.grid(row=0, column=0)

    welcomeBackText = tk.Label(mainFrame, text="Welcome back, "+str(USERNAME))
    welcomeBackText.grid(row=1, column=0)

    createButton=tk.Button(mainFrame, text="Make post", command=lambda: goto(create))
    createButton.grid(row=2, column=0)

    subscribesButton=tk.Button(mainFrame, text="Subscribes", command=lambda: goto(subscribes))
    subscribesButton.grid(row=3, column=0)

    accountButton = tk.Button(mainFrame, text="account", command=lambda: goto(account))
    accountButton.grid(row=4, column=0)

    searchButton = tk.Button(mainFrame, text="Search", command=lambda: goto(search))
    searchButton.grid(row=5, column=0)


    return mainFrame

def create(*args):
    frame = tk.Frame(root)

    backButton = tk.Button(frame, text="Back", command=lambda: goto(main))
    backButton.grid(row=0, column=0)

    filePathLabel = tk.Label(frame, text="File path: "+args[0] if len(args) >0 else "")
    filePathLabel.grid(row=0, column=2)

    titleLabel = tk.Label(frame, text="Title: ")
    titleLabel.grid(row=1, column=0)

    titleInput = tk.Entry(frame, width=40)
    titleInput.grid(row=1, column=1)


    selectFileButton = tk.Button(frame, text="upload file", command=lambda: selectFileWrap())
    selectFileButton.grid(row=0, column=1)

    errorLabel = tk.Label(frame, text=args[1] if len(args) >1 else "")
    errorLabel.grid(row=2, column=0)

    uploadButton = tk.Button(frame, text="Make post", command=lambda: makePost(args[0] if len(args) >0 else None, titleInput.get()))
    uploadButton.grid(row=2, column=1)



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
    for index, sub in enumerate(subs):
        a=tk.Button(frame, command=lambda: goto(viewSomeone(sub)))
        a.grid(row=index, column=1)
    if len(subs)==0:
        lbl=tk.Label(frame, text="No subscribes")
        lbl.grid(row=0, column=1)


    return frame

def search(*args):
    frame = tk.Frame(root)

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
            command=lambda res=result: goto(viewSomeone, [res[1], args[0], inputString.get()])
        ).grid(row=i + 1, column=1)
        #print(result)

    return frame

def viewSomeone(*args):
    if len(args) == 0:
        goto(main)
    #print('args', args)

    frame = tk.Frame(root)
    data=getDataAboutOtherUser(args[0])

    backButton = tk.Button(frame, text="Back", command=lambda: goto(search, [args[1], args[2],]))
    backButton.grid(row=0, column=0)

    usernameLabel = tk.Label(frame, text="Username: "+args[0])
    usernameLabel.grid(row=0, column=1)

    polLabel = tk.Label(frame, text="Pol: "+data[0][0])
    polLabel.grid(row=1, column=1)

    nomerMamiLabel = tk.Label(frame, text="NomerMami: "+data[0][1])
    nomerMamiLabel.grid(row=2, column=1)

    razmerLabel = tk.Label(frame, text="Razmer: "+data[0][2])
    razmerLabel.grid(row=3, column=1)



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