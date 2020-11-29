import random
from dataclasses import dataclass
from tkinter import *


@dataclass
class Tile:
    x: int
    y: int
    is_covered: bool = True
    is_mine: bool = False
    count: int = 0


class Minesweeper:
    def __init__(self, size, num_mines):
        self.size = size
        self.num_mines = num_mines

        self.tiles = {(x, y): Tile(x, y)
                      for x in range(self.size) for y in range(self.size)}
        self._place_mines()

    def _iter_neighbours(self, tile):
        (x, y) = (tile.x, tile.y)
        return (self.tiles[(dx, dy)]
                for (dx, dy) in [(x-1, y-1), (x, y-1), (x+1, y-1),
                                 (x-1, y),             (x+1, y),
                                 (x-1, y+1), (x, y+1), (x+1, y+1)]
                if (dx, dy) in self.tiles)

    def _place_mines(self):
        for tile in random.sample(list(self.tiles.values()), self.num_mines):
            tile.is_mine = True
            for neighbour in self._iter_neighbours(tile):
                neighbour.count += 1

    def _uncover(self, tile):
        if tile.is_covered:
            tile.is_covered = False
            yield tile

            if tile.count == 0:
                for neighbour in self._iter_neighbours(tile):
                    yield from self._uncover(neighbour)

    def step(self, x, y):
        yield from self._uncover(self.tiles[(x, y)])


class GUI:
    def __init__(self, tile_size=40):
        self.tile_size = tile_size
        self.tiles = {}

        self.tk = Tk()

        frame = Frame(self.tk, borderwidth=2, relief=RAISED)
        frame.pack(side=LEFT)

        self.canvas = Canvas(frame)
        self.canvas.pack(side=LEFT)

        self.canvas.bind('<Button-1>', self.step)
        self.canvas.bind('<Button-3>', self.toggle_flag)

        frame = Frame(self.tk)
        frame.pack(side=LEFT)

        button = Button(self.tk, text='Quit', command=self.tk.quit)
        button.pack(side=BOTTOM, fill=X)

        button = Button(self.tk, text='New Game', command=self.new_game)
        button.pack(side=BOTTOM, fill=X)

        self.tk.bind('<KeyPress-space>', self.new_game)

        self.size = 10
        self.num_mines = 10

        self.new_game()

    def new_game(self, event=None):
        self.game = Minesweeper(self.size, self.num_mines)
        self.covers = {}
        self.flags = {}

        self.canvas.delete('covers')
        self.canvas.delete('board')

        sz = self.tile_size

        self.canvas.config(width=self.size*sz, height=self.size*sz)

        self.create_board()

        rect = self.canvas.create_rectangle
        for (x, y) in self.game.tiles:
            cover = rect(x*sz, y*sz, (x+1)*sz, (y+1)*sz,
                         fill='gray60', tag='covers')
            
            self.covers[(x, y)] = cover

    def tile_xy(self, event):
        return (event.x // self.tile_size, event.y // self.tile_size)

    def step(self, event):
        x, y = self.tile_xy(event)

        if (x, y) not in self.flags:
            for tile in self.game.step(x, y):
                self.canvas.delete(self.covers.pop((tile.x, tile.y)))

                if tile.is_mine:
                    # Game over!
                    self.canvas.itemconfigure('covers', stipple='gray25')

    def toggle_flag(self, event):
        x, y = self.tile_xy(event)

        try:
            self.canvas.delete(self.flags.pop((x, y)))
        except KeyError:
            if self.game.tiles[(x, y)].is_covered:
                sz = self.tile_size
                rect = self.canvas.create_rectangle
                self.flags[x, y] = rect((x + 0.2) * sz, (y + 0.1) * sz,
                                        (x + 0.8) * sz, (y + 0.5) * sz,
                                        tag='board',
                                        fill='white')

    def create_board(self):
        sz = self.tile_size

        for (x, y), tile in self.game.tiles.items():
            if tile.is_mine:
                self.canvas.create_oval((x + 0.2) * sz, (y + 0.2) * sz,
                                        (x + 0.8) * sz, (y + 0.8) * sz,
                                        fill='black',
                                        tag='board')
            elif tile.count > 0:
                self.canvas.create_text((x + 0.5) * sz,
                                        (y + 0.5) * sz,
                                        text=repr(tile.count),
                                        anchor='center',
                                        tag='board')

    def mainloop(self):
        self.tk.mainloop()

gui = GUI()
gui.mainloop()
