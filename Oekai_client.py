import socket

import pyxel

WINDOW_SIZE = 256


class App:
    def __init__(self):
        pyxel.init(WINDOW_SIZE, WINDOW_SIZE)
        self.canvas = [[0 for _ in range(WINDOW_SIZE)] for _ in range(WINDOW_SIZE)]
        self.new_paint = []
        self.color = 7
        self.s = socket.socket()
        self.s.connect((socket.gethostname(), 1234))
        self.send_data_id = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
            self.new_paint.append((pyxel.mouse_x, pyxel.mouse_y, self.color))
            self.s.send(bytes(' '.join(map(str, (self.send_data_id, pyxel.mouse_x, pyxel.mouse_y, self.color))), 'utf-8'))
            self.send_data_id += 1

    def draw(self):
        for x in range(WINDOW_SIZE):
            for y in range(WINDOW_SIZE):
                pyxel.pset(x, y, self.canvas[x][y])
        for p in self.new_paint:
            pyxel.pset(*p)


if __name__ == '__main__':
    App()
