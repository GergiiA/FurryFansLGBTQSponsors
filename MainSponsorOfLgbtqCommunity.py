import tkinter as tk
from tkinter import messagebox
import requests
import json
import base64

SERVER_URL = "http://127.0.0.1:8080"

'''
def send_data():
    data = {
        "username": entry_username.get(),
        "name": entry_name.get(),
        "password": entry_password.get(),
        "momnum": entry_momnum.get(),
        "razmer": entry_razmer.get(),
        "age": entry_age.get()
    }

    if not all(data.values()):
        messagebox.showerror("error", "each field must be filled in")
        return

    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            messagebox.showinfo("success", "data sent successfully")
        else:
            messagebox.showerror("error", f"The server returned: {response.text}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("error", f"lox: {e}")
#dfghj
'''

USERNAME=None
PASSWORD=None

def onStartup():
    global USERNAME, PASSWORD

    savedData = open('clientData.json', 'r').read()
    data = json.loads(savedData)
    USERNAME = base64.b64decode(data['username']).decode("utf-8")
    PASSWORD = base64.b64decode(data['password']).decode("utf-8")

    loginJson = json.dumps({
        "username": USERNAME,
        "password": PASSWORD
    })
    answer = requests.post(SERVER_URL + '/login', json=loginJson)

    if answer.text == 'True':
        print("login success")
        print('Show main page when it is ready')

    else:
        USERNAME = None
        PASSWORD = None

def writeToFile(username,password):
    savedData = open('clientData.json', 'w')
    usrn=base64.b64encode(username.encode()).decode()
    pw=base64.b64encode(password.encode()).decode()
    jsondata = json.dumps({
        "username": usrn,
        "password": pw
    })
    savedData.write(jsondata)

def requestUserRegistration(entry_username, entry_password, entry_momnum, entry_razmer, entry_pol, root):
    global USERNAME, PASSWORD
    data={
        "username": entry_username.get(),
        "password": entry_password.get(),
        "momnum": entry_momnum.get(),
        "razmer": entry_razmer.get(),
        "pol": entry_pol.get()
    }
    datajson = json.dumps(data)
    print(datajson)

    dataGood=True
    for key, value in data.items():
        if value == '':
            dataGood = False

    if not dataGood:
        messagebox.showerror("error", "data must be filled in")
        return

    answer=requests.post(SERVER_URL+'/createNewUser2', json=datajson)
    if answer.text == 'True':
        USERNAME=entry_username.get()
        PASSWORD=entry_password.get()
        writeToFile(USERNAME,PASSWORD)
        root.quit()
        root.destroy()
        welcome()
    elif answer.text == 'False':
        USERNAME=None
        PASSWORD=None
        messagebox.showerror("error", "user registration failed")

def register_user():
    root = tk.Tk()
    root.title("client reg")

    tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
    entry_username = tk.Entry(root)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=5)
    entry_password = tk.Entry(root, show="*")
    entry_password.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(root, text="Momnum:").grid(row=3, column=0, padx=10, pady=5)
    entry_momnum = tk.Entry(root)
    entry_momnum.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(root, text="Razmer:").grid(row=4, column=0, padx=10, pady=5)
    entry_razmer = tk.Entry(root)
    entry_razmer.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(root, text="Pol:").grid(row=5, column=0, padx=10, pady=5)
    entry_pol = tk.Entry(root)
    entry_pol.grid(row=5, column=1, padx=10, pady=5)

    tk.Button(root, text="Send", command=lambda: requestUserRegistration(entry_username, entry_password, entry_momnum, entry_razmer, entry_pol, root)).grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()

def requestUserLogin(username, password):
    global USERNAME, PASSWORD
    data={
        "username": username,
        "password": password,
    }
    datajson = json.dumps(data)
    print(datajson)


    answer=requests.post(SERVER_URL+'/login', json=datajson)
    if answer.text == 'True':
        USERNAME=username
        PASSWORD=password
        writeToFile(USERNAME,PASSWORD)
    elif answer.text == 'False':
        USERNAME=None
        PASSWORD=None
        messagebox.showerror("error", "user login failed")

def login_user():
    root = tk.Tk()
    root.title("client login")
    tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
    entry_username = tk.Entry(root)
    entry_username.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5)
    entry_password = tk.Entry(root, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    tk.Button(root, text="Send",
              command=lambda: requestUserLogin(entry_username.get(), entry_password.get())).grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()

def welcome():
    root = tk.Tk()
    root.title("welcome")
    tk.Label(root, text="Welcome to FurryFans").grid(row=0, column=0, padx=10, pady=5)

    tk.Button(root, text="Login", command=login_user).grid(row=1, column=0, padx=10, pady=5)

    tk.Button(root, text="Register", command=register_user).grid(row=2, column=0, padx=10, pady=5)

    root.mainloop()


onStartup()

welcome()

#register_user()
#login_user()