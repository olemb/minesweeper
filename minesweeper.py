import random
from dataclasses import dataclass
from tkinter import *


@dataclass
class Tile:
    x: int
    y: int
    is_covered: bool = True
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

    def iter_neighbours(self, tile):
        (x, y) = (tile.x, tile.y)
        for dx, dy in [(x-1,y-1), (x,y-1), (x+1,y-1),
                       (x-1,y),            (x+1,y),
                       (x-1,y+1), (x,y+1), (x+1,y+1)]:
            try:
                yield self.tiles[(dx, dy)]
            except KeyError:
                pass

    def _place_bombs(self):
        for tile in random.sample(list(self.tiles.values()), self.num_bombs):
            tile.is_bomb = True
            for neighbour in self.iter_neighbours(tile):
                neighbour.count += 1

    def _uncover(self, tile):
        if not tile.is_covered or tile.is_bomb:
            return

        tile.is_covered = False
        self.show_func(tile.x, tile.y)

        if tile.count == 0:
            for neighbour in self.iter_neighbours(tile):
                self._uncover(neighbour)

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

        new_game = lambda event=None: self.new_game(self.size, self.num_bombs)
        button = Button(self.tk, text='New game', command=new_game)
        button.pack(side=BOTTOM, fill=X)

        self.tk.bind('<KeyPress-space>', new_game)

        self.new_game(10, 10)

    def new_game(self, size, num_bombs):
        self.tiles = {}
        self.flags = {}

        self.size = size
        self.num_bombs = num_bombs

        self.canvas.delete('tiles')
        self.canvas.delete('board')

        sz = self.tile_size

        self.canvas.config(width=size*sz, height=size*sz)
        self.game = Minesweeper(self.size, self.num_bombs,
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

        for (x, y), tile in self.game.tiles.items():
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
