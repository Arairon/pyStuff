import socket
import threading
import sys
import codecs
from datetime import datetime

global toKill
global clients
global S
global listeners
listeners = []
clients = []
toKill = []

host = ''
port = 7777

S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.bind((host, port))
print(f"Bound to {host} with port {port}")
S.listen(5)


def cls(classname):
    return getattr(sys.modules[__name__], classname)


def curTime():
    return datetime.now().strftime("%d:%m:%Y %I:%M%p")


class LogCls:
    instances = []

    def __init__(self, filename):
        print('Initializing logs')
        self.instances.append(self)
        self.file = codecs.open(f"{filename}", 'a', 'utf-8')
        self.file.write(f'\n\n\nServerLog Starting... @ {curTime()}')

    def log(self, txt='LogError: No text passed', loc='Unspec', tag='LOG'):
        print(f'[{tag}] @{{{loc}}} ({curTime()}) > {txt}')
        self.file.write(f'\n[{tag}] @{{{loc}}} ({curTime()}) > {txt}')
        self.file.flush()
        try:
            for i in Client.instances:
                if i.getCmd: i.s.send(f'[{tag}] @{{{loc}}} ({curTime()}) > {txt}'.encode('utf-8'))
        except:
            pass


log = LogCls(f'logs/ServerLog-{datetime.now().strftime("%d-%m-%Y_%I-%M%p")}.txt')


class Client:
    instances = []
    totalConnections = 0

    def __init__(self, socket, addr, name):
        #print(f"Initializing {name}")
        Client.totalConnections += 1
        self.active = True
        self.instances.append(self)
        self.s = socket
        self.ip = addr[0]
        self.addr = addr[1]
        self.id = self.totalConnections
        self.name = name
        self.username = f'{name}-{self.id}@{self.addr}'
        self.fucked = 0
        self.players = []
        self.authorized = False
        self.getCmd = False

    def gameRun(self, txt):
        for i in self.players:
            if i.active:
                #print(f"{self.username} >> Passing {txt} to {i.username}")
                log.log(f"{self.username} >> Passing {txt} to {i.username}", 'gameRun()')
                i.s.send(txt.encode('utf-8'))

def resetCons():
    global clients
    global listeners
    global toKill
    try:
        toKill.append('all')
        for i in listeners:
            toKill.append(i)
        for i in Client.instances:
            try:
                del i
            except Exception as e:
                log.log(f'Error: {e}', 'resetCons()@del-i', 'ERROR')
        try:
            clients = []
            Client.totalConnections = 0
            toKill.remove('all')
        except Exception as e:
            log.log(f'Error: {e}', 'resetCons()@VarsSet', 'ERROR')
    except Exception as e:
        log.log(f'Error: {e}', 'resetCons()', 'ERROR')
    log.log('resetCons completed', 'resetCons()')

def sendToAll(txt):
    global clients
    for i in clients:
        if i.active:
            #print(f"sending a msg to {i.username}")
            log.log(f"Sending a msg to {i.username}", 'sendToAll()')
            i.s.send(txt.encode('utf-8'))


def userSend(user, msg):
    global clients
    for i in clients:
        if i.username != user.username and i.active:
            i.s.send(f'{user.name}: {msg}'.encode("utf-8"))
            log.log(f'{user.name}: {msg}    as {user.username}', 'userSend()')


def accept():
    global S
    global clients
    #print(f'Listening to new connections')
    log.log('Listening to new connections', 'accept()', 'StartUp')
    while True:
        try:
            client, addr = S.accept()
            #print(f"Connection from {addr}")
            sendToAll(f"{addr[1]} is connecting!")
            client.send('>Connected, please login\n'.encode('utf-8'))
            threading.Thread(target=login, args=(client, addr,), daemon=True).start()
            #print(f"{addr[1]} is connecting!")
        except KeyboardInterrupt:
            #print("\n\n>>>STOPPING<<<\n\nReason: KeyboardInterrupt@accept")
            log.log('Error: KeyboardInterrupt -> Stopping', 'accept', 'ERROR')
            break
        except Exception as e:
            #print(f'{e}\n@accept')
            log.log(f'Error: {e} -> Ignoring', 'accept', 'ERROR')


def login(client, addr):
    global S
    try:
        global clients
        #print(f"Logging in {addr}")
        log.log(f'Logging in {addr}', f'login_{addr}')
        client.send(f"Please enter your name:".encode('utf-8'))
        name = client.recv(1024).decode('utf-8')
        log.log(f'Received name - {name}', f'login_{addr}')
        cl = Client(client, addr, name)
        for i in Client.instances:
            #print(f"Checking {i.username}")
            if cl.name == i.name and cl != i:
                #print("Found name")
                if i.active:
                    #print("Taken")
                    client.send(
                        f"This name is already taken and active\nUsing a random name(/name [name] to change it".encode(
                            'utf-8'))
                    cl.name = f'User{addr[1]}'
                    log.log(f'Name {name} is taken -> using random', f'login_{addr}')
                else:
                    #print("Changing")
                    cl.s.send(f"Found an existing client with that name\nReconnecting to it".encode('utf-8'))
                    cl.id = i.id
                    Client.instances.remove(i)
                    Client.totalConnections -= 1
                    cl.active = True
                    cl.username = f'{cl.name}-{cl.id}@{cl.addr}'
                    clients.append(cl)
                    cl.s.send(f"Welcome! {cl.username}".encode("utf-8"))
                    threading.Thread(target=listen, args=(cl,), daemon=True).start()
                    log.log(f'Logging in an existing client', f'login_{addr}')
                    return None
        client.send(f"Creating a new client...\n".encode('utf-8'))
        # exec(f'client{(len(Client.instances)+1)} = Client({client}, {addr}, {name})')
        clients.append(cl)
        #print(cl)
        #print(f'Clients:\n{clients}')
        cl.s.send(f"Welcome! {cl.username}".encode("utf-8"))
        threading.Thread(target=listen, args=(cl,), daemon=True).start()
        log.log(f'Created a new client: {cl.username}', f'login_{addr}')
    except KeyboardInterrupt:
        #print("\n\n>>>ERROR<<<\n\nReason: KeyboardInterrupt@login")
        log.log('Error: KeyboardInterrupt -> Stopping', 'accept', 'ERROR')
    except Exception as e:
        #print(f'{e}\n@login')
        log.log(f'Error: {e} -> Ignoring', 'accept', 'ERROR')



def id(id):
    for i in Client.instances[::-1]:
        if i.id == id:
            ret = i
        else:
            ret = 'I am a failure'
    return ret


def disconnect(client):
    global clients
    global toKill
    try:
        client.s.send(
            f'Goodbye, the server will keeping the client account\nFeel free to reconnect using your name'.encode(
                'utf-8'))
    except:
        #print('Failed to send the disconnect message')
        log.log(f'Failed to send the disconnect message', f'disconnect({client.username})', 'MinorWarn')
    for i in clients:
        if i.username != client.username:
            if i.active:
                i.s.send(f'>>{client.name} has disconnected'.encode("utf-8"))
    toKill.append(client.addr)
    del client.s
    client.fucked = 0
    client.active = False
    log.log(f'Disconnected {client.username}', 'disconnect()')


def ditch(client):
    global clients
    global toKill
    try:
        client.s.send(f'Goodbye, the server will be keeping the client account'.encode('utf-8'))
    except:
        #print('Failed to send the ditch message')
        log.log(f'Failed to send the ditch message', f'ditch({client.username})', 'MinorWarn')
    for i in clients:
        if i.username != client.username:
            if i.active:
                i.s.send(f'>>{client.name} has left'.encode("utf-8"))
    toKill.append(client.addr)
    clients.remove(client)
    client.active = False
    Client.instances.remove(client)
    log.log(f'Ditched {client.username}', 'ditch()')
    del client


def listen(client):
    global toKill
    global clients
    global listeners
    listenId = f'{client.addr}'
    listeners.append(listenId)
    #print(f"Listening to {client.username}")
    log.log(f'Listening to {client.username}', f'listen_{client.username}')
    while True:
        try:
            if listenId in toKill:
                #print(f"Listener-{listenId} killed by list")
                log.log(f'Listener killed by list', f'listen_{client.username}')
                try:
                    toKill.remove(listenId)
                except:
                    pass
                break
            if not client.active: break
            msg = client.s.recv(1024).decode("utf-8")
            if not client.active: break
            #print(f'{client.name}: {msg}          ({client.username})')
            log.log(f'Received \'{msg}\' from {client.username}', f'listen_{client.username}', 'MSG')
            if msg == '': client.fucked += 1
            if client.fucked >= 10:
                #print(f'>>{client.username} IS FUCKED (ditching them)')
                log.log(f'{client.username} IS FUCKED', f'listen_{client.username}', 'ERROR')
                ditch(client)
                break
            if msg[0] not in '/%$' and msg != '':
                userSend(client, msg)
            elif msg != '':
                log.log(f'{client.username} issued {msg}', f'listen_{client.username}', 'CMD')
                #print(f'{client.username} issued {msg}')
                if msg.split()[0] == "/leave":
                    log.log(f'{client.username} has left', f'listen_{client.username}@/leave', 'CMD')
                    #print(f'>>{client.username} has left (ditching the client)')
                    ditch(client)
                    toKill.remove(listenId)
                    break
                elif msg.split()[0] == "/disconnect":
                    log.log(f'{client.username} has disconnected', f'listen_{client.username}@/disconnect', 'CMD')
                    #print(f'>>{client.username} has disconnected (keeping the client)')
                    disconnect(client)
                    toKill.remove(listenId)
                    break
                elif msg.split()[0] == "/list":
                    fullList = ''
                    for i in clients:
                        if i.active:
                            fullList = fullList + i.username + '\n'
                            #print(fullList)
                    #print(f'Fullist {fullList}')
                    client.s.send(fullList.encode('utf-8'))
                    log.log(f'Sent \n{fullList} back to client', f'listen_{client.username}@/list', 'CMD')
                elif msg.split()[0] == "/whoami":
                    client.s.send(f'You are {client.name}     ({client.username})'.encode('utf-8'))
                    log.log(f'Sent {client.username} info back', f'listen_{client.username}@/whoami', 'CMD')
                elif msg.split()[0] == "/connect":
                    try:
                        #print(msg.split()[1])
                        #print(client.id)
                        if int(msg.split()[1]) == int(client.id):
                            raise Exception("You can't connect to yourself")
                        client.players.append(id(msg.split()[1]))
                        id(msg.split()[1]).players.append(client)
                        id(msg.split()[1]).s.send(f"{client.username} has connected to you as a player".encode('utf-8'))
                        client.s.send(f"Connected to {id(msg.split()[1]).username}".encode('utf-8'))
                        log.log(f'{client.username} has connected to {id(msg.split()[1]).username}', f'listen_{client.username}@/connect', 'CMD')
                    except IndexError:
                        client.s.send(f"Usage: /playWith [clientID]".encode("utf-8"))
                        log.log(f'IndexError when handling /connect (may be user error)', f'listen_{client.username}', 'ERROR')
                    except Exception as e:
                        client.s.send(f"Error {e}".encode("utf-8"))
                        log.log(f'Error: {e}', f'listen_{client.username}@/connect', 'ERROR')
                elif msg.split()[0] == "/help":
                    client.s.send((
                                          f"List of commands:" +
                                          f"\n/leave - disconnect, ditch the client" +
                                          f"\n/disconnect - disconnect, keep the client for reconnecting" +
                                          f"\n/list - list connected clients\n/whoami - get your username" +
                                          f"\n/connect [id] - connect to someone to play").encode('utf-8'))
                    log.log(f'Sent help msg to client', f'listen_{client.username}@/help', 'CMD')
                elif msg.split()[0] == "/name":
                    try:
                        for i in clients:
                            if i.name == msg.split()[1]:
                                client.s.send(f"Name {msg.split()[1]} is already taken".encode('utf-8'))
                                raise Exception("Name is already taken (Ignore this error)")
                        client.name = str(msg.split()[1])
                        client.s.send(f"Changed your name to {msg.split()[1]}".encode('utf-8'))
                        log.log(f'Changed client name to {msg.split()[1]}', f'listen_{client.username}@/name', 'CMD')
                    except Exception as e:
                        #print(e)
                        log.log(f'Error: {e}', f'listen_{client.username}@/name', 'ERROR')
                elif msg.split()[0] == "/authorise":
                    if msg.split()[1] == '5452323':
                        client.authorized = True
                        client.s.send(f'\n\n\n\n\n\n\n\n'.encode('utf-8'))
                        client.s.send(f'You are now authorized'.encode('utf-8'))
                        log.log(f'Authorized {client.username}', f'listen_{client.username}@/authorise', 'CMD_WARN')
                    else:
                        client.s.send(f'Wrong password'.encode('utf-8'))
                        log.log(f'Wrong password', f'listen_{client.username}@/authorise', 'CMD_WARN')
                elif msg.split()[0] == "/getCmd":
                    if client.authorized and client.getCmd:
                        client.getCmd = False
                    elif client.authorized and not client.getCmd:
                        client.getCmd = True
                    elif not client.authorized:
                        log.log(f'{client.username} Issued an auth command {msg}', f'listen_{client.username}@$', 'CMD_WARN')

                elif msg.split()[0][0] == '$' and client.authorized:
                    #print(f'>>>\n{client.username} Issued a shell command {msg}\n>>>\n')
                    log.log(f'{client.username} Issued a shell command {msg}', f'listen_{client.username}@$', 'CMD_WARN')
                    try:
                        exec(msg.split('$')[1])
                    except Exception as e:
                        #print(f'>>>\n{e}\n@listen when handling {client.username}\'s command')
                        log.log(f'Error: {e} when handling {client.username}\'s command', f'listen_{client.username}@$', 'CMD_WARN')
                        client.s.send(e.encode('utf-8'))
                elif msg.split()[0][0] == '$' and not client.authorized:
                    log.log(f'{client.username} tried to issue a shell command {msg}, while not authorized', f'listen_{client.username}@$', 'CMD_WARN')
                elif msg.split()[0][0] == '%':
                    client.gameRun(msg)



        except AssertionError:
            break
        except Exception as e:
            log.log(f'Error: {e}', f'listen_{client.username}', 'ERROR')
            client.fucked += 1
            if client.fucked >= 5:
                log.log(f'Ditching {client.username} as FUCKED', f'listen_{client.username}', 'LOG')
                client.fucked = 0
                ditch(client)
                break
            #print(f'{e}\n@listen for {client.username}')


threading.Thread(target=accept, args=(), daemon=True).start()

while True:
    try:
        inp = input()
        if inp[0] == '$':
            log.log(f'Executing local command: {inp}', 'mainloop', 'WARN')
            exec(inp.split('$')[1])
        else:
            msg = f'CONSOLE: {inp}'
            log.log(f'Sent \'{inp}\' from console', 'mainloop', 'MSG')
            for i in clients:
                i.s.send(msg.encode('utf-8'))
    except KeyboardInterrupt:
        #print("\n\n>>>STOPPING<<<\n\nReason: KeyboardInterrupt@mainLoop")
        log.log(f'Error: KeyboardInterrupt -> Stopping', f'mainloop', 'ERROR')
        break
    except Exception as e:
        #print(f'{e}\n@mainLoop')
        log.log(f'Error: {e}', f'mainloop', 'ERROR')

log.log(f'Program end reached, closing...', f'MainThread', 'FINISH')