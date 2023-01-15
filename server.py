import tkinter
import time
from datetime import datetime
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

t = datetime.now()


def xtime():
    global current_time
    global t
    while 1:
        t = datetime.now()
        current_time = t.strftime("%H:%M:%S")


def acceptIncomingConnections():
    while 1:
        client, clientAddress = server.accept()
        msg_list.insert(tkinter.END, f"{current_time}- New client " + f"%s:%s has connected." % clientAddress)
        client.send(bytes("Welcome to chat, type your name", "utf-8"))
        addresses[client] = clientAddress
        handle_thread = Thread(target=handleClient, args=(client,))
        handle_thread.start()


def handleClient(client):
    name = client.recv(bufferSize).decode("utf-8")
    joined = f'Welcome {name} !'
    client.send(bytes(joined, "utf-8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf-8"))
    clientsNames[client] = name

    while 1:
        msg = client.recv(bufferSize)
        if msg != bytes("C2636AD578F7B925EE4CF573969D4EC6640DE7B0176BF1701ADECE3A75937DC206AB1B8EE5343341D102C3BED1EC804A5C2A9E1222A7FB53A3CC02DA55487329", "utf-8"):
            if msg == b'B02E9D6FA85D5C391C7EC133218ACC10EB34D4A3649E0B4C61D766A401889CD1075A6DEA7CA924B86AFB06BE7DFA506FFD9512109855CD2B8FF0602EA3826A35':
                broadcast(msg)
                while 1:
                    msg = client.recv(bufferSize)
                    if msg == b'440453497D561BB73996D6BDD1008CC104D0124CFBC1996B128235348F7936F88867F80DB341A533C50B3457A12B352BA2D7D91D10835CA0F9A470C6B789AA45':
                        broadcast(msg)
                        break
                    else:
                        broadcast(msg)
            else:
                broadcast(msg, f"{name} : ")
        else:
            client.close()
            del clientsNames[client]
            broadcast(bytes(f"%s has left." % name, "utf-8"))
            break


def broadcast(msg, prefix=""):
    msg_list.insert(tkinter.END, f"{current_time}- All connected clients: ", clientsNames.values())
    for sock in clientsNames:
        msg_list.insert(tkinter.END, "sock: ", prefix)
        sock.send(bytes(prefix, "utf-8") + msg)


def gui_start():
    tkinter.mainloop()


top = tkinter.Tk('300x900')
top.title("Server")
top.resizable(False, False)
messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()
my_msg.set("!!! Server started !!!")
scrollbar = tkinter.Scrollbar(messages_frame)
msg_list = tkinter.Listbox(messages_frame, height=15, background='#3b4652', fg='White', width=50,
                           yscrollcommand=scrollbar.set, font=("Calibri", 14))
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

clientsNames = {}
addresses = {}
host = ''
port = 1234
bufferSize = 4096
addr = (host, port)

server = socket(AF_INET, SOCK_STREAM)
server.bind(addr)

current_time = ''
if __name__ == "__main__":
    server.listen(5)
    current_time = t.strftime("%H:%M:%S")
    msg_list.insert(tkinter.END, f"{current_time}- Server listening, waiting for connections...")
    XTIME = Thread(target=xtime)
    XTIME.start()
    ACCEPT_THREAD = Thread(target=acceptIncomingConnections)
    ACCEPT_THREAD.start()
    GUI_THREAD = Thread(target=gui_start())
    GUI_THREAD.start()
    ACCEPT_THREAD.join()
    server.close()
