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


global MONEY
SERVER_URL = "http://127.0.0.1:5000"
root = tk.Tk()
USERNAME = None
PASSWORD = None
MONEY = 1000


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

    buster = Image.open("img/svinBuster.jpg")
    buster = buster.resize((250, 250), )
    buster = ImageTk.PhotoImage(buster)
    print(buster.width(), buster.height())

    lbl = tk.Label(mainFrame, image=buster)
    lbl.image = buster
    lbl.grid(row=1, column=1, sticky=tk.W)


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

    tk.Label(frame, text="Choose Your Game", font=("Arial", 24, "bold")).pack(pady=20)

    # 1Win Roulette Button
    win1Logo = Image.open('img/1win.png')
    win1Logo = win1Logo.resize((200, 50))
    win1Logo = ImageTk.PhotoImage(win1Logo)
    btn_roulette = tk.Button(frame, image=win1Logo, command=lambda: goto(win1Win))
    btn_roulette.image = win1Logo
    btn_roulette.pack(pady=5)
    tk.Label(frame, text="5x5 Roulette").pack()

    # Slots Button
    btn_slots = tk.Button(frame, text="🎰 SLOTS 🎰", font=("Arial", 16, "bold"), 
                          bg="gold", width=20, command=lambda: goto(game_slots))
    btn_slots.pack(pady=10)

    # Coin Flip Button
    btn_coin = tk.Button(frame, text="🪙 COIN FLIP 🪙", font=("Arial", 16, "bold"), 
                         bg="silver", width=20, command=lambda: goto(game_coin_flip))
    btn_coin.pack(pady=10)

    # Dice Button
    btn_dice = tk.Button(frame, text="🎲 DICE 🎲", font=("Arial", 16, "bold"), 
                         bg="white", width=20, command=lambda: goto(game_dice))
    btn_dice.pack(pady=10)

    tk.Button(frame, text="DEPNUT POCHKU", command=lambda: goto(sellKidney)).pack(pady=10)

    # Back Button
    tk.Button(frame, text="Back to Main", command=lambda: goto(main)).pack(pady=20)


    return frame

def game_slots():
    frame = tk.Frame(root)
    
    tk.Label(frame, text="🎰 SUPER SLOTS 🎰", font=("Arial", 24, "bold"), fg="gold", bg="purple").pack(fill=tk.X, pady=10)
    
    # Money Display
    money_label = tk.Label(frame, text=f"Money: {MONEY}", font=("Arial", 16, "bold"), fg="green")
    money_label.pack(pady=5)

    # Reels
    reels_frame = tk.Frame(frame, bg="black", bd=5, relief="sunken")
    reels_frame.pack(pady=20)
    
    reel_labels = []
    for i in range(3):
        lbl = tk.Label(reels_frame, text="❓", font=("Segoe UI Emoji", 50), width=2, bg="white")
        lbl.grid(row=0, column=i, padx=10, pady=10)
        reel_labels.append(lbl)

    # Bet Controls
    bet_frame = tk.Frame(frame)
    bet_frame.pack(pady=10)
    
    tk.Label(bet_frame, text="Bet Amount:").pack(side=tk.LEFT)
    bet_entry = tk.Entry(bet_frame, width=10)
    bet_entry.insert(0, "50")
    bet_entry.pack(side=tk.LEFT, padx=5)

    def update_money_display():
        money_label.config(text=f"Money: {MONEY}")

    def spin_slots():
        global MONEY
        try:
            bet_amount = int(bet_entry.get())
            if bet_amount <= 0:
                messagebox.showerror("Error", "Bet must be positive!")
                return
            if bet_amount > MONEY:
                messagebox.showerror("Error", "Not enough money!")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid bet amount!")
            return

        MONEY -= bet_amount
        update_money_display()
        spin_btn.config(state=tk.DISABLED)

        symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣", "🍇"]
        # Weights: Cherries/Lemons common, 7s rare
        weights = [30, 30, 20, 10, 5, 5] 
        
        # Animation
        steps = 20
        
        def animate(step):
            global MONEY
            if step < steps:
                # Randomize reels
                for lbl in reel_labels:
                    lbl.config(text=random.choice(symbols))
                frame.after(100, lambda: animate(step+1))
            else:
                # Final Result
                final_symbols = []
                for i in range(3):
                    # Weighted choice
                    sym = random.choices(symbols, weights=weights, k=1)[0]
                    final_symbols.append(sym)
                    reel_labels[i].config(text=sym)
                
                # Check Win
                s1, s2, s3 = final_symbols
                winnings = 0
                
                if s1 == s2 == s3:
                    if s1 == "7️⃣":
                        winnings = bet_amount * 50 # Jackpot
                        messagebox.showinfo("JACKPOT!", f"777 JACKPOT!\nYou won {winnings}!")
                    else:
                        winnings = bet_amount * 10
                        messagebox.showinfo("BIG WIN!", f"Triple {s1}!\nYou won {winnings}!")
                elif s1 == s2 or s2 == s3 or s1 == s3:
                    winnings = bet_amount * 2
                    messagebox.showinfo("WIN!", f"Pair match!\nYou won {winnings}!")
                else:
                    # Loss
                    pass
                
                if winnings > 0:
                    MONEY += winnings
                    update_money_display()
                
                spin_btn.config(state=tk.NORMAL)

        animate(0)

    spin_btn = tk.Button(frame, text="SPIN!", command=spin_slots, font=("Arial", 18, "bold"), bg="gold")
    spin_btn.pack(pady=20)
    
    tk.Button(frame, text="Back", command=lambda: goto(freeSpin)).pack(pady=10)

    return frame

def game_coin_flip():
    global MONEY
    frame = tk.Frame(root)
    
    tk.Label(frame, text="🪙 COIN FLIP 🪙", font=("Arial", 24, "bold"), fg="gold", bg="blue").pack(fill=tk.X, pady=10)
    
    money_label = tk.Label(frame, text=f"Money: {MONEY}", font=("Arial", 16, "bold"), fg="green")
    money_label.pack(pady=5)

    # Coin Display
    coin_label = tk.Label(frame, text="❓", font=("Segoe UI Emoji", 100))
    coin_label.pack(pady=20)

    # Bet Controls
    bet_frame = tk.Frame(frame)
    bet_frame.pack(pady=10)
    
    tk.Label(bet_frame, text="Bet Amount:").pack(side=tk.LEFT)
    bet_entry = tk.Entry(bet_frame, width=10)
    bet_entry.insert(0, "50")
    bet_entry.pack(side=tk.LEFT, padx=5)

    def update_money_display():
        money_label.config(text=f"Money: {MONEY}")

    def flip(choice):
        global MONEY
        try:
            bet_amount = int(bet_entry.get())
            if bet_amount <= 0:
                messagebox.showerror("Error", "Bet must be positive!")
                return
            if bet_amount > MONEY:
                messagebox.showerror("Error", "Not enough money!")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid bet amount!")
            return

        MONEY -= bet_amount
        update_money_display()
        btn_heads.config(state=tk.DISABLED)
        btn_tails.config(state=tk.DISABLED)

        # Animation
        steps = 20
        
        def animate(step):
            global MONEY
            if step < steps:
                coin_label.config(text="🪙" if step % 2 == 0 else "⚪")
                frame.after(50, lambda: animate(step+1))
            else:
                # Result
                result = random.choice(["Heads", "Tails"])
                coin_label.config(text="🦅" if result == "Heads" else "🪙") # Eagle for Heads, Coin for Tails
                
                if choice == result:
                    winnings = bet_amount * 2
                    MONEY += winnings
                    messagebox.showinfo("WON!", f"It's {result}!\nYou won {winnings}!")
                else:
                    messagebox.showinfo("LOST", f"It's {result}.\nYou lost {bet_amount}.")
                
                update_money_display()
                btn_heads.config(state=tk.NORMAL)
                btn_tails.config(state=tk.NORMAL)

        animate(0)

    btn_frame = tk.Frame(frame)
    btn_frame.pack(pady=20)

    btn_heads = tk.Button(btn_frame, text="HEADS (x2)", font=("Arial", 14, "bold"), bg="silver", 
                          command=lambda: flip("Heads"))
    btn_heads.pack(side=tk.LEFT, padx=20)

    btn_tails = tk.Button(btn_frame, text="TAILS (x2)", font=("Arial", 14, "bold"), bg="gold", 
                          command=lambda: flip("Tails"))
    btn_tails.pack(side=tk.LEFT, padx=20)
    
    tk.Button(frame, text="Back", command=lambda: goto(freeSpin)).pack(pady=10)

    return frame

def game_dice():
    global MONEY
    frame = tk.Frame(root)
    
    tk.Label(frame, text="🎲 LUCKY DICE 🎲", font=("Arial", 24, "bold"), fg="white", bg="red").pack(fill=tk.X, pady=10)
    
    money_label = tk.Label(frame, text=f"Money: {MONEY}", font=("Arial", 16, "bold"), fg="green")
    money_label.pack(pady=5)

    # Dice Display
    dice_label = tk.Label(frame, text="🎲", font=("Segoe UI Emoji", 100))
    dice_label.pack(pady=20)

    # Bet Controls
    bet_frame = tk.Frame(frame)
    bet_frame.pack(pady=10)
    
    tk.Label(bet_frame, text="Bet Amount:").pack(side=tk.LEFT)
    bet_entry = tk.Entry(bet_frame, width=10)
    bet_entry.insert(0, "50")
    bet_entry.pack(side=tk.LEFT, padx=5)

    def update_money_display():
        money_label.config(text=f"Money: {MONEY}")

    def roll(bet_type, value=None):
        global MONEY
        try:
            bet_amount = int(bet_entry.get())
            if bet_amount <= 0:
                messagebox.showerror("Error", "Bet must be positive!")
                return
            if bet_amount > MONEY:
                messagebox.showerror("Error", "Not enough money!")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid bet amount!")
            return

        MONEY -= bet_amount
        update_money_display()
        
        # Disable all buttons (simplified)
        # In a real app we'd disable all, here we just rely on the modal dialog blocking interaction mostly

        # Animation
        steps = 20
        
        def animate(step):
            if step < steps:
                dice_label.config(text=str(random.randint(1, 6)))
                frame.after(50, lambda: animate(step+1))
            else:
                # Result
                result = random.randint(1, 6)
                dice_label.config(text=str(result))
                
                won = False
                payout = 0
                
                if bet_type == "number":
                    if result == value:
                        won = True
                        payout = 6
                elif bet_type == "parity":
                    if value == "Odd" and result % 2 != 0:
                        won = True
                        payout = 2
                    elif value == "Even" and result % 2 == 0:
                        won = True
                        payout = 2
                
                if won:
                    global MONEY
                    winnings = bet_amount * payout
                    MONEY += winnings
                    messagebox.showinfo("WON!", f"Rolled {result}!\nYou won {winnings}!")
                else:
                    messagebox.showinfo("LOST", f"Rolled {result}.\nYou lost {bet_amount}.")
                
                update_money_display()

        animate(0)

    # Number Buttons
    num_frame = tk.Frame(frame)
    num_frame.pack(pady=10)
    tk.Label(num_frame, text="Bet on Number (x6):").pack()
    for i in range(1, 7):
        tk.Button(num_frame, text=str(i), width=4, font=("Arial", 12),
                  command=lambda v=i: roll("number", v)).pack(side=tk.LEFT, padx=2)

    # Parity Buttons
    parity_frame = tk.Frame(frame)
    parity_frame.pack(pady=10)
    tk.Label(parity_frame, text="Bet on Parity (x2):").pack()
    tk.Button(parity_frame, text="ODD", width=8, bg="lightblue", command=lambda: roll("parity", "Odd")).pack(side=tk.LEFT, padx=5)
    tk.Button(parity_frame, text="EVEN", width=8, bg="lightpink", command=lambda: roll("parity", "Even")).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame, text="Back", command=lambda: goto(freeSpin)).pack(pady=10)

    return frame

def win1Win():
    frame = tk.Frame(root)
    
    # Header
    win1Logo = Image.open('img/1win.png')
    win1Logo = win1Logo.resize((400, 100))
    win1Logo = ImageTk.PhotoImage(win1Logo)
    win1 = tk.Label(frame, image=win1Logo)
    win1.image = win1Logo
    win1.grid(row=0, column=0, columnspan=5)

    # Money Display
    money_label = tk.Label(frame, text=f"Money: {MONEY}", font=("Arial", 16, "bold"), fg="green")
    money_label.grid(row=1, column=0, columnspan=5)

    # Bet Controls
    bet_frame = tk.Frame(frame)
    bet_frame.grid(row=2, column=0, columnspan=5, pady=5)
    
    tk.Label(bet_frame, text="Bet Amount:").pack(side=tk.LEFT)
    bet_entry = tk.Entry(bet_frame, width=10)
    bet_entry.insert(0, "100")
    bet_entry.pack(side=tk.LEFT, padx=5)

    # 5x5 Grid
    cells = []
    # 0 = Red, 1 = Black (Checkerboard)
    # We will use this for visual style
    
    grid_frame = tk.Frame(frame)
    grid_frame.grid(row=3, column=0, columnspan=5)

    for r in range(5):
        row_cells = []
        for c in range(5):
            cell_val = r * 5 + c + 1
            # Checkerboard pattern
            bg_color = "red" if (r + c) % 2 == 0 else "black"
            fg_color = "white"
            
            lbl = tk.Label(grid_frame, text=str(cell_val), width=6, height=3, 
                           relief="raised", font=("Arial", 12, "bold"),
                           bg=bg_color, fg=fg_color)
            lbl.grid(row=r, column=c, padx=2, pady=2)
            row_cells.append(lbl)
        cells.append(row_cells)

    def update_money_display():
        money_label.config(text=f"Money: {MONEY}")

    def spin(choice):
        global MONEY
        try:
            bet_amount = int(bet_entry.get())
            if bet_amount <= 0:
                messagebox.showerror("Error", "Bet must be positive!")
                return
            if bet_amount > MONEY:
                messagebox.showerror("Error", "Not enough money!")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid bet amount!")
            return

        # Deduct bet
        MONEY -= bet_amount
        update_money_display()
        
        # Disable controls
        btn_red.config(state=tk.DISABLED)
        btn_black.config(state=tk.DISABLED)

        # Animation parameters
        total_steps = 40
        delay = 50
        current_step = 0
        
        def step():
            global MONEY
            nonlocal current_step, delay
            
            # "Spinning Disks" effect: Randomize numbers and colors briefly
            for r in range(5):
                for c in range(5):
                    # Randomize number
                    rand_num = random.randint(1, 99)
                    cells[r][c].config(text=str(rand_num))
                    
                    # Randomize color slightly to simulate motion/blur? 
                    # Or just keep checkerboard but highlight random ones?
                    # Let's just highlight a random cell as the "active" one
            
            # Pick a random cell to highlight
            r_sel = random.randint(0, 4)
            c_sel = random.randint(0, 4)
            
            # Reset all to base colors
            for r in range(5):
                for c in range(5):
                    base_bg = "red" if (r + c) % 2 == 0 else "black"
                    cells[r][c].config(bg=base_bg)
            
            # Highlight selected
            cells[r_sel][c_sel].config(bg="yellow")

            current_step += 1
            
            if current_step < total_steps:
                # Slow down
                if current_step > total_steps - 10:
                    delay += 20
                frame.after(delay, step)
            else:
                # Final Result
                final_r = random.randint(0, 4)
                final_c = random.randint(0, 4)
                
                # Reset colors
                for r in range(5):
                    for c in range(5):
                        base_bg = "red" if (r + c) % 2 == 0 else "black"
                        cells[r][c].config(bg=base_bg)
                
                # Show winner
                winner_color = "red" if (final_r + final_c) % 2 == 0 else "black"
                cells[final_r][final_c].config(bg="green") # Winning cell
                
                won = False
                if choice.lower() == winner_color:
                    won = True
                    winnings = bet_amount * 2
                    MONEY += winnings
                    messagebox.showinfo("WON!", f"You won {winnings}!\nResult: {winner_color.upper()}")
                else:
                    messagebox.showinfo("LOST", f"You lost {bet_amount}.\nResult: {winner_color.upper()}")
                
                update_money_display()
                btn_red.config(state=tk.NORMAL)
                btn_black.config(state=tk.NORMAL)

        step()

    # Bet Buttons
    btn_frame = tk.Frame(frame)
    btn_frame.grid(row=4, column=0, columnspan=5, pady=10)

    btn_red = tk.Button(btn_frame, text="Bet RED (x2)", bg="red", fg="black", 
                        font=("Arial", 12, "bold"), width=15,
                        command=lambda: spin("red"))
    btn_red.pack(side=tk.LEFT, padx=10)

    btn_black = tk.Button(btn_frame, text="Bet BLACK (x2)", bg="black", fg="white", 
                          font=("Arial", 12, "bold"), width=15,
                          command=lambda: spin("black"))
    btn_black.pack(side=tk.LEFT, padx=10)

    return frame

def sellKidney():
    global MONEY

    def addMoney(val):
        global MONEY
        try:
            MONEY += int(val)
        except:
            messagebox.showerror("Error", "Error")
        goto(sellKidney)


    frame=tk.Frame(root)

    backButton = ttk.Button(frame, text="Back", command=lambda: goto(freeSpin))
    backButton.grid(row=0, column=0)

    moneyLabel = ttk.Label(frame, text="Money:"+str(MONEY))
    moneyLabel.grid(row=0, column=1)

    m = tk.Entry(frame)
    m.grid(row=1, column=0)

    b=tk.Button(frame, text="Sell Kidney", command=lambda: addMoney(m.get()))
    b.grid(row=2, column=0)

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