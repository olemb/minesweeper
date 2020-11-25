import random
from dataclasses import dataclass
from tkinter import *


@dataclass
class Tile:
    x: int
    y: int
    covered: bool = True
    is_bomb: bool = False
    count: int = 0


class Minesweeper:
    def __init__(self, size, num_bombs, show_func, boom_func):
        self.size = size
        self.num_bombs = num_bombs

        self.tiles = {(x, y): Tile(x, y) for x in range(self.size) for y in range(self.size)}
        self._place_bombs()

        self.show_func = show_func
        self.boom_func = boom_func

        self.boom = False

    def iter_neighbours(self, x, y):
        for dx, dy in [(x-1,y-1), (x,y-1), (x+1,y-1),
                       (x-1,y),            (x+1,y),
                       (x-1,y+1), (x,y+1), (x+1,y+1)]:
            if (dx, dy) in self.tiles:
                yield (dx, dy)

    def _place_bombs(self):
        for (x, y) in random.sample(list(self.tiles), self.num_bombs):
            tile = self.tiles[(x, y)]
            tile.is_bomb = True
            for (dx, dy) in self.iter_neighbours(x, y):
                self.tiles[(dx, dy)].count += 1

    def _uncover(self, tile):
        if not tile.covered or tile.is_bomb:
            return

        tile.covered = False
        self.show_func(tile.x, tile.y)

        if tile.count == 0:
            for (dx, dy) in self.iter_neighbours(tile.x, tile.y):
                self._uncover(self.tiles[(dx, dy)])

    def step(self, x, y):
        tile = self.tiles[(x, y)]

        self._uncover(tile)
        if tile.is_bomb:
            self.boom = True
            self.boom_func()
  
    def toggle_flag(self, x, y):
        tile = self.tiles[(x, y)]
        tile.flagged = not tile.flagged
        return tile.flagged


class GUI:
    def __init__(self, tile_size=40):
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
        for (x, y) in self.game.tiles:
            tile = rect(x*sz, y*sz, (x+1)*sz, (y+1)*sz,
                        fill='gray60', tag='tiles')

            self.tiles[(x, y)] = tile

    def tile_xy(self, event):
        return (event.x // self.tile_size, event.y // self.tile_size)

    def step(self, event):
        x, y = self.tile_xy(event)

        if (x, y) not in self.flags:
            self.game.step(x, y)

    def toggle_flag(self, event):
        x, y = self.tile_xy(event)

        try:
            flag = self.flags[(x, y)]
            del self.flags[(x, y)]
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

                tile = self.game.tiles[(x, y)]

                if tile.is_bomb:
                    self.canvas.create_oval((x+0.2)*sz, (y+0.2)*sz,
                                            (x+0.8)*sz, (y+0.8)*sz,
                                            fill='black',
                                            tag='board')
                elif tile.count > 0:
                    self.canvas.create_text((x+0.5)*sz,
                                            (y+0.5)*sz,
                                            text=repr(tile.count),
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
