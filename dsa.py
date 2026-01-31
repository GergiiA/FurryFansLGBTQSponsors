import tkinter as tk
from tkinter import messagebox, filedialog
from tkscrolledframe import ScrolledFrame
import requests
import json
import base64
from PIL import Image, ImageTk
import io
import urllib3
import random
import time

urllib3.disable_warnings()

# -------------------- ТЁМНАЯ ТЕМА --------------------
BG_COLOR = "#1e1e1e"
FG_COLOR = "#e0e0e0"
BTN_BG = "#333333"
BTN_FG = "#ffffff"
ENTRY_BG = "#2b2b2b"
ENTRY_FG = "#ffffff"

SERVER_URL = "http://127.0.0.1:5000"
root = tk.Tk()
USERNAME = None
PASSWORD = None

# -------------------- ФУНКЦИИ --------------------
def clear_all_inside_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def goto(func, args=[]):
    clear_all_inside_frame(root)
    func(*args).pack()

def checkLogin(username, password):
    data={'username': username, 'password': password}
    json_data = json.dumps(data)
    answer = requests.post(SERVER_URL+'/login', data=json_data, headers={'Content-Type': 'application/json'}, verify=False)
    if answer.text == 'True':
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
    try:
        file=open('clientData.json', 'r')
    except:
        file=open('clientData.json', 'w')
        file.write(json.dumps({'username': 'Tm9uZQ==', 'password': 'Tm9uZQ==', 'coins':100}))
        file.close()
    file=open('clientData.json', 'r')
    data=json.load(file)
    USERNAME=base64.b64decode(data['username']).decode()
    PASSWORD=base64.b64decode(data['password']).decode()

def saveData(username,password):
    json.dump({'username': base64.b64encode(username.encode('utf-8')).decode(),
               'password': base64.b64encode(password.encode('utf-8')).decode(),
               'coins': getCoins()},
              open('clientData.json', 'w'))

def saveDataWithCoins(username, password, coins):
    json.dump({
        'username': base64.b64encode(username.encode()).decode(),
        'password': base64.b64encode(password.encode()).decode(),
        'coins': coins
    }, open('clientData.json','w'))

def getCoins():
    try:
        data=json.load(open('clientData.json','r'))
        return int(data.get('coins',100))
    except:
        return 100

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
    if filePath.lower().split('.')[-1] not in allowedFiletypes:
        messagebox.showerror("Error", "Incorrect file type")
        return
    image = open(filePath, 'rb').read()
    size= Image.open(filePath).size
    data={'postType': 'image', 'username': USERNAME, 'password': PASSWORD, 'title': title,
          'file': base64.b64encode(image).decode(), 'fileTitle': filePath.split('/')[-1], 'size': size}
    json_data = json.dumps(data)
    response = requests.post(SERVER_URL+'/newPost', data=json_data, headers={'Content-Type': 'application/json'}, verify=False)
    if response.text == 'True':
        messagebox.showinfo("Success", "Posted successfully")
        goto(create2, args=['Text'])
    else:
        messagebox.showerror("Error", "Failed to post")
        goto(create2, args=['Image', response.text])

def makeTextPost(title, text):
    data={'postType': 'text', 'title': title, 'text': text, 'username': USERNAME, 'password': PASSWORD}
    json_data = json.dumps(data)
    answer = requests.post(SERVER_URL+'/newPost', data=json_data, headers={'Content-Type': 'application/json'}, verify=False)
    if answer.text == 'True':
        messagebox.showinfo("Success", "Posted successfully")
        goto(create2, ['Text'])

def logout():
    saveData('None', 'None')
    goto(welcome)

def getSubscribes():
    data={'username': USERNAME, 'password': PASSWORD}
    answer = requests.get(SERVER_URL+'/getSubscribes', json=data ,headers={'Content-Type': 'application/json'}, verify=False)
    if answer.text != 'invalid credentials':
        subscribes=json.loads(answer.text)
        return subscribes
    else:
        return []

def requestSearch(prompt):
    data=json.dumps({'search': prompt})
    answer = requests.post(SERVER_URL+'/searchUsers', data=data, headers={'Content-Type': 'application/json'}, verify=False)
    return json.loads(answer.text)

def getDataAboutOtherUser(username):
    data=json.dumps({'username': username, 'selfUsername': USERNAME, 'selfPassword': PASSWORD})
    answer = requests.get(SERVER_URL+'/getPublicUserData', json=data, headers={'Content-Type': 'application/json'}, verify=False)
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
    answer = requests.get(SERVER_URL+'/getLast10Posts', json=data, headers={'Content-Type': 'application/json'}, verify=False)
    json_data = json.loads(answer.text)
    return json_data

# -------------------- FREE BET --------------------
def open_slot_machine():
    slot = tk.Toplevel(root)
    slot.title("Free Bet Slot Machine")
    slot.geometry("500x350")
    slot.resizable(False, False)
    slot.config(bg=BG_COLOR)

    coins_var = tk.IntVar(value=getCoins())
    tk.Label(slot, text="Монеты:", bg=BG_COLOR, fg=FG_COLOR, font=("Arial",14)).pack()
    coins_label = tk.Label(slot, textvariable=coins_var, bg=BG_COLOR, fg=FG_COLOR, font=("Arial",16))
    coins_label.pack(pady=5)

    symbols = ["🍒", "⭐", "7", "🍋", "💎", "🔔", "🍇", "🍉"]
    reels_frame = tk.Frame(slot, bg=BG_COLOR)
    reels_frame.pack(pady=10)
    reel_vars = [tk.StringVar(value=random.choice(symbols)) for _ in range(3)]
    for i, rv in enumerate(reel_vars):
        lbl = tk.Label(reels_frame, textvariable=rv, font=("Arial",48), width=2, bg=BG_COLOR, fg=FG_COLOR)
        lbl.grid(row=0,column=i,padx=10)

    info_var = tk.StringVar(value="Нажми SPIN чтобы крутить")
    tk.Label(slot, textvariable=info_var, bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)

    controls_frame = tk.Frame(slot, bg=BG_COLOR)
    controls_frame.pack(pady=8)
    spin_btn = tk.Button(controls_frame, text="SPIN (10 монет)", font=("Arial",18), bg=BTN_BG, fg=BTN_FG)
    spin_btn.grid(row=0,column=0,padx=5)
    stop_btn = tk.Button(controls_frame, text="STOP", font=("Arial",12), bg=BTN_BG, fg=BTN_FG)
    stop_btn.grid(row=0,column=1,padx=5)

    state = {"spinning": False, "start_time": None, "delays": [50]*3, "stop_times": [0]*3, "after_ids": [None]*3}

    def set_final_results():
        finals = [reel_vars[i].get() for i in range(3)]
        if finals[0] == finals[1] == finals[2]:
            won = 50
            info_var.set(f"WIN! {finals[0]*3} +{won} монет!")
        elif finals[0]==finals[1] or finals[1]==finals[2] or finals[0]==finals[2]:
            won = 20
            info_var.set(f"Победа! +{won} монет!")
        else:
            won = 0
            info_var.set("Нет выигрыша. Попробуй ещё.")
        coins_var.set(coins_var.get() + won)
        saveDataWithCoins(USERNAME, PASSWORD, coins_var.get())
        state['spinning']=False
        spin_btn.config(state=tk.NORMAL)

    def animate_reel(i):
        if not state['spinning']: return
        now = time.time()
        if now >= state['stop_times'][i]:
            state['after_ids'][i]=None
            if all(time.time()>=st for st in state['stop_times']):
                slot.after(200,set_final_results)
            return
        reel_vars[i].set(random.choice(symbols))
        state['delays'][i] = min(state['delays'][i]+10, 250)
        state['after_ids'][i] = slot.after(state['delays'][i], lambda idx=i: animate_reel(idx))

    def start_spin():
        if state['spinning']: return
        if coins_var.get() < 10:
            messagebox.showinfo("Недостаточно монет", "У вас недостаточно монет для спина!")
            return
        coins_var.set(coins_var.get()-10)
        saveDataWithCoins(USERNAME, PASSWORD, coins_var.get())
        state['spinning'] = True
        state['start_time'] = time.time()
        info_var.set("Крутится...")
        spin_btn.config(state=tk.DISABLED)
        base = state['start_time']
        durations = [1.0, 1.6, 2.2]
        state['stop_times'] = [base+d for d in durations]
        state['delays'] = [30]*3
        for i in range(3):
            if state['after_ids'][i]:
                try: slot.after_cancel(state['after_ids'][i])
                except: pass
                state['after_ids'][i] = None
            animate_reel(i)

    def stop_all_immediately():
        if not state['spinning']: return
        now = time.time()
        state['stop_times'] = [now]*3

    spin_btn.config(command=start_spin)
    stop_btn.config(command=stop_all_immediately)

# -------------------- GUI ФУНКЦИИ --------------------
def welcome():
    frame1 = tk.Frame(root, bg=BG_COLOR)
    label = tk.Label(frame1, text="Welcome to FurryFans", bg=BG_COLOR, fg=FG_COLOR)
    label.grid(row=0, column=0)
    loginButton = tk.Button(frame1, text="Login", command=lambda: goto(login), bg=BTN_BG, fg=BTN_FG)
    loginButton.grid(row=1, column=0)
    registerButton = tk.Button(frame1, text="Register", command=lambda: goto(register), bg=BTN_BG, fg=BTN_FG)
    registerButton.grid(row=2, column=0)
    return frame1

def login(*args):
    frame=tk.Frame(root, bg=BG_COLOR)
    backButton = tk.Button(frame, text="Back", command=lambda: goto(welcome), bg=BTN_BG, fg=BTN_FG)
    backButton.grid(row=0, column=0)
    usernameLabel = tk.Label(frame, text="Username", bg=BG_COLOR, fg=FG_COLOR)
    usernameLabel.grid(row=1, column=0)
    usernameEntry = tk.Entry(frame, width=40, bg=ENTRY_BG, fg=ENTRY_FG)
    usernameEntry.grid(row=1, column=1)
    passwordLabel = tk.Label(frame, text="Password", bg=BG_COLOR, fg=FG_COLOR)
    passwordLabel.grid(row=2, column=0)
    passwordEntry = tk.Entry(frame, width=40, bg=ENTRY_BG, fg=ENTRY_FG)
    passwordEntry.grid(row=2, column=1)
    errorLabel = tk.Label(frame, text=args[0] if len(args) else "", bg=BG_COLOR, fg="red")
    errorLabel.grid(row=3, column=0)
    submitButton = tk.Button(frame, text="Login",
                             command=lambda: checkLoginWrap(usernameEntry.get(), passwordEntry.get()),
                             bg=BTN_BG, fg=BTN_FG)
    submitButton.grid(row=3, column=1)
    return frame

def register(*args):
    frame = tk.Frame(root, bg=BG_COLOR)
    backButton = tk.Button(frame, text="Back", command=lambda: goto(welcome), bg=BTN_BG, fg=BTN_FG)
    backButton.grid(row=0, column=0)
    usernameLabel = tk.Label(frame, text="Username", bg=BG_COLOR, fg=FG_COLOR)
    usernameLabel.grid(row=1, column=0)
    usernameEntry = tk.Entry(frame, width=40, bg=ENTRY_BG, fg=ENTRY_FG)
    usernameEntry.grid(row=1, column=1)
    passwordLabel = tk.Label(frame, text="Password", bg=BG_COLOR, fg=FG_COLOR)
    passwordLabel.grid(row=2, column=0)
    passwordEntry = tk.Entry(frame, width=40, bg=ENTRY_BG, fg=ENTRY_FG)
    passwordEntry.grid(row=2, column=1)
    polLabel = tk.Label(frame, text="Pol", bg=BG_COLOR, fg=FG_COLOR)
    polLabel.grid(row=3, column=0)
    polEntry = tk.Entry(frame, width=40, bg=ENTRY_BG, fg=ENTRY_FG)
    polEntry.grid(row=3, column=1)
    nomerMamiLabel = tk.Label(frame, text="Nomer Mami", bg=BG_COLOR, fg=FG_COLOR)
    nomerMamiLabel.grid(row=4, column=0)
    nomerMamiEntry = tk.Entry(frame, width=40, bg=ENTRY_BG, fg=ENTRY_FG)
    nomerMamiEntry.grid(row=4, column=1)
    razmerLabel = tk.Label(frame, text="Razmer", bg=BG_COLOR, fg=FG_COLOR)
    razmerLabel.grid(row=5, column=0)
    razmerEntry = tk.Entry(frame, width=40, bg=ENTRY_BG, fg=ENTRY_FG)
    razmerEntry.grid(row=5, column=1)
    errorLabel = tk.Label(frame, text=args[0] if len(args) == 1 else "", bg=BG_COLOR, fg="red")
    errorLabel.grid(row=6, column=0)
    submitButton = tk.Button(frame, text="Register", command=lambda: createNewUserWrap(
        usernameEntry.get(), passwordEntry.get(), polEntry.get(), nomerMamiEntry.get(), razmerEntry.get()),
                             bg=BTN_BG, fg=BTN_FG)
    submitButton.grid(row=6, column=1)
    return frame

def main():
    mainFrame = tk.Frame(root, bg=BG_COLOR)
    tk.Label(mainFrame, text="FurryFans", bg=BG_COLOR, fg=FG_COLOR, font=("Arial",18)).grid(row=0, column=0)
    tk.Label(mainFrame, text="Welcome back, "+str(USERNAME), bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0)
    tk.Button(mainFrame, text="Make post", command=lambda: goto(create2, ['Text']), bg=BTN_BG, fg=BTN_FG).grid(row=2, column=0)
    tk.Button(mainFrame, text="Subscribes", command=lambda: goto(subscribes), bg=BTN_BG, fg=BTN_FG).grid(row=3, column=0)
    tk.Button(mainFrame, text="Account", command=lambda: goto(account), bg=BTN_BG, fg=BTN_FG).grid(row=4, column=0)
    tk.Button(mainFrame, text="Search", command=lambda: goto(search), bg=BTN_BG, fg=BTN_FG).grid(row=5, column=0)
    tk.Button(mainFrame, text="Free Bet 🎰", command=open_slot_machine, bg=BTN_BG, fg=BTN_FG).grid(row=6, column=0)
    return mainFrame

onStart()
if checkLogin(USERNAME, PASSWORD)==True:
    main().pack()
else:
    welcome().pack()

root.geometry ("800x600")
