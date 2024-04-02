# imports all the necessary libraries
from tkinter import *
from tkinter import scrolledtext
from login import *
import requests
import cv2
from PIL import ImageTk, Image
import processing

log_box = None


# creates the root tkinter window with options to Create Account, #Login, or Quit
def create_root():
    global log_box
    root = Tk()
    root.geometry("500x500")
    create = Button(root, text='Create Account', command=lambda: create_window(root))
    create.grid(row=0, column=7)
    log = Button(root, text='Login', command=lambda: LoginWindow(root))
    log.grid(row=1, column=7)
    out = Button(root, text='Quit', command=root.destroy)
    out.grid(row=3, column=7)

    root.mainloop()


# returns whatever window is inputted back to the root window
def Aeturn(login_wind, root, username=None):
    login_wind.destroy()
    root.deiconify()


# if an account is created succesfully, returns to the root window
def check_create_acc(user, pword, fname, lname, create_wind, root):
    logging_create(user)
    if create_acc(user, pword, fname, lname):
        Aeturn(create_wind, root)


# posts the direction given to the button key on the give url
# also calls the logging movement function and updates the log
def postDataMove(direct, user):
    # url = "http://192.168.1.42:4200/moving"
    # data = {'button': direct}
    # r = requests.post(url, json=data)
    # print("Command Sent")
    logging_movement(user, direct)
    log_text = update_log()
    log_box.configure(state='normal')
    log_box.delete('1.0', END)
    log_box.insert(INSERT, log_text)
    log_box.configure(state='disabled')


# creates a window where users can enter all of the parameters
# required to create an account and where users can create the #account
def create_window(root):
    global log_box
    create_wind = Toplevel(root)
    root.withdraw()
    create_wind.title('Create Account')
    create_wind.geometry('500x500')
    user = Label(create_wind, text='Enter your username: ')
    user.grid(row=0, column=0)
    pword = Label(create_wind, text='Enter your password: ')
    pword.grid(row=1, column=0)
    fname = Label(create_wind, text='Enter your first name: ')
    fname.grid(row=2, column=0)
    lname = Label(create_wind, text='Enter your last name: ')
    lname.grid(row=3, column=0)
    e1 = StringVar()
    e2 = StringVar()
    e3 = StringVar()
    e4 = StringVar()
    userent = Entry(create_wind, textvariable=e1, bg="light gray", fg="black")
    userent.grid(row=0, column=1)
    pwordent = Entry(create_wind, textvariable=e2, bg="light gray", fg="black")
    pwordent.grid(row=1, column=1)
    fnament = Entry(create_wind, textvariable=e3, bg="light gray", fg="black")
    fnament.grid(row=2, column=1)
    lnament = Entry(create_wind, textvariable=e4, bg="light gray", fg="black")
    lnament.grid(row=3, column=1)
    enterbutton = Button(create_wind, text='Create',
                         command=lambda: check_create_acc(userent.get(), pwordent.get(), fnament.get(), lnament.get(),
                                                          create_wind, root))
    enterbutton.grid(row=7, column=0)
    backbutton = Button(create_wind, text='Back', command=lambda: Aeturn(create_wind, root))
    backbutton.grid(row=7, column=1)
    create_wind.mainloop()


# if a user logs in successfully, creates the Tank GUI window with,
# #at the moment, a welcome statement and logout button
def check_logged_in(user, password, login_wind, root):
    global log_box
    valid, name = login(user, password)
    if valid:
        all_log(user)
        tank_wind = Toplevel(login_wind)
        login_wind.withdraw()
        tank_wind.title('Tank Interface')

        tank_wind.geometry('500x500')
        canvas = Canvas(tank_wind, bg='white', height=500, width=500)
        canvas.pack()
        canvas.create_line(250, 0, 250, 500, fill='black')
        canvas.create_line(0, 250, 500, 250, fill='black')
        welcome = Label(tank_wind, text=f'Welcome {name.title()}')
        logout = Button(tank_wind, text='Logout', command=lambda: logging_out(tank_wind, root, user))
        forward = Button(tank_wind, text=u'\u2191', command=lambda: postDataMove("forward", user))
        backward = Button(tank_wind, text=u'\u2193', command=lambda: postDataMove("backward", user))
        right = Button(tank_wind, text=u'\u2192', command=lambda: postDataMove("right", user))
        left = Button(tank_wind, text=u'\u2190', command=lambda: postDataMove("left", user))
        play = Button(tank_wind, text=u'\u25B6', command=lambda: postDataMove("go", user))
        stop = Button(tank_wind, text=u'\u2587', command=lambda: postDataMove("stop", user))
        log_box = scrolledtext.ScrolledText(tank_wind, width=30, height=15, wrap=WORD)
        log_box.insert(INSERT, str(update_log()))
        log_box.configure(state='disabled')
        clean_vid = cv2.VideoCapture('My Movie 29.mp4')
        update_vid(canvas, tank_wind, clean_vid)
        update_overlay(canvas, tank_wind, clean_vid)
        # log_data = Button(tank_wind, text='View Full Log', command=lambda: postData("stop", user))
        # tank_wind.bind('<Up>', lambda: postDataMove('forward', user))
        # tank_wind.bind('<Down>', lambda: postDataMove('backward', user))
        # tank_wind.bind('<Left>', lambda: postDataMove('left', user))
        # tank_wind.bind('<Right>', lambda: postDataMove('right', user))
        canvas.create_window(380, 370, window=log_box)
        canvas.create_window(250, 20, window=welcome)
        canvas.create_window(400, 20, window=logout)
        canvas.create_window(370, 100, window=forward)
        canvas.create_window(370, 200, window=backward)
        canvas.create_window(440, 150, window=right)
        canvas.create_window(300, 150, window=left)
        canvas.create_window(350, 150, window=play)
        canvas.create_window(390, 150, window=stop)
        tank_wind.mainloop()


# creates a window where the user can log into the Tank GUI,
# and the window notifies the user of successful login, incorrect password, or account nonexistence
def LoginWindow(root):
    login_wind = Toplevel(root)
    root.withdraw()

    login_wind.title('Login')
    login_wind.geometry('500x500')
    user = Label(login_wind, text='Enter your username: ')
    user.grid(row=0, column=0)
    pword = Label(login_wind, text='Enter your password: ')
    pword.grid(row=1, column=0)
    e1 = StringVar()
    e2 = StringVar()
    userent = Entry(login_wind, textvariable=e1, bg="light gray", fg="black")
    userent.grid(row=0, column=1)
    pwordent = Entry(login_wind, textvariable=e2, bg="light gray", fg="black")
    pwordent.grid(row=1, column=1)
    print(userent.get(), pwordent.get())
    enterbutton = Button(login_wind, text='Login',
                         command=lambda: check_logged_in(userent.get(), pwordent.get(), login_wind, root))
    enterbutton.grid(row=5, column=0)
    backbutton = Button(login_wind, text='Back', command=lambda: Aeturn(login_wind, root))
    backbutton.grid(row=5, column=1)
    login_wind.mainloop()


# returns the user to the previous screen and calls the logging function to update the log
def logging_out(tank_wind, root, username):
    Aeturn(tank_wind, root, username)
    logging_movement(username, 'logout')


# logs the creation of an account with the given user name and the time
def logging_create(username):
    try:
        tdytime = datetime.datetime.now()
        tdy = tdytime.strftime("%x")
        timet = tdytime.strftime("%X")

        writestr = f"\n{username} created an account on {tdy} at {timet}"

        with open("log.txt", "a") as f:
            f.write(writestr)

    except Exception as e:
        print(f"An error occurred: {e}")


# logs whenever the user logins in with the given time and date
def all_log(username):
    try:
        tdytime = datetime.datetime.now()
        tdy = tdytime.strftime("%x")
        timet = tdytime.strftime("%X")

        writestr = f"\n{username} logged into their account on {tdy} at {timet}"

        with open("log.txt", "a") as f:
            f.write(writestr)

    except Exception as e:
        print(f"An error occurred: {e}")


# logs the movement given the direction and user who moved the robot with a time and date
def logging_movement(username, direction):
    tdytime = datetime.datetime.now()
    tdy = tdytime.strftime("%x")
    timet = tdytime.strftime("%X")
    if direction == 'stop':
        writestr = f"\n{username} stopped the robot on {tdy} at {timet}"
    elif direction == 'logout':
        writestr = f"\n{username} logged out on {tdy} at {timet}"
    elif direction == "go":
        writestr = f"\n{username} played the demo on {tdy} at {timet}"
    else:
        writestr = f"\n{username} moved the robot {direction} on {tdy} at {timet}"
    with open("log.txt", "a") as f:
        f.write(writestr)


# updates the visible log using the log.txt file
def update_log():
    log_str = ""
    try:
        with open("log.txt", "r") as f:
            log_lines = f.readlines()[-10:]
            for line in log_lines[::-1]:
                log_str += line.strip() + "\n"
    except Exception as e:
        print(f"An error occurred while updating the log: {e}")
    return log_str


# updates the clean video stream on the gui by reading it from a video source already given
def update_vid(canvas, tank_wind, source):
    ret, frame = source.read()
    if ret:
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        resized_photo = img.resize((256, 144))
        photo = ImageTk.PhotoImage(image=resized_photo)
        canvas.create_image(120, 120, image=photo)

        canvas.photo1 = photo

    canvas.after(30, update_vid, canvas, tank_wind, source)


# updates the overlay video on the gui by reading the video already given and applying the processing function on it
def update_overlay(canvas1, tank_wind, source):
    ret, frame = source.read()
    if ret:
        img = processing.process(frame)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        resized_photo = img.resize((256, 144))
        photo = ImageTk.PhotoImage(image=resized_photo)
        canvas1.create_image(120, 360, image=photo)

        canvas1.photo2 = photo

    canvas1.after(30, update_overlay, canvas1, tank_wind, source)
