import random
from dataclasses import dataclass
from tkinter import *


@dataclass
class Tile:
    x: int
    y: int
    is_mine: bool = False
    is_covered: bool = True
    is_flagged: bool = False
    count: int = 0


class Minesweeper:
    def __init__(self, size, num_mines):
        self.size = size
        self.num_mines = num_mines
        self.over = False

        self.tiles = {(x, y): Tile(x, y)
                      for x in range(self.size) for y in range(self.size)}
        self._place_mines()

    def _get_neighbours(self, tile):
        (x, y) = (tile.x, tile.y)
        return [self.tiles[(dx, dy)]
                for (dx, dy) in [(x-1, y-1), (x, y-1), (x+1, y-1),
                                 (x-1, y),             (x+1, y),
                                 (x-1, y+1), (x, y+1), (x+1, y+1)]
                if (dx, dy) in self.tiles]

    def _place_mines(self):
        for tile in random.sample(list(self.tiles.values()), self.num_mines):
            tile.is_mine = True
            for neighbour in self._get_neighbours(tile):
                neighbour.count += 1

    def _uncover(self, tile):
        if tile.is_covered:
            tile.is_covered = False

            if tile.count == 0:
                for neighbour in self._get_neighbours(tile):
                    self._uncover(neighbour)

    def step(self, tile):
        if not self.over and not tile.is_flagged:
            if tile.is_mine:
                self.over = True

            self._uncover(tile)

    def toggle_flag(self, tile):
        if not self.over:
            if tile.is_flagged:
                tile.is_flagged = False
            elif tile.is_covered:
                tile.is_flagged = True


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

    def get_event_tile(self, event):
        (x, y) = (event.x // self.tile_size, event.y // self.tile_size)
        return self.game.tiles[(x, y)]

    def new_game(self, event=None):
        self.game = Minesweeper(self.size, self.num_mines)
        self.update_display()

    def step(self, event):
        self.game.step(self.get_event_tile(event))
        self.update_display()

    def toggle_flag(self, event):
        self.game.toggle_flag(self.get_event_tile(event))
        self.update_display()

    def update_display(self):
        sz = self.tile_size
        self.canvas.config(width=self.size*sz, height=self.size*sz)
        self.canvas.delete('all')

        for (x, y), tile in self.game.tiles.items():
            if tile.is_mine:
                self.canvas.create_oval((x + 0.2) * sz, (y + 0.2) * sz,
                                        (x + 0.8) * sz, (y + 0.8) * sz,
                                        fill='black', tag='board')
            elif tile.count > 0:
                self.canvas.create_text((x + 0.5) * sz,
                                        (y + 0.5) * sz,
                                        anchor='center',
                                        text=repr(tile.count),
                                        tag='board')

            if tile.is_covered:
                self.canvas.create_rectangle(x*sz, y*sz, (x+1)*sz, (y+1)*sz,
                                             fill='gray60', tag='covers')

            if tile.is_flagged:
                self.canvas.create_rectangle(
                    (x + 0.2) * sz, (y + 0.1) * sz,
                    (x + 0.8) * sz, (y + 0.5) * sz,
                    fill='white', tag='board')

        if self.game.over:
            self.canvas.itemconfigure('covers', stipple='gray25')

    def mainloop(self):
        self.tk.mainloop()


gui = GUI()
gui.mainloop()
