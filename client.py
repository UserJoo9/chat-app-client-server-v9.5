import threading
from datetime import datetime
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from tkinter import *
from tkinter import filedialog
import ntpath
import os
from time import sleep
from tkinter import messagebox
from PIL import Image, ImageTk
from pygame import mixer
import speech_recognition

mixer.init()


def notify(s):
    messagebox.showwarning("Notify!", s)


def getName():
    global name
    global tryGetName

    try:
        if my_msg.get() == "":
            notify("Enter valid name")
            tryGetName = True
        elif my_msg.get():
            n = my_msg.get()
            m = n.split(' ')
            if len(m) > 1:
                notify("Name too long\nType your first name only or your nickname")
                tryGetName = True

            else:
                name = my_msg.get()
                top.title(name)
                my_msg.set("")
                tryGetName = False
                receive_thread.start()
    except Exception:
        notify("An error while set name")


def receive():
    global recOn, recMediaOn, tryGetName
    global name
    while recOn:
        try:
            msg = client_sock.recv(bufferSize).decode("utf-8")
            print("received msg : ", msg)
            if msg == "B02E9D6FA85D5C391C7EC133218ACC10EB34D4A3649E0B4C61D766A401889CD1075A6DEA7CA924B86AFB06BE7DFA506FFD9512109855CD2B8FF0602EA3826A35":
                if recMediaOn:
                    print("the finger msg : ", msg)
                    recmedia()
                else:
                    pass
            else:
                if msg == "Welcome to chat, type your name":
                    client_sock.send(bytes(name, "utf-8"))
                else:
                    if recNormal:
                        ms = msg.split(' ')
                        for i in range(0, len(ms)):
                            if ms[i] == name:
                                if SEPARATOR in ms:
                                    pass
                                else:
                                    msg_list.insert(END, f">>> {current_time}- " + msg)
                                    msg_list.insert(END, "")
                                    print("your name")
                                    break
                            else:
                                if SEPARATOR in ms:
                                    pass
                                else:
                                    msg_list.insert(END, f"{current_time}- " + msg)
                                    msg_list.insert(END, "")

                                break
                        print(msg)
        except Exception:
            break
        msg_list.yview(END)


def recmedia():
    global recOn
    recOn = False
    try:
        msg_list.insert(END, "Receiving files")
        print("Start receiving files")
        file = client_sock.recv(bufferSize).decode("utf-8")
        sender_name, file, dData = file.split(SEPARATOR)
        print("Received file name: ", file)
        with open(file, 'wb') as f:
            print("-------------------------------------\n")
            dDataArr = bytes(dData, 'utf-8')
            print("dData1 : ", dDataArr)
            f.write(dDataArr)
            print("dData2 : ", dData)
            while 1:
                data = client_sock.recv(bufferSize)
                print("data received : ", data)
                if data == b'440453497D561BB73996D6BDD1008CC104D0124CFBC1996B128235348F7936F88867F80DB341A533C50B3457A12B352BA2D7D91D10835CA0F9A470C6B789AA45':
                    break
                f.write(data)
                print("the data written : ", data)
        f.close()
        print("writing closed")
        msg_list.insert(END, f"Received {file} from ({sender_name})")
        msg_list.insert(END, "")
        print(f"Received {file} from {sender_name}")
        recOn = True
    except:
        notify("File receiving failed!")
        recOn = True
    msg_list.yview(END)


def media():
    global recMediaOn, recNormal, recOn
    recMediaOn = False
    recNormal = False
    file_path = filedialog.askopenfilename(initialdir='C:/', title='Select a file', filetypes=[("All files", "*.txt")])
    file_name = os.path.basename(file_path)
    if file_path == '':
        notify("You haven't select any file!")
    else:
        try:

            client_sock.send(bytes(
                "B02E9D6FA85D5C391C7EC133218ACC10EB34D4A3649E0B4C61D766A401889CD1075A6DEA7CA924B86AFB06BE7DFA506FFD9512109855CD2B8FF0602EA3826A35",
                "utf-8"))
            msg_list.insert(END, f"File {file_name} sending...")
            print("Header sent")
            client_sock.send(bytes(f"{name} {SEPARATOR} {file_name} {SEPARATOR}", "utf-8"))
            print("file name sent", file_name)
            with open(file_path, "rb") as f:
                while True:
                    bytes_read = f.read(bufferSize)
                    print("data sent : ", bytes_read)
                    if not bytes_read:
                        break
                    client_sock.sendall(bytes_read)
            f.close()
            print("reading closed")
            sleep(1)
            client_sock.send(bytes(
                "440453497D561BB73996D6BDD1008CC104D0124CFBC1996B128235348F7936F88867F80DB341A533C50B3457A12B352BA2D7D91D10835CA0F9A470C6B789AA45",
                "utf-8"))
            print("trailer sent")
            msg_list.insert(END, f"File {file_name} sent.")
            msg_list.insert(END, "")
            sleep(1)
            recMediaOn = True
            recNormal = True
        except:
            notify("file sending failed!")
    recMediaOn = True
    recNormal = True
    msg_list.yview(END)


def send(event=None):
    global str
    global count
    global name
    if tryGetName:
        try:
            client_sock.send(bytes("", "utf-8"))
            getName()
        except Exception:
            notify("You not connected to any target!")
    else:
        msg = my_msg.get()
        my_msg.set("")
        if msg == "C2636AD578F7B925EE4CF573969D4EC6640DE7B0176BF1701ADECE3A75937DC206AB1B8EE5343341D102C3BED1EC804A5C2A9E1222A7FB53A3CC02DA55487329":
            try:
                client_sock.send(bytes(msg, "utf-8"))
                force_on_closing()
            except Exception:
                notify("Can't close, not connected before!")
        else:
            try:
                client_sock.send(bytes(msg, "utf-8"))
            except Exception:
                notify("You not connected to any target!")


count = 0


def audio():
    global text
    mixer.music.load('music1.mp3')
    mixer.music.play()
    sr = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as m:
        try:
            sr.adjust_for_ambient_noise(m, duration=0.2)
            voice = sr.listen(m)
            text = sr.recognize_google(voice)
            my_msg.set(text)
            mixer.music.load('music2.mp3')
            mixer.music.play()
        except:
            pass



# def voice_status_():
#     global voice_status
#     if voice_status is None:
#         voice_status = True
#         voice_stat['text'] = "VOICE ON"
#         voice_stat['fg'] = "blue"
#         voice_stat['font'] = ("calbiri", 10, "bold")
#     else:
#         voice_status = None
#         voice_stat['text'] = "VOICE OFF"
#         voice_stat['fg'] = "red"
#         voice_stat['font'] = ("calbiri", 10, "bold")


def conn(*args):
    global flag, count, port, addr, client_sock, host, str, recflag, flag2, s
    # global var
    # arr=['a','b','c','d','e','f','g','h','i','g','k','l','m','n','o','b','q','r','s','t','u','v','w','x','y','z','$',',',';',':','!','?','(',')','<','>']
    # chars = "'q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m',':',':','#','^','*','(',')','_','-','+','=','/','>','<','{','}'"
    count += 1
    if str:
        if count != 4:
            flag2 = True
            arr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
            s = my_msg.get()
            for i in arr:
                for j in s:
                    if j != i:
                        flag2 = False
                    else:
                        flag2 = True
                        break

            if flag2:
                try:
                    host = my_msg.get()
                    addr = (host, port)
                    client_sock.connect(addr)
                    notify("Enter your name")
                    msg_list.insert(END, "Type your name")
                    my_msg.set("Type your name!")
                    # if recflag==True:
                    # # getName_thread.start()
                    #
                    # recflag=False
                    str = False
                    entry_field.bind("<Return>", send)
                    conn_button.forget()
                except Exception:
                    # msg_list.insert(END, "Connection out, invalid try.")
                    notify("Connection out, invalid try.")
                    host = ''
                    if (flag == True):
                        conn_check.start()
                    flag = False

            else:
                # msg_list.insert(END, "Invalid address")
                notify("Invalid address")
                host = ''
                if (flag == True):
                    conn_check.start()
                flag = False

        elif count == 4:
            # msg_list.insert(END, "Too many trying attempts, will exit!")
            notify("Too many trying attempts, will exit!")
            sleep(3)
            force_on_closing()

    else:
        # msg_list.insert(END, "Already connected")
        notify("Already connected")


var = 0


def conn_check():
    global count
    global var
    global str
    while count != 4:
        if var != 6:
            if host == '':
                msg_list.insert(END, "Waiting for ip, 10 second left!")
                # notify("Waiting for ip, 10 second left!")
                var += 1
                sleep(10)
            elif host != '':
                break
        elif var == 6:
            # msg_list.insert(END, "Too many time to response, will exit!")
            notify("Too many time to response, will exit!")
            str = False
            sleep(3)
            # msg_list.insert(END, "exited.")
            notify("exited.")
            sleep(2)
            force_on_closing()


def on_closing(event=None):
    global recOn
    ok = messagebox.askokcancel("Alert!","If you closed now all your chat will be remove!\nSure do you want to exit?")
    if ok == 1:
        recOn = False
        try:
            client_sock.send(bytes("C2636AD578F7B925EE4CF573969D4EC6640DE7B0176BF1701ADECE3A75937DC206AB1B8EE5343341D102C3BED1EC804A5C2A9E1222A7FB53A3CC02DA55487329", "utf-8"))
        except Exception:
            # msg_list.insert(END,f"{current_time} Error, can't close!")
            notify("Can't close, not connected before!")
        client_sock.close()
        top.quit()
        top.destroy()
    else:
        pass

def force_on_closing(event=None):
    global recOn

    recOn = False
    try:
        client_sock.send(bytes("C2636AD578F7B925EE4CF573969D4EC6640DE7B0176BF1701ADECE3A75937DC206AB1B8EE5343341D102C3BED1EC804A5C2A9E1222A7FB53A3CC02DA55487329", "utf-8"))
    except Exception:
        # msg_list.insert(END,f"{current_time} Error, can't close!")
        notify("Can't close, not connected before!")
    client_sock.close()
    top.quit()
    top.destroy()



# def popGetName():
#     global name
#
#     def notify():
#         messagebox.showwarning("Alert", "You must type your name in chat box")
#         popup.destroy()
#     def getName():
#         global name
#         if(name_field.get()=="Type here"):
#             alert=Label(popup,text="Invalid name")
#             alert.pack()
#         else:
#             name = name_field.get()
#             name_field.set("")
#             my_msg.set(name)
#             send()
#             top.title(name)
#             popup.destroy()
#     try:
#         popup=Toplevel(top)
#         popup.title("Define your name")
#         popup.geometry("300x200")
#         alert = Label(popup, text="Type your name!")
#         alert.pack()
#         name_field = StringVar()
#         name_field.set("Type here")
#         na_field = Entry(popup, textvariable=name_field,width=30)
#         na_field.pack()
#         na_field.bind("<Return>", getName)
#         button=Button(popup, text="Confirm",command=getName)
#         button.pack()
#         popup.protocol("WM_DELETE_WINDOW", notify)
#         popup.mainloop()
#     except Exception:
#         pass

# def off_session():
#     global str, count, var, flag2
#     str = True
#     flag2 = True
#     count = 0
#     var = 0
#     client_sock.send(bytes("exit","utf-8"))
#     client_sock.close()


t = datetime.now()


def xtime():
    global current_time
    global t
    while 1:
        t = datetime.now()
        current_time = t.strftime("%H:%M:%S")


top = Tk('500x900')
top.title("Client")
top.resizable(False, False)
top.iconbitmap(True, "images/chatFavicon.ico")
top.config(bg="#6c7e84")
massage_frame = Frame(top)
my_msg = StringVar()
my_msg.set("Type ip here!")
scrollbar = Scrollbar(massage_frame)
msg_list = Listbox(massage_frame, height=15, background='#45805a', width=71, fg='White', yscrollcommand=scrollbar.set,
                   font=("Calibri", 14))
scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack(side=LEFT, fill=BOTH)
msg_list.pack()
current_time = t.strftime("%H:%M:%S")
msg_list.insert(END, f"{current_time}- Enter target ip!")
massage_frame.pack()

entry_field = Entry(top, textvariable=my_msg, width=56, background="#e8dab5", font=("Calbiri", 18,'bold'))
entry_field.bind("<Return>", conn)
entry_field.pack()
entry_field.focus_set()
SendImage = Image.open("images/send.png")
send_img_resized = SendImage.resize((50, 50), Image.ANTIALIAS)
newSendImg = ImageTk.PhotoImage(send_img_resized)
send_button = Button(top, image=newSendImg, command=send,bd=0,relief=GROOVE, background="#6c7e84", activebackground="#1d2224")
send_button.pack(side=RIGHT,padx=5,pady=5)
textImage = Image.open("images/text.ico")
text_img_resized = textImage.resize((50, 50), Image.ANTIALIAS)
newTextImg = ImageTk.PhotoImage(text_img_resized)
text_button = Button(top, image=newTextImg, command=media,bd=0,relief=GROOVE, background="#6c7e84", activebackground="#1d2224", padx=5)
text_button.pack(side=RIGHT,padx=15,pady=5)
connectImage = Image.open("images/connect.png")
connect_img_resized = connectImage.resize((50, 50), Image.ANTIALIAS)
newConnectImg = ImageTk.PhotoImage(connect_img_resized)
conn_button = Button(top, image=newConnectImg, command=conn, bd=0,relief=GROOVE, background="#6c7e84", activebackground="#1d2224", padx=5)
conn_button.pack(side=RIGHT)
# exit_button = Button(top, text="Exit!", command=off_session, background="red", fg='black', font=("Calbiri", 14))
# exit_button.pack(side=LEFT)

newFrame = Frame(top, bg='#6c7e84')
newFrame.pack(expand=True, fill=BOTH)
MicImage = Image.open("images/microphone.png")
img_resized = MicImage.resize((50, 50), Image.ANTIALIAS)
newMicImg = ImageTk.PhotoImage(img_resized)
voice = Button(newFrame, image=newMicImg, relief=GROOVE, bd=0, bg="#6c7e84", activebackground="#1d2224", command=audio)
voice.place(y=7,x=540)
# voice_stat = Button(newFrame, text='VOICE OFF', font=("calbiri", 10, "bold"), relief=GROOVE, bd=0, fg="red",
#                     bg="#6c7e84", activebackground="#6c7e84", command=voice_status_)
# voice_stat.pack(side=LEFT, expand=TRUE, fill=BOTH)

top.protocol("WM_DELETE_WINDOW", on_closing)

tryGetName = True
flag = True
flag2 = True
str = True
recflag = True
recOn = True
recMediaOn = True
recNormal = True
voice_status = None
SEPARATOR = "<SEPARATOR>"
# name = ''

port = 1234
bufferSize = 2048

host = ''
addr = ()

client_sock = socket(AF_INET, SOCK_STREAM)

# getName_thread=Thread(target=popGetName)

XTIME = Thread(target=xtime)
XTIME.start()

receive_thread = Thread(target=receive)

conn_check = Thread(target=conn_check)

top.mainloop()
