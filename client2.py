import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import requests
import base64
from PIL import Image, ImageTk
import io
import urllib3

urllib3.disable_warnings()
SERVER_URL = "http://127.0.0.1:5000"

# -------------------------------------------------------------
# Helper: Threaded network call
# -------------------------------------------------------------
def run_in_thread(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper

# -------------------------------------------------------------
# Root window setup
# -------------------------------------------------------------
root = tk.Tk()
root.title("FurryFans Client")
root.geometry("900x650")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=6, font=("Segoe UI", 11))
style.configure("TLabel", padding=4, font=("Segoe UI", 11))
style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))

USERNAME = None
PASSWORD = None

# -------------------------------------------------------------
# Utility UI
# -------------------------------------------------------------
def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()

def show_frame(builder, *args):
    clear_frame(main_area)
    frame = builder(*args)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

def loading_screen(text="Loading..."):
    frm = ttk.Frame(main_area)
    ttk.Label(frm, text=text, style="Header.TLabel").pack(pady=20)
    pb = ttk.Progressbar(frm, mode="indeterminate")
    pb.pack(pady=10)
    pb.start()
    return frm

# -------------------------------------------------------------
# Networking
# -------------------------------------------------------------
def api_post(endpoint, data):
    try:
        return requests.post(
            SERVER_URL + endpoint,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            verify=False
        )
    except:
        return None

def api_get(endpoint, data=None):
    try:
        return requests.get(
            SERVER_URL + endpoint,
            json=data,
            headers={'Content-Type': 'application/json'},
            verify=False
        )
    except:
        return None

# -------------------------------------------------------------
# Login state persistence
# -------------------------------------------------------------
def load_saved_data():
    global USERNAME, PASSWORD
    try:
        with open("clientData.json", "r") as f:
            d = json.load(f)
            USERNAME = base64.b64decode(d["username"]).decode()
            PASSWORD = base64.b64decode(d["password"]).decode()
    except:
        USERNAME = "None"
        PASSWORD = "None"

def save_login(u, p):
    with open("clientData.json", "w") as f:
        json.dump({
            "username": base64.b64encode(u.encode()).decode(),
            "password": base64.b64encode(p.encode()).decode()
        }, f)

# -------------------------------------------------------------
# Screens
# -------------------------------------------------------------
def welcome():
    frm = ttk.Frame(main_area)

    ttk.Label(frm, text="FurryFans", style="Header.TLabel").pack(pady=10)
    ttk.Button(frm, text="Login", command=lambda: show_frame(login)).pack(pady=5)
    ttk.Button(frm, text="Register", command=lambda: show_frame(register)).pack(pady=5)

    return frm


def login(error_text=""):
    frm = ttk.Frame(main_area)

    ttk.Label(frm, text="Login", style="Header.TLabel").grid(row=0, column=1, pady=10)

    ttk.Label(frm, text="Username").grid(row=1, column=0)
    username = ttk.Entry(frm, width=40)
    username.grid(row=1, column=1)

    ttk.Label(frm, text="Password").grid(row=2, column=0)
    password = ttk.Entry(frm, width=40, show="*")
    password.grid(row=2, column=1)

    ttk.Label(frm, text=error_text, foreground="red").grid(row=3, column=0, columnspan=2)

    @run_in_thread
    def attempt():
        show_frame(lambda: loading_screen("Checking login..."))
        r = api_post("/login", {"username": username.get(), "password": password.get()})
        if r and r.text == "True":
            global USERNAME, PASSWORD
            USERNAME = username.get()
            PASSWORD = password.get()
            save_login(USERNAME, PASSWORD)
            show_frame(main)
        else:
            show_frame(login, "Invalid login")

    ttk.Button(frm, text="Submit", command=attempt).grid(row=4, column=1, pady=10)
    ttk.Button(frm, text="Back", command=lambda: show_frame(welcome)).grid(row=4, column=0)

    return frm


def register(error_text=""):
    frm = ttk.Frame(main_area)

    ttk.Label(frm, text="Register", style="Header.TLabel").grid(row=0, column=1, pady=10)

    fields = ["Username", "Password", "Pol", "Nomer Mami", "Razmer"]
    entries = {}

    for i, f in enumerate(fields):
        ttk.Label(frm, text=f).grid(row=i+1, column=0)
        e = ttk.Entry(frm, width=40)
        e.grid(row=i+1, column=1)
        entries[f] = e

    ttk.Label(frm, text=error_text, foreground="red").grid(row=7, column=0, columnspan=2)

    @run_in_thread
    def attempt():
        show_frame(lambda: loading_screen("Creating account..."))
        data = {
            "username": entries["Username"].get(),
            "password": entries["Password"].get(),
            "pol": entries["Pol"].get(),
            "momnum": entries["Nomer Mami"].get(),
            "razmer": entries["Razmer"].get()
        }
        r = api_post("/createNewUser2", data)

        if r and r.text == "True":
            show_frame(main)
        else:
            show_frame(register, r.text if r else "Connection error")

    ttk.Button(frm, text="Submit", command=attempt).grid(row=8, column=1, pady=10)
    ttk.Button(frm, text="Back", command=lambda: show_frame(welcome)).grid(row=8, column=0)

    return frm


def main():
    frm = ttk.Frame(main_area)

    ttk.Label(frm, text=f"Welcome back, {USERNAME}", style="Header.TLabel").pack(pady=10)

    ttk.Button(frm, text="Make Post", width=30, command=lambda: show_frame(create_post, "Text", None)).pack(pady=5)
    ttk.Button(frm, text="Subscribes", width=30, command=lambda: show_frame(subscribes)).pack(pady=5)
    ttk.Button(frm, text="Search", width=30, command=lambda: show_frame(search)).pack(pady=5)
    ttk.Button(frm, text="Account", width=30, command=lambda: show_frame(account)).pack(pady=5)

    return frm


def account():
    frm = ttk.Frame(main_area)
    ttk.Label(frm, text=f"Name: {USERNAME}", style="Header.TLabel").pack(pady=10)
    ttk.Button(frm, text="Logout", command=lambda: (save_login("None", "None"), show_frame(welcome))).pack()
    ttk.Button(frm, text="Back", command=lambda: show_frame(main)).pack(pady=10)
    return frm

# -------------------------------------------------------------
# Create post
# -------------------------------------------------------------
def create_post(post_type, image_path):
    frm = ttk.Frame(main_area)

    ttk.Button(frm, text="Back", command=lambda: show_frame(main)).grid(row=0, column=0, pady=10)

    ttk.Button(frm, text="Text Post", command=lambda: show_frame(create_post, "Text", None)).grid(row=1, column=0)
    ttk.Button(frm, text="Image Post", command=lambda: show_frame(create_post, "Image", image_path)).grid(row=1, column=1)

    # TEXT POST
    if post_type == "Text":
        ttk.Label(frm, text="Title").grid(row=2, column=0)
        title = ttk.Entry(frm, width=40)
        title.grid(row=2, column=1)

        ttk.Label(frm, text="Text").grid(row=3, column=0)
        text = ttk.Entry(frm, width=40)
        text.grid(row=3, column=1)

        @run_in_thread
        def send_text():
            show_frame(lambda: loading_screen("Uploading..."))
            r = api_post("/newPost", {
                "postType": "text",
                "title": title.get(),
                "text": text.get(),
                "username": USERNAME,
                "password": PASSWORD
            })
            if r and r.text == "True":
                messagebox.showinfo("OK", "Posted!")
                show_frame(create_post, "Text", None)
            else:
                messagebox.showerror("Error", "Failed")

        ttk.Button(frm, text="Upload", command=send_text).grid(row=4, column=1, pady=10)

    # IMAGE POST
    else:
        ttk.Label(frm, text=f"File: {image_path if image_path else ''}").grid(row=2, column=0)

        def select():
            fp = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if fp:
                show_frame(create_post, "Image", fp)

        ttk.Button(frm, text="Select File", command=select).grid(row=2, column=1)

        ttk.Label(frm, text="Title").grid(row=3, column=0)
        title = ttk.Entry(frm, width=40)
        title.grid(row=3, column=1)

        @run_in_thread
        def send_image():
            if not image_path:
                messagebox.showerror("Error", "Choose file")
                return

            show_frame(lambda: loading_screen("Uploading image..."))

            img_bytes = open(image_path, "rb").read()
            payload = {
                "postType": "image",
                "file": base64.b64encode(img_bytes).decode(),
                "fileTitle": image_path.split("/")[-1],
                "username": USERNAME,
                "password": PASSWORD,
                "title": title.get(),
                "size": Image.open(image_path).size
            }

            r = api_post("/newPost", payload)

            if r and r.text == "True":
                messagebox.showinfo("OK", "Posted!")
                show_frame(create_post, "Text", None)
            else:
                messagebox.showerror("Error", "Failed to post")

        ttk.Button(frm, text="Upload", command=send_image).grid(row=4, column=1, pady=10)

    return frm


# -------------------------------------------------------------
# Subscribes list (non-freezing)
# -------------------------------------------------------------
def subscribes():
    frm = loading_screen("Loading subscribes...")

    @run_in_thread
    def load():
        r = api_get("/getSubscribes", {"username": USERNAME, "password": PASSWORD})
        data = json.loads(r.text) if r else []

        def show():
            show_frame(subscribes_display, data)
        root.after(0, show)

    load()
    return frm


def subscribes_display(subs):
    frm = ttk.Frame(main_area)
    ttk.Button(frm, text="Back", command=lambda: show_frame(main)).pack(pady=5)

    if not subs:
        ttk.Label(frm, text="No subscriptions").pack()
        return frm

    for s in subs:
        ttk.Button(frm, text=s, command=lambda u=s: show_frame(view_user, u)).pack(pady=4, anchor="w")

    return frm

# -------------------------------------------------------------
# Search
# -------------------------------------------------------------
def search(prev_results=None):
    frm = ttk.Frame(main_area)

    ttk.Button(frm, text="Back", command=lambda: show_frame(main)).grid(row=0, column=0)

    entry = ttk.Entry(frm, width=40)
    entry.grid(row=0, column=1)

    @run_in_thread
    def do_search():
        show_frame(lambda: loading_screen("Searching..."))
        q = entry.get()
        r = api_post("/searchUsers", {"search": q})
        if r:
            show_frame(search_results, json.loads(r.text), q)

    ttk.Button(frm, text="Search", command=do_search).grid(row=0, column=2)

    return frm


def search_results(results, query):
    frm = ttk.Frame(main_area)
    ttk.Button(frm, text="Back", command=lambda: show_frame(search)).pack()

    for r in results:
        ttk.Button(frm, text=r[1], command=lambda u=r[1]: show_frame(view_user, u)).pack(anchor="w")

    return frm

# -------------------------------------------------------------
# View user (non-freezing)
# -------------------------------------------------------------
def view_user(username):
    frm = loading_screen("Loading user...")

    @run_in_thread
    def load():
        r = api_get("/getPublicUserData", {"username": username, "selfUsername": USERNAME, "selfPassword": PASSWORD})
        posts = api_get("/getLast10Posts", {"username": username, "page": 0})
        if not r or not posts:
            return

        data = json.loads(r.text)
        posts = [json.loads(base64.b64decode(p[0])) for p in json.loads(posts.text)]

        def show():
            show_frame(view_user_display, username, data, posts)
        root.after(0, show)

    load()
    return frm


def view_user_display(username, info, posts):
    frm = ttk.Frame(main_area)

    ttk.Button(frm, text="Back", command=lambda: show_frame(main)).pack()

    ttk.Label(frm, text=username, style="Header.TLabel").pack()

    ttk.Label(frm, text=f"Subscribers: {info[2]}").pack()
    ttk.Label(frm, text=f"Pol: {info[0][0]}").pack()
    ttk.Label(frm, text=f"Nomer Mami: {info[0][1]}").pack()
    ttk.Label(frm, text=f"Razmer: {info[0][2]}").pack()

    can = tk.Canvas(frm)
    can.pack(fill="both", expand=True)
    vs = ttk.Scrollbar(frm, orient="vertical", command=can.yview)
    vs.pack(side="right", fill="y")
    can.configure(yscrollcommand=vs.set)

    posts_frame = ttk.Frame(can)
    can.create_window((0, 0), window=posts_frame, anchor="nw")

    def conf(e):
        can.configure(scrollregion=can.bbox("all"))
    posts_frame.bind("<Configure>", conf)

    for p in posts:
        box = ttk.LabelFrame(posts_frame, text=p["title"], padding=10)
        box.pack(fill="x", pady=10)

        if p["postType"] == "text":
            ttk.Label(box, text=p["text"]).pack(anchor="w")
        else:
            img = Image.open(io.BytesIO(base64.b64decode(p["file"])))
            w, h = img.size
            scale = w / 250
            img = img.resize((250, int(h / scale)))
            img_tk = ImageTk.PhotoImage(img)
            lbl = ttk.Label(box, image=img_tk)
            lbl.image = img_tk
            lbl.pack(anchor="w")

    return frm

# -------------------------------------------------------------
# Start
# -------------------------------------------------------------
main_area = ttk.Frame(root)
main_area.pack(fill="both", expand=True)

load_saved_data()

if USERNAME != "None" and api_post("/login", {"username": USERNAME, "password": PASSWORD}).text == "True":
    show_frame(main)
else:
    show_frame(welcome)

root.mainloop()
