from random import choice
from tkinter import *


tile_size = 20


class Minesweeper:
    def __init__(self, size, nbombs,
                 show_func=lambda x, y: None,
                 boom_func=lambda: None):
        self.size = size
        self.nbombs = nbombs

        self.board = {}
        self.hidden = {}

        self.hide_all()
        self.place_bombs()

        self.unknown = (size**2) - nbombs

        self.show_func = show_func
        self.boom_func = boom_func

        self.boom = 0

    def hide_all(self):
        hidden = self.hidden
        for x, y in self.all_coords():
            hidden[x, y] = 1        

    def all_coords(self):
        """Return the coordinates of all squares as a list."""
        coords = []
        for i in range(self.size**2):
            y, x = divmod(i, self.size)
            coords.append((x, y))
        return coords

    def place_bombs(self):
        squares = self.all_coords()
        board = self.board

        neighbours = [(-1,-1), (0,-1), (1,-1),
                      (-1,0), (0,0), (1,0),
                      (-1,1), (0,1), (1,1)]

        bombs = self.bombs = []                    # Place bombs
        for i in range(self.nbombs):
            square = choice(squares)
            squares.remove(square)
            bombs.append(square)

            x, y = square
            for dx, dy in neighbours:
                key = (x+dx, y+dy)
                try:
                    count = board[key]
                except KeyError:
                    count = 0
                board[key] = count + 1

        for key in bombs:
            board[key] = 'bomb'

    def show(self, x, y):
        del self.hidden[x, y]
        self.show_func(x, y)

        if self.board.get((x, y)) != None:
            return

        neighbours = [(x-1,y-1), (x,y-1), (x+1,y-1),
                      (x-1,y), (x,y), (x+1,y),
                      (x-1,y+1), (x,y+1), (x+1,y+1)]

        for x, y in neighbours:
            if (x, y) in self.hidden:
                if self.board.get(x, y) != 'bomb':
                    self.show(x, y)
            

    def step(self, x, y):
        c = self.board.get((x, y))

        if c == 'bomb':
            self.boom = 1
            self.hidden = {}
            self.boom_func()
        elif (x, y) in self.hidden:
            self.show(x, y)
            self.unknown = len(self.hidden) - self.nbombs




class GUI:
    def __init__(self):
        self.tile_size = tile_size
        self.tiles = {}

        self.tk = Tk()
        
        new_game = lambda e=None, s=self: s.new_game(s.size, s.nbombs)

        frame = Frame(self.tk,
                      borderwidth=2,
                      relief=RAISED)
        frame.pack(side=LEFT)

        self.canvas = Canvas(frame)
        self.canvas.pack(side=LEFT)

        self.canvas.bind('<Button-1>', self.step)
        self.canvas.bind('<Button-3>', self.toggle_flag)

        frame = Frame(self.tk)
        frame.pack(side=LEFT)

        button = Button(self.tk, text='Quit', command=self.tk.quit)
        button.pack(side=BOTTOM, fill=X)

        button = Button(self.tk, text='New game', command=new_game)
        button.pack(side=BOTTOM, fill=X)

        self.tk.bind('<KeyPress-space>', new_game)

        self.new_game(10, 10)

    def new_game(self, size, nbombs):
        self.tiles = {}
        self.flags = {}

        self.size = size
        self.nbombs = nbombs

        self.canvas.delete('tiles')
        self.canvas.delete('board')

        sz = self.tile_size

        self.canvas.config(width=size*sz, height=size*sz)
        self.game = Minesweeper(self.size, self.nbombs,
                                show_func=self.remove_tile,
                                boom_func=self.boom)

        self.create_board()

        rect = self.canvas.create_rectangle
        for x, y in self.game.all_coords():
            tile = rect(x*sz, y*sz, (x+1)*sz, (y+1)*sz,
                        fill='blue', tag='tiles')

            self.tiles[x, y] = tile

    def canvas_xy(self, event):
        sz = self.tile_size
        return (event.x // sz, event.y // sz)

    def step(self, event):
        x, y = self.canvas_xy(event)

        if (x, y) not in self.flags:
            self.game.step(x, y)

    def toggle_flag(self, event):
        x, y = self.canvas_xy(event)

        try:
            flag = self.flags[x, y]
            del self.flags[x, y]
            self.canvas.delete(flag)
        except KeyError:
            if (x, y) in self.tiles:
                sz = self.tile_size
                rect = self.canvas.create_rectangle
                flag = rect((x+0.2)*sz, (y+0.1)*sz,
                            (x+0.8)*sz, (y+0.5)*sz,
                            tag='board',
                            fill='white')
                self.flags[x, y] = flag

    def create_board(self):
        sz = self.tile_size

        for y in range(self.size):
            for x in range(self.size):

                c = self.game.board.get((x, y))
                if c == 'bomb':
                    self.canvas.create_oval((x+0.2)*sz, (y+0.2)*sz,
                                            (x+0.8)*sz, (y+0.8)*sz,
                                            fill='black',
                                            tag='board')
                elif c is not None:
                    self.canvas.create_text((x+0.5)*sz,
                                            (y+0.5)*sz,
                                            text=repr(c),
                                            anchor='center',
                                            tag='board')

    def boom(self):
        self.canvas.itemconfigure('tiles', stipple='gray25')

    def remove_tile(self, x, y):
        self.canvas.delete(self.tiles[x, y])
        del self.tiles[x, y]

    def mainloop(self):
        self.tk.mainloop()

gui = GUI()
gui.mainloop()
