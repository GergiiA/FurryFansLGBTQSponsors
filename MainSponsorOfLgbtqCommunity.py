import tkinter as tk
from tkinter import messagebox
import requests

SERVER_URL = "http://192.168.199.59:8080"


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

root = tk.Tk()
root.title("client reg")

tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Name:").grid(row=1, column=0, padx=10, pady=5)
entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Momnum:").grid(row=3, column=0, padx=10, pady=5)
entry_momnum = tk.Entry(root)
entry_momnum.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Razmer:").grid(row=4, column=0, padx=10, pady=5)
entry_razmer = tk.Entry(root)
entry_razmer.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Age:").grid(row=5, column=0, padx=10, pady=5)
entry_age = tk.Entry(root)
entry_age.grid(row=5, column=1, padx=10, pady=5)

tk.Button(root, text="Send", command=send_data).grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()
