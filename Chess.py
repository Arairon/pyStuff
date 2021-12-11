from tkinter import *
import sys


def func():  # Коммандная строка
    str = console.get()
    exec(str)
    print(f"Executing {str}")


def clamp(value, minv, maxv):
    return max(min(value, maxv), minv)


def turn():
    toTurn = save(True)
    move = toTurn[1]
    toTurn = toTurn[0]
    toTurn = toTurn[::-1]
    load((toTurn, move))
    for i in Square.instances:
        if i.black:
            i.black = False
        elif not i.black:
            i.black = True
    reloadAvailability()



global figDict
figDict = {
    "wp": "♙",
    "wr": "♖",
    "wk": "♘",
    "wb": "♗",
    "wq": "♕",
    "wa": "♔",
    "bp": "♟",
    "br": "♜",
    "bk": "♞",
    "bb": "♝",
    "bq": "♛",
    "ba": "♚",
    "none": "",
    "mode": "u"
}


def figureMode(mode=None):
    global figDict
    if mode is None:
        current = figDict.get("mode")
        if current == "u": mode = "n"
        if current == "n": mode = "c"
        if current == "c": mode = "u"
    if mode.lower() in ["unicode", "u"]:
        figDict = {
            "wp": "♙",
            "wr": "♖",
            "wk": "♘",
            "wb": "♗",
            "wq": "♕",
            "wa": "♔",
            "bp": "♟",
            "br": "♜",
            "bk": "♞",
            "bb": "♝",
            "bq": "♛",
            "ba": "♚",
            "none": "",
            "mode": "u"
        }
    elif mode.lower() in ["names", "titles", "n"]:
        figDict = {
            "wp": "pwn",
            "wr": "RK",
            "wk": "Kni",
            "wb": "Bis",
            "wq": "QQ",
            "wa": "KNG",
            "bp": "pwn",
            "br": "RK",
            "bk": "Kni",
            "bb": "Bis",
            "bq": "QQ",
            "ba": "KNG",
            "none": "",
            "mode": "n"
        }
    elif mode.lower() in ["characters", "chars", "c"]:
        figDict = {
            "wp": ".",
            "wr": "||",
            "wk": "K",
            "wb": "^",
            "wq": "/\\",
            "wa": "W",
            "bp": ".",
            "br": "||",
            "bk": "K",
            "bb": "^",
            "bq": "/\\",
            "ba": "W",
            "none": "",
            "mode": "c"
        }
    else:
        sendText(f"Unknown mode {mode}")
    for i in Square.instances:
        if (i.figure != "none") and (type(i.figure) != "NoneType"):
            i.setPiece(i.figure)
    reloadAvailability()


global board
boardList = [  # Не знаю почему, но объявил этот лист заранее
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
]

global pieceSelected
pieceSelected = None
global whiteMoves
whiteMoves = True


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


def toCoords(coords):  # Перевод из a1 в (0, 0)
    toCoords = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
    }
    coords = list(coords)
    a = toCoords[coords[0]]
    b = int(coords[1]) - 1
    return (a, b)


def getCoords(coords):  # Перевод из (0,0) в а1
    fromCoords = {
        0: "a",
        1: "b",
        2: "c",
        3: "d",
        4: "e",
        5: "f",
        6: "g",
        7: "h"
    }
    a = fromCoords[coords[0]]
    b = str(coords[1] + 1)
    c = a + b
    return (c)


class SquareObj:  # Для удобного обращения к объектам интерфейса
    def __init__(self, figure, label, button, output, frame):
        self.figure = figure
        self.label = label
        self.button = button
        self.output = output
        self.frame = frame


class Square:  # Сама клетка
    instances = []

    def __init__(self, coords, figure, tkObject):
        self.coords = coords
        self.figure = figure
        self.tkObject = tkObject
        self.brdCoords = toCoords(coords)
        self.black = False
        self.instances.append(self)
        self.hasMoved = False

    def available(self):  # Раскрывает кнопку выбора и окно, где отображается фигура
        self.tkObject.figure.grid(row=1, column=0)
        self.tkObject.button.grid(row=1, column=1)

    def unavailable(self):  # Скрывает кнопку выбора...
        self.tkObject.figure.grid_forget()
        self.tkObject.button.grid_forget()

    def selectable(self, switch):  # Вкл\выкл кнопка выбора
        if switch == True:
            self.tkObject.button.grid(row=1, column=1)
        else:
            self.tkObject.button.grid_forget()

    def setPiece(self, piece):  # Устанавливает значения фигур, цвет окна и символ фигуры
        piece = piece.lower()
        global figDict
        if piece in figDict.keys():
            self.figure = piece
            self.hasMoved = True
            if self.black is True: sq.tkObject.frame.config(highlightbackground="black", highlightthickness=3)
            if self.black is False: sq.tkObject.frame.config(highlightbackground="gray", highlightthickness=2)
            self.tkObject.frame.config(highlightbackground="black")
            if piece[0] == "w":
                self.tkObject.figure.config(bg="white")
            if piece[0] == "b":
                self.tkObject.figure.config(bg="gray")
            if piece != "none":
                self.tkObject.figure.delete(0.0, END)
                self.tkObject.figure.insert(END, figDict.get(piece))
                self.available()
            else:
                self.tkObject.figure.delete(0.0, END)
                self.tkObject.figure.config(bg="lightgray")


def aroundSquares(square):  # Находит диагонали, на которых находится клетка
    horseMove = {
        1: (-2, -1),
        2: (-2, 1),
        3: (2, -1),
        4: (2, 1),
        5: (-1, -2),
        6: (-1, 2),
        7: (1, -2),
        8: (1, 2)
    }
    origCoords = square.brdCoords
    coords = origCoords
    r_u = []
    diag = abs(7 - max(coords))
    for i in range(diag):
        coords = (coords[0] + 1, coords[1] + 1)
        exec(f"r_u.append({getCoords(coords)})")
    l_l = []
    coords = origCoords
    diag = abs((7 - abs(coords[0] - coords[1])) - diag)
    for i in range(diag):
        coords = (coords[0] - 1, coords[1] - 1)
        exec(f"l_l.append({getCoords(coords)})")
    coords = origCoords
    invertCoords = (7 - coords[0], coords[1])
    l_u = []
    coords = origCoords
    diag = abs(7 - max(invertCoords))
    for i in range(diag):
        coords = (coords[0] - 1, coords[1] + 1)
        exec(f"l_u.append({getCoords(coords)})")
    r_l = []
    coords = origCoords
    diag = abs((7 - abs(invertCoords[0] - invertCoords[1])) - diag)
    for i in range(diag):
        coords = (coords[0] + 1, coords[1] - 1)
        exec(f"r_l.append({getCoords(coords)})")
    diagonals = (r_u, l_u, r_l, l_l)
    coords = origCoords
    horL = []
    horR = []
    vertU = []
    vertD = []
    for i in range(coords[0]):
        coords = (coords[0] - 1, coords[1])
        exec(f"horL.append({getCoords(coords)})")
    coords = origCoords
    for i in range(7 - coords[1]):
        coords = (coords[0], coords[1] + 1)
        exec(f"vertU.append({getCoords(coords)})")
    coords = origCoords
    for i in range(7 - coords[0]):
        coords = (coords[0] + 1, coords[1])
        exec(f"horR.append({getCoords(coords)})")
    coords = origCoords
    for i in range(coords[1]):
        coords = (coords[0], coords[1] - 1)
        exec(f"vertD.append({getCoords(coords)})")
    coords = origCoords
    lines = (horL, horR, vertU, vertD)
    horse = []
    for i in range(8):
        try:
            got = (coords[0] + horseMove.get(i + 1)[0], coords[1] + horseMove.get(i + 1)[1])
            exec(f"horse.append({getCoords(got)})")
        except:
            pass
    horse = tuple(horse)
    return diagonals, lines, horse


def select(Square):
    eventCheck()
    global boardList
    global pieceSelected
    global whiteMoves
    textOut.delete(0, END)
    if Square == pieceSelected:  # при нажатии на уже выбранную клетку снимает выбор
        sendText("Piece unselected")
        if pieceSelected.black is True: pieceSelected.tkObject.frame.config(highlightbackground="black",
                                                                            highlightthickness=3)
        if pieceSelected.black is False: pieceSelected.tkObject.frame.config(highlightbackground="gray",
                                                                             highlightthickness=2)
        pieceSelected = None
        reloadAvailability()
    elif pieceSelected is None:  # Если клетка не выбрана, выбрать нажатую
        if ((whiteMoves is True) and (Square.figure[0] == "w")) or (
                (whiteMoves is False) and (Square.figure[0] == "b") or everythingSelectable.get()):
            squareObj = Square.tkObject
            sendText(f"{Square.coords} Was selected")
            pieceSelected = Square
            squareObj.frame.config(highlightbackground="yellow")
            around = aroundSquares(pieceSelected)  # Declare available squares =========
            if Square.figure[0] == "b":
                if a1.black:
                    enemy = "w"
                    updwn = 1
                else:
                    enemy = "w"
                    updwn = 0
            if Square.figure[0] == "w":
                if a1.black:
                    enemy = "b"
                    updwn = 0
                else:
                    enemy = "b"
                    updwn = 1
            if Square.figure[1] == "p":  # PAWN LOGIC
                for i in Square.instances:
                    if i.figure[0] == Square.figure[0]: i.selectable(False)
                Square.selectable(True)
                around[1][updwn + 2][0].selectable(True)
                if (not Square.hasMoved) and (around[1][updwn + 2][0].figure == "none"):
                    around[1][updwn + 2][1].selectable(True)
                if around[1][updwn + 2][0].figure != "none": around[1][updwn + 2][0].selectable(False)
                if around[0][updwn * 2][0].figure[0] == enemy: around[0][updwn * 2][0].selectable(True)
                if around[0][updwn * 2 + 1][0].figure[0] == enemy: around[0][updwn * 2 + 1][0].selectable(True)

            if Square.figure[1] == "r":  # ROOK LOGIC
                for i in Square.instances:
                    if i.figure[0] == Square.figure[0]: i.selectable(False)
                Square.selectable(True)
                for ii in around[1]:
                    for i in ii:
                        if i.figure == "none":
                            i.selectable(True)
                        else:
                            if i.figure[0] == enemy:
                                i.selectable(True)
                                break
                            else:
                                break

            if Square.figure[1] == "k":  # KNIGHT LOGIC
                for i in Square.instances:
                    if i.figure[0] == Square.figure[0]: i.selectable(False)
                Square.selectable(True)
                for i in around[2]:
                    if i.figure[0] != Square.figure[0]: i.selectable(True)

            if Square.figure[1] == "b":  # BISHOP LOGIC
                for i in Square.instances:
                    if i.figure[0] == Square.figure[0]: i.selectable(False)
                Square.selectable(True)
                for ii in around[0]:
                    for i in ii:
                        if i.figure == "none":
                            i.selectable(True)
                        else:
                            if i.figure[0] == enemy:
                                i.selectable(True)
                                break
                            else:
                                break

            if Square.figure[1] == "q":  # QUEEN LOGIC
                for i in Square.instances:
                    if i.figure[0] == Square.figure[0]: i.selectable(False)
                Square.selectable(True)
                for ii in around[0]:
                    for i in ii:
                        if i.figure == "none":
                            i.selectable(True)
                        else:
                            if i.figure[0] == enemy:
                                i.selectable(True)
                                break
                            else:
                                break
                for ii in around[1]:
                    for i in ii:
                        if i.figure == "none":
                            i.selectable(True)
                        else:
                            if i.figure[0] == enemy:
                                i.selectable(True)
                                break
                            else:
                                break

            if Square.figure[1] == "a":  # KING LOGIC
                for i in Square.instances:
                    if i.figure[0] == Square.figure[0]: i.selectable(False)
                Square.selectable(True)
                for ii in around[0]:
                    for i in ii:
                        if i.figure == "none":
                            i.selectable(True)
                            break
                        else:
                            if i.figure[0] == enemy:
                                i.selectable(True)
                                break
                            else:
                                break
                for ii in around[1]:
                    for i in ii:
                        if i.figure == "none":
                            i.selectable(True)
                            break
                        else:
                            if i.figure[0] == enemy:
                                i.selectable(True)
                                break
                            else:
                                break
                if not Square.hasMoved:
                    color = i.figure[0]
                    for i in around[1][0]:
                        if (i.figure == (color + "r")) and (not i.hasMoved):
                            i.available()
                        elif i.figure == "none":
                            pass
                        else:
                            break
                    for i in around[1][1]:
                        if (i.figure == (color + "r")) and (not i.hasMoved):
                            i.available()
                        elif i.figure == "none":
                            pass
                        else:
                            break


        else:
            sendText("That's not your move! (HOW DID YOU EVEN DO THAT?)")
    else:  # Если клетка выбрана, и нажата другая клетка, сделать ход
        piece = pieceSelected.figure
        if Square.figure == "none":  # Если цель пустая, просто переместить фишку
            Square.setPiece(pieceSelected.figure)
            pieceSelected.setPiece("none")
            pieceSelected = None
            switchMover()

        try:
            if Square.figure[0] == "w" and not whiteMoves:  # Если цель - белая м чёрный ходит, ударить
                Square.setPiece(pieceSelected.figure)
                pieceSelected.setPiece("none")
                pieceSelected = None
                switchMover()
        except:
            pass
        try:
            if Square.figure[0] == "b" and whiteMoves:
                Square.setPiece(pieceSelected.figure)
                pieceSelected.setPiece("none")
                pieceSelected = None
                switchMover()
        except:
            pass
        try:
            if (pieceSelected.figure[1] == "a") and (Square.figure[1] == "r"):
                color = pieceSelected.figure[0]
                line = Square.brdCoords[1]
                dif = pieceSelected.brdCoords[0] - Square.brdCoords[0]
                dif = clamp(dif, -1, 1)
                sqCoords = getCoords((pieceSelected.brdCoords[0] - dif * 2, line))
                sqr = str_to_class(sqCoords)
                pieceSelected.setPiece("none")
                sqr.setPiece(color + "a")
                Square.setPiece("none")
                sqCoords = getCoords((pieceSelected.brdCoords[0] - dif, line))
                sqr = str_to_class(sqCoords)
                sqr.setPiece(color + "r")
                pieceSelected = None
                switchMover()
        except:
            pass
    eventCheck()


def switchMover():  # Передать ход, обновить доступность клеток
    global whiteMoves
    if whiteMoves:
        for i in Square.instances:
            if i.figure == "none":
                i.unavailable()
            elif i.figure[0] == "w":
                i.selectable(False)
            elif i.figure[0] == "b":
                i.selectable(True)
            whiteMoves = False
    else:
        for i in Square.instances:
            if i.figure == "none":
                i.unavailable()
            elif i.figure[0] == "b":
                i.selectable(False)
            elif i.figure[0] == "w":
                i.selectable(True)
            whiteMoves = True
    for i in Square.instances:
        if i.figure == "none":
            i.unavailable()
        if i.black is True: i.tkObject.frame.config(highlightbackground="black", highlightthickness=3)
        if i.black is False: i.tkObject.frame.config(highlightbackground="gray", highlightthickness=2)
        if i.black is True: i.tkObject.frame.config(background="#999999")
        if i.black is False: i.tkObject.frame.config(background="#e8e8e8")
    if turnToggle.get(): turn()


def eventCheck():  # Проверка событий (Становление дамкой или конец игры)
    whiteList = []
    blackList = []
    for i in Square.instances:
        if i.figure == "wp" and i.brdCoords[1] == 7:
            i.setPiece("wq")
            reloadAvailability()
        if i.figure == "bp" and i.brdCoords[1] == 0:
            i.setPiece("bq")
            reloadAvailability()
    for i in Square.instances:
        if i.figure != "none":
            if i.figure == "wa":
                whiteList.append(i)  # check if there are still white pieces
        if i.figure != "none":
            if i.figure == "ba":
                blackList.append(i)  # check if there are still black pieces
    if len(blackList) == 0:
        sendText("Congrats! White won!")
        for i in Square.instances: i.unavailable()
    if len(whiteList) == 0:
        sendText("Congrats! Black won!")
        for i in Square.instances: i.unavailable()


def reloadAvailability():  # Обновить доступность клеток
    global whiteMoves
    if whiteMoves:
        for i in Square.instances:
            if i.figure == "none":
                i.unavailable()
            elif i.figure[0] == "w":
                i.selectable(True)
            elif i.figure[0] == "b":
                i.selectable(False)
    else:
        for i in Square.instances:
            if i.figure == "none":
                i.unavailable()
            elif i.figure[0] == "b":
                i.selectable(True)
            elif i.figure[0] == "w":
                i.selectable(False)
    for i in Square.instances:
        if i.figure == "none":
            i.unavailable()
        if i.black is True: i.tkObject.frame.config(highlightbackground="black", highlightthickness=3)
        if i.black is False: i.tkObject.frame.config(highlightbackground="gray", highlightthickness=2)
        if i.black is True: i.tkObject.frame.config(background="#999999")
        if i.black is False: i.tkObject.frame.config(background="#e8e8e8")


global saved
def save(ret = False):
    global saved
    global whiteMoves
    saveList = []
    for i in Square.instances:
        saveList.append(dict(i.__dict__))
    saved = (saveList, whiteMoves)
    if ret: return saved

def load(toLoad = None):
    global saved
    global whiteMoves
    if toLoad is not None:
        save1 = toLoad
    else:
        save1 = saved
    if save1[1] is not whiteMoves: switchMover()
    for index, i in enumerate(Square.instances):
        i.setPiece(save1[0][index].get("figure"))
        if save1[0][index].get("hasMoved") is False: i.hasMoved = False
    reloadAvailability()

def sendText(text):
    textOut.delete(0, END)
    textOut.insert(END, text)

def unselect():     # Needed for debug menu
    global pieceSelected
    sendText("Piece unselected")
    if pieceSelected.black is True: pieceSelected.tkObject.frame.config(highlightbackground="black", highlightthickness=3)
    if pieceSelected.black is False: pieceSelected.tkObject.frame.config(highlightbackground="gray", highlightthickness=2)
    pieceSelected = None
    reloadAvailability()

def restart():      # Needed for debug menu
    setup()

# =====================================================================================
#                                         GUI
# =====================================================================================
root = Tk()
root.geometry("700x700")
frame = Frame(root, height=60, width=640)
frame.pack()
board = Frame(root, width=640, height=640, background="#000000")
board.pack()
board.pack_propagate(0)  # В PyCharm Можно свернуть кучу строк, выберите строки с 429 по 501 и нажмите CTRL + .

square_a8 = Frame(board, background="#e8e8e8", width=80, height=80)
square_a7 = Frame(board, background="#999999", width=80, height=80)
square_a6 = Frame(board, background="#e8e8e8", width=80, height=80)
square_a5 = Frame(board, background="#999999", width=80, height=80)
square_a4 = Frame(board, background="#e8e8e8", width=80, height=80)
square_a3 = Frame(board, background="#999999", width=80, height=80)
square_a2 = Frame(board, background="#e8e8e8", width=80, height=80)
square_a1 = Frame(board, background="#999999", width=80, height=80)

square_b8 = Frame(board, background="#999999", width=80, height=80)
square_b7 = Frame(board, background="#e8e8e8", width=80, height=80)
square_b6 = Frame(board, background="#999999", width=80, height=80)
square_b5 = Frame(board, background="#e8e8e8", width=80, height=80)
square_b4 = Frame(board, background="#999999", width=80, height=80)
square_b3 = Frame(board, background="#e8e8e8", width=80, height=80)
square_b2 = Frame(board, background="#999999", width=80, height=80)
square_b1 = Frame(board, background="#e8e8e8", width=80, height=80)

square_c8 = Frame(board, background="#e8e8e8", width=80, height=80)
square_c7 = Frame(board, background="#999999", width=80, height=80)
square_c6 = Frame(board, background="#e8e8e8", width=80, height=80)
square_c5 = Frame(board, background="#999999", width=80, height=80)
square_c4 = Frame(board, background="#e8e8e8", width=80, height=80)
square_c3 = Frame(board, background="#999999", width=80, height=80)
square_c2 = Frame(board, background="#e8e8e8", width=80, height=80)
square_c1 = Frame(board, background="#999999", width=80, height=80)

square_d8 = Frame(board, background="#999999", width=80, height=80)
square_d7 = Frame(board, background="#e8e8e8", width=80, height=80)
square_d6 = Frame(board, background="#999999", width=80, height=80)
square_d5 = Frame(board, background="#e8e8e8", width=80, height=80)
square_d4 = Frame(board, background="#999999", width=80, height=80)
square_d3 = Frame(board, background="#e8e8e8", width=80, height=80)
square_d2 = Frame(board, background="#999999", width=80, height=80)
square_d1 = Frame(board, background="#e8e8e8", width=80, height=80)

square_e8 = Frame(board, background="#e8e8e8", width=80, height=80)
square_e7 = Frame(board, background="#999999", width=80, height=80)
square_e6 = Frame(board, background="#e8e8e8", width=80, height=80)
square_e5 = Frame(board, background="#999999", width=80, height=80)
square_e4 = Frame(board, background="#e8e8e8", width=80, height=80)
square_e3 = Frame(board, background="#999999", width=80, height=80)
square_e2 = Frame(board, background="#e8e8e8", width=80, height=80)
square_e1 = Frame(board, background="#999999", width=80, height=80)

square_f8 = Frame(board, background="#999999", width=80, height=80)
square_f7 = Frame(board, background="#e8e8e8", width=80, height=80)
square_f6 = Frame(board, background="#999999", width=80, height=80)
square_f5 = Frame(board, background="#e8e8e8", width=80, height=80)
square_f4 = Frame(board, background="#999999", width=80, height=80)
square_f3 = Frame(board, background="#e8e8e8", width=80, height=80)
square_f2 = Frame(board, background="#999999", width=80, height=80)
square_f1 = Frame(board, background="#e8e8e8", width=80, height=80)

square_g8 = Frame(board, background="#e8e8e8", width=80, height=80)
square_g7 = Frame(board, background="#999999", width=80, height=80)
square_g6 = Frame(board, background="#e8e8e8", width=80, height=80)
square_g5 = Frame(board, background="#999999", width=80, height=80)
square_g4 = Frame(board, background="#e8e8e8", width=80, height=80)
square_g3 = Frame(board, background="#999999", width=80, height=80)
square_g2 = Frame(board, background="#e8e8e8", width=80, height=80)
square_g1 = Frame(board, background="#999999", width=80, height=80)

square_h8 = Frame(board, background="#999999", width=80, height=80)
square_h7 = Frame(board, background="#e8e8e8", width=80, height=80)
square_h6 = Frame(board, background="#999999", width=80, height=80)
square_h5 = Frame(board, background="#e8e8e8", width=80, height=80)
square_h4 = Frame(board, background="#999999", width=80, height=80)
square_h3 = Frame(board, background="#e8e8e8", width=80, height=80)
square_h2 = Frame(board, background="#999999", width=80, height=80)
square_h1 = Frame(board, background="#e8e8e8", width=80, height=80)  # square_XX Defined

for i in [
    "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
    "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
    "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8",
    "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"
]:  # Yep, That's a mess, it creates a menu inside each cell
    b = i  # Might be useless, but i'll add it anyway to be sure,   just so {i} used for the class doesn't get mixed up
    exec(f"{i}_figure = Text(square_{i}, width=2, height=1, bg=\'lightgray\', font=(\'arial\', 25))")  # Menu part
    exec(f"{i}_figure.grid(row=1, column=0)")
    exec(f"{i}_label = Label(square_{i}, text=\"{i}\", width=3, height=1)")
    # exec(f"{i}_label.grid(row=2, column=0)")
    exec(f"{i}_button = Button(square_{i}, text=\"SEL\", width=4, height=1)")
    exec(f"{i}_button.grid(row=3, column=0)")
    exec(f"{i}_output = Label(square_{i}, width=8,height=1)")
    # exec(f"{i}_output.grid(row=3,column=0, columnspan=2)")
    exec(f"square_{i}.config(highlightbackground=\"black\")")
    exec(f"square_{i}.config(highlightthickness=3)")
    temp = toCoords(i)
    exec(
        f"{b}_object = SquareObj({b}_figure, {b}_label, {b}_button, {b}_output, square_{b})")  # Creates a SquareObj instance, to access tkinter elements using that class
    exec(f"{b} = None")
    exec(
        f"{b} = Square(\"{i}\", None, {b}_object)")  # Creates Square instance(Not fully) and places SquareObj instance there
    exec(f"{i}_button.config(command=lambda: select({i}))")
    boardList[temp[0]].append(i)

revBoardList = boardList.reverse()

exitButton = Button(frame, text="Exit", command=root.destroy)  # Верхние кнопки
textOut = Entry(frame, width=30)
label = Label(frame, text="Chess")
console = Entry(frame, width=30)
confirmButton = Button(frame, text="Submit", command=func)

exitButton.grid(column=4, row=0, )  # Упаковка верхних кнопок
textOut.grid(column=3, row=0)
label.grid(column=2, row=0)
console.grid(column=1, row=0)
confirmButton.grid(column=0,
                   row=0)  # Дальше тоже нужно сворачивать, 546 - 616, 618-681, мог бы сделать через for, но это было сделано ещё в начале написания кода

square_a8.grid(column=0, row=0)
square_a7.grid(column=0, row=1)
square_a6.grid(column=0, row=2)
square_a5.grid(column=0, row=3)
square_a4.grid(column=0, row=4)
square_a3.grid(column=0, row=5)
square_a2.grid(column=0, row=6)
square_a1.grid(column=0, row=7)

square_b8.grid(column=1, row=0)
square_b7.grid(column=1, row=1)
square_b6.grid(column=1, row=2)
square_b5.grid(column=1, row=3)
square_b4.grid(column=1, row=4)
square_b3.grid(column=1, row=5)
square_b2.grid(column=1, row=6)
square_b1.grid(column=1, row=7)

square_c8.grid(column=2, row=0)
square_c7.grid(column=2, row=1)
square_c6.grid(column=2, row=2)
square_c5.grid(column=2, row=3)
square_c4.grid(column=2, row=4)
square_c3.grid(column=2, row=5)
square_c2.grid(column=2, row=6)
square_c1.grid(column=2, row=7)

square_d8.grid(column=3, row=0)
square_d7.grid(column=3, row=1)
square_d6.grid(column=3, row=2)
square_d5.grid(column=3, row=3)
square_d4.grid(column=3, row=4)
square_d3.grid(column=3, row=5)
square_d2.grid(column=3, row=6)
square_d1.grid(column=3, row=7)

square_e8.grid(column=4, row=0)
square_e7.grid(column=4, row=1)
square_e6.grid(column=4, row=2)
square_e5.grid(column=4, row=3)
square_e4.grid(column=4, row=4)
square_e3.grid(column=4, row=5)
square_e2.grid(column=4, row=6)
square_e1.grid(column=4, row=7)

square_f8.grid(column=5, row=0)
square_f7.grid(column=5, row=1)
square_f6.grid(column=5, row=2)
square_f5.grid(column=5, row=3)
square_f4.grid(column=5, row=4)
square_f3.grid(column=5, row=5)
square_f2.grid(column=5, row=6)
square_f1.grid(column=5, row=7)

square_g8.grid(column=6, row=0)
square_g7.grid(column=6, row=1)
square_g6.grid(column=6, row=2)
square_g5.grid(column=6, row=3)
square_g4.grid(column=6, row=4)
square_g3.grid(column=6, row=5)
square_g2.grid(column=6, row=6)
square_g1.grid(column=6, row=7)

square_h8.grid(column=7, row=0)
square_h7.grid(column=7, row=1)
square_h6.grid(column=7, row=2)
square_h5.grid(column=7, row=3)
square_h4.grid(column=7, row=4)
square_h3.grid(column=7, row=5)
square_h2.grid(column=7, row=6)
square_h1.grid(column=7, row=7)  # square_XX.grid(...) Placing all squares in a grid

square_a8.grid_propagate(0)
square_a7.grid_propagate(0)
square_a6.grid_propagate(0)
square_a5.grid_propagate(0)
square_a4.grid_propagate(0)
square_a3.grid_propagate(0)
square_a2.grid_propagate(0)
square_a1.grid_propagate(0)
square_b8.grid_propagate(0)
square_b7.grid_propagate(0)
square_b6.grid_propagate(0)
square_b5.grid_propagate(0)
square_b4.grid_propagate(0)
square_b3.grid_propagate(0)
square_b2.grid_propagate(0)
square_b1.grid_propagate(0)
square_c8.grid_propagate(0)
square_c7.grid_propagate(0)
square_c6.grid_propagate(0)
square_c5.grid_propagate(0)
square_c4.grid_propagate(0)
square_c3.grid_propagate(0)
square_c2.grid_propagate(0)
square_c1.grid_propagate(0)
square_d8.grid_propagate(0)
square_d7.grid_propagate(0)
square_d6.grid_propagate(0)
square_d5.grid_propagate(0)
square_d4.grid_propagate(0)
square_d3.grid_propagate(0)
square_d2.grid_propagate(0)
square_d1.grid_propagate(0)
square_e8.grid_propagate(0)
square_e7.grid_propagate(0)
square_e6.grid_propagate(0)
square_e5.grid_propagate(0)
square_e4.grid_propagate(0)
square_e3.grid_propagate(0)
square_e2.grid_propagate(0)
square_e1.grid_propagate(0)
square_f8.grid_propagate(0)
square_f7.grid_propagate(0)
square_f6.grid_propagate(0)
square_f5.grid_propagate(0)
square_f4.grid_propagate(0)
square_f3.grid_propagate(0)
square_f2.grid_propagate(0)
square_f1.grid_propagate(0)
square_g8.grid_propagate(0)
square_g7.grid_propagate(0)
square_g6.grid_propagate(0)
square_g5.grid_propagate(0)
square_g4.grid_propagate(0)
square_g3.grid_propagate(0)
square_g2.grid_propagate(0)
square_g1.grid_propagate(0)
square_h8.grid_propagate(0)
square_h7.grid_propagate(0)
square_h6.grid_propagate(0)
square_h5.grid_propagate(0)
square_h4.grid_propagate(0)
square_h3.grid_propagate(0)
square_h2.grid_propagate(0)
square_h1.grid_propagate(0)  # square_XX.grid_propagate(0), so they have a fixed size

menubar = Menu(root, tearoff=0)
turnToggle = BooleanVar()
turnToggle.set(True)
pieceColor = StringVar()
pieceColor.set("w")
everythingSelectable = BooleanVar()
everythingSelectable.set(False)

settings_menu = Menu(menubar)
settings_menu.add_checkbutton(label="Turn the board on move", onvalue=1, offvalue=0, variable=turnToggle)
settings_menu.add_checkbutton(label="Do NOT turn the board", onvalue=0, offvalue=1, variable=turnToggle)
settings_menu.add_command(label="Force turn the board", command = turn)
menubar.add_cascade(label='Settings', menu=settings_menu)

menubar.add_command(label="Style", command=figureMode)
menubar.add_command(label="Reload", command=reloadAvailability)
menubar.add_separator()

debug_menu = Menu(menubar)
debug_menu.add_command(label="For debug (maybe cheating) purposes only!")
debug_menu.add_checkbutton(label="Debug <- press this", onvalue=1, offvalue=0, variable=everythingSelectable)
debug_menu.add_separator()
debug_menu.add_command(label="switchMover()", command = switchMover)
debug_menu.add_separator()
debug_menu.add_command(label="Save", command = save)
debug_menu.add_command(label="Load", command = load)
debug_menu.add_separator()
debug_menu.add_checkbutton(label="Set White pieces", onvalue="w", offvalue="b", variable=pieceColor)
debug_menu.add_checkbutton(label="Set Black pieces", onvalue="b", offvalue="w", variable=pieceColor)
debug_menu.add_command(label="Reload", command=reloadAvailability)
debug_menu.add_command(label="Everything selectable (Only in debug mode)", command = lambda: exec("for i in Square.instances: i.selectable(True)"))
debug_menu.add_command(label="Unselect piece", command=unselect)
debug_menu.add_separator()
debug_menu.add_command(label="These ones work on the selected piece")
debug_menu.add_command(label="Force hasMoved False", command = lambda: exec("pieceSelected.hasMoved = False"))
debug_menu.add_command(label="SetPiece pawn", command = lambda: pieceSelected.setPiece(pieceColor.get() + "p"))
debug_menu.add_command(label="SetPiece rook", command = lambda: pieceSelected.setPiece(pieceColor.get() + "r"))
debug_menu.add_command(label="SetPiece knight", command = lambda: pieceSelected.setPiece(pieceColor.get() + "k"))
debug_menu.add_command(label="SetPiece bishop", command = lambda: pieceSelected.setPiece(pieceColor.get() + "b"))
debug_menu.add_command(label="SetPiece queen", command = lambda: pieceSelected.setPiece(pieceColor.get() + "q"))
debug_menu.add_command(label="SetPiece king", command = lambda: pieceSelected.setPiece(pieceColor.get() + "a"))
debug_menu.add_separator()
debug_menu.add_command(label="RESTART", command = restart)
menubar.add_cascade(label='Debug', menu=debug_menu)

root.config(menu = menubar)


# =====================================================
#                 Some value setup
# =====================================================
zipBoard = []  # Шахматный порядок
emptyList = [None, None, None, None, None, None, None, None]
for a, b, c, d, e, f, g, h, i in zip(boardList[0], boardList[1], boardList[2], boardList[3], boardList[4], boardList[5],
                                     boardList[6], boardList[7], emptyList):
    zipBoard.append(a)
    zipBoard.append(b)
    zipBoard.append(c)
    zipBoard.append(d)
    zipBoard.append(e)
    zipBoard.append(f)
    zipBoard.append(g)
    zipBoard.append(h)
    zipBoard.append(i)

for i in zipBoard:
    if i == None:
        pass
    elif zipBoard.index(i) % 2 == 1:  # Add black = True
        exec(f"sq = {i}")
        sq.black = True

# =====================================================
#                 Game setup
# =====================================================

global piecePlacement
piecePlacement = [
    ["br", "bk", "bb", "bq", "ba", "bb", "bk", "br"],
    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
    ["wr", "wk", "wb", "wq", "wa", "wb", "wk", "wr"],
]


def setup():
    global piecePlacement
    global whiteMoves
    placement = piecePlacement[::-1]
    for index, i in enumerate(Square.instances):
        index = (index % 8, index // 8)
        if placement[index[0]][index[1]] != "--":
            i.setPiece(placement[index[0]][index[1]])
            i.hasMoved = False
        if placement[index[0]][index[1]] == "--":
            i.setPiece("none")
            i.hasMoved = False
    whiteMoves = True
    for i in Square.instances:
        if i.black is True: i.tkObject.frame.config(highlightbackground="black", highlightthickness=3)
        if i.black is False: i.tkObject.frame.config(highlightbackground="gray", highlightthickness=2)
        if i.black is True: i.tkObject.frame.config(background="#999999")
        if i.black is False: i.tkObject.frame.config(background="#e8e8e8")

    reloadAvailability()


setup()

root.title("PAAAAAAIN")
root.mainloop()
exit()
