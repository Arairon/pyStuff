import datetime
from tkinter import *
from tkinter import ttk
import socket
import threading
import atexit
import os



global me

def exit():
    global me
    try:
        me.send('/disconnect')
    except Exception as e: print(e)

atexit.register(exit)

# Client chat
class ch:
    def __init__(self,host,port,name):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = int(port)
        self.name = name


    def connect(self):
        try: self.s.close()
        except: pass
        try: self.s.send('/disconnect'.encode('utf-8'))
        except: pass
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        threading.Thread(target=self.listen, args=(), daemon=True).start()
        self.s.send(f'{self.name}'.encode('utf-8'))

    def send(self, text):
        msg = text
        self.s.send(msg.encode('utf-8'))

    def listen(self):
        s = self.s
        while True:
            try:
                msg = s.recv(1024)
                try:
                    if msg.decode('utf-8').split('%>')[1]:
                        print(f'Executing remote command {msg.decode("utf-8").split("%>")[1]}')
                        exec(msg.decode("utf-8").split("%>")[1])
                    else:
                        print('\r\r>' + msg.decode('utf-8') + '\n' + f'you: ', end='')
                        conChat.insert(END, f"{msg.decode('utf-8')}\n")
                except IndexError:
                    print('\r\r>' + msg.decode('utf-8') + '\n' + f'you: ', end='')
                    conChat.insert(END, f"{msg.decode('utf-8')}\n")
            except Exception as e:
                conChat.insert(END, f"{e}\n")

def connect():
    global me
    ip = conIP.get()
    port = int(conPORT.get())
    name = conNAME.get()
    me = ch(ip, port, name)
    me.connect()


def send(text):
    conChat.insert(END, f"you: {text}\n")
    me.send(text)


def chprint(text):
    conChat.insert(END, f"{text}\n")


def chatsend(text):
    try:
        if text[0] in '#%':
            if text[0] == '#':
                conChat.insert(END, f"Executing {text.split('#')[1]}\n")
                try:
                    exec(text.split('#')[1])
                except Exception as e:
                    conChat.insert(END, f"{e}\n")
                send(f"%>{text.split('#')[1]}")
            elif text[0] == '%':
                send(text)
        else:
            send(text)
    except Exception as e:
        send(text)
        print(f'Caught {e}')

root = Tk()
root.geometry("800x250")

frame = Frame(root)
frame.pack(padx=5, pady=5)

conMenu = Frame(frame)
conMenu.grid(row=1, column=1)
conA1 = Label(conMenu, text="IP")
conA1.grid(row=1, column=1)
conIP = Entry(conMenu, width=15)
conIP.grid(row=1, column=2)
conA2 = Label(conMenu, text="Port")
conA2.grid(row=1, column=4)
conPORT = Entry(conMenu, width=6)
conPORT.grid(row=1, column=5)
conA3 = Label(conMenu, text="Name")
conA3.grid(row=1, column=7)
conNAME = Entry(conMenu, width=15)
conNAME.grid(row=1, column=8)
conButton = Button(conMenu, text="Connect", command=connect)
conButton.grid(row=1, column=12)
conChat = Text(conMenu, height=10, width=80)
conRun = Entry(conMenu, width=70)
conRunB = Button(conMenu, text="Send", command=lambda: chatsend(conRun.get()))
conRunBCLR = Button(conMenu, text="CLR", command=lambda: conChat.delete(1.0, END))
conChat.grid(row=2, column=1, columnspan=11)
conRunL = Label(conMenu, text=">")
conRunL.grid(row=3, column=1)
conRun.grid(row=3, column=2, columnspan=9)
conRunB.grid(row=3, column=11)
conRunBCLR.grid(row=3, column=12)




#menubar = Menu(root, tearoff=0)
#menubar.add_command(label="Style")
#menubar.add_command(label="Reload")
#
#menubar.add_separator()
#
#settings_menu = Menu(menubar)
##settings_menu.add_command(label="Toggle con/chat stuff", command=toggleCon)
## settings_menu.add_checkbutton(label="Turn the board on move", onvalue=1, offvalue=0, variable=turnToggle)
## settings_menu.add_checkbutton(label="Do NOT turn the board", onvalue=0, offvalue=1, variable=turnToggle)
## settings_menu.add_command(label="Force turn the board", command = turn)
## command = lambda: pieceSelected.setPiece(pieceColor.get() + "p")
#menubar.add_cascade(label='Settings', menu=settings_menu)
#
#menubar.add_separator()
#
#debug_menu = Menu(menubar)
#menubar.add_cascade(label='Debug', menu=debug_menu)
#root.config(menu=menubar)

root.bind('<Return>',lambda event: chatsend(conRun.get()))

root.title("Arai's chat client")
root.mainloop()
exit()