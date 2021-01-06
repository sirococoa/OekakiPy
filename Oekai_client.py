import pyxel

WINDOW_SIZE = 256


class App:
    def __init__(self):
        pyxel.init(WINDOW_SIZE, WINDOW_SIZE)
        self.canvas = [[0 for _ in range(WINDOW_SIZE)] for _ in range(WINDOW_SIZE)]
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        for x in range(WINDOW_SIZE):
            for y in range(WINDOW_SIZE):
                pyxel.pset(x, y, self.canvas[x][y])


if __name__ == '__main__':
    App()
