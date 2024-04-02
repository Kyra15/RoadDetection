# imports all necessary libraries
import sqlite3
from cryptography.fernet import Fernet
import datetime
from tkinter import messagebox

# open file that contains the encryption and decryption key
with open("fernet_key.key", "rb") as key_file:
    key = key_file.read()
fernet = Fernet(key)

tdytime = datetime.datetime.now()
tdy = tdytime.strftime("%x")
timet = tdytime.strftime("%X")

# connect to SQL database
conn = sqlite3.connect('tank_database')
c = conn.cursor()


# creates a new table, if one doe not already exist, that has #parameters user id, username, password, first name, and last name
def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS tank_database 
    ([user_id] INTEGER PRIMARY KEY AUTOINCREMENT, 
    [username] TEXT,
    [password] TEXT,
    [firstname] TEXT,
    [lastname] TEXT)''')


# creates an account, if the
# #username is not already taken,
# #stores all the parameters in #the database, and notifies the
# #user of the successful #account creation
def create_acc(username, password, firstname, lastname):
    c.execute('''SELECT username FROM tank_database WHERE username = ?''', (username,))
    existing_user = c.fetchone()
    if existing_user:
        messagebox.showerror("Already Exists", "This account already exists, choose a different username")
        return False
    elif username == '' or username.isspace():
        messagebox.showerror("Invalid User", "Choose a valid username")
        # print('Choose a valid username')
    elif password == '' or password.isspace():
        messagebox.showerror("Invalid Password", "Choose a valid password")
        # print('Choose a valid password')
    elif not (firstname.isalpha()):
        messagebox.showerror("Invalid First Name", "Choose a valid first name")
        # print('Choose a valid first name')
    elif not (lastname.isalpha()):
        messagebox.showerror("Invalid Last Name", "Choose a valid last name")
        # print('Choose a valid last name')
    else:
        enc_password = fernet.encrypt(password.encode())
        # print("Encrypted Password:", enc_password)
        c.execute('''
        INSERT INTO tank_database (username, password, firstname, lastname)
        VALUES
        (?, ?, ?, ?)
        ''', (username, enc_password, firstname, lastname))
        conn.commit()
        messagebox.showinfo("Success!", "You have created an account.")
        return True


# logs the user into the Tank GUI if the username and password 
# entered match an acount in the database
def login(username, password):
    c.execute('''SELECT password FROM tank_database WHERE username = ?''', (username,))
    existing_user = c.fetchone()
    if existing_user is None:
        messagebox.showerror("Does not Exist", "This account does not exist, please create one")
        return False, 'nope'
    else:
        password_database = existing_user[0]
        try:
            decrypted_data_password = fernet.decrypt(password_database).decode()
            if password == decrypted_data_password:
                messagebox.showinfo("Success!", "You are now logged in.")
                c.execute('''SELECT firstname FROM tank_database WHERE username = ?''', (username,))
                use = c.fetchone()
                name = use[0]

                return True, name

            else:
                messagebox.showerror("Incorrect Password",
                                     "That is not the right password for this username, please try again")
                return False, 'nope'
        except Exception as e:
            print(f'The error was: {e}')
