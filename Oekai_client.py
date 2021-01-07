import socket

import pyxel

WINDOW_SIZE = 256


class App:
    def __init__(self):
        pyxel.init(WINDOW_SIZE, WINDOW_SIZE)
        pyxel.mouse(True)
        self.canvas = [[0 for _ in range(WINDOW_SIZE)] for _ in range(WINDOW_SIZE)]
        self.new_paint = []
        self.color = 7
        self.s = socket.socket()
        self.s.connect((socket.gethostname(), 1234))
        self.s.setblocking(False)
        self.send_data_id = 0
        self.recv_data = ''
        self.load_canvas()
        self.pre_mouse_x = pyxel.mouse_x
        self.pre_mouse_y = pyxel.mouse_y
        self.drawing = False
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
            if self.drawing:
                sx, sy = pyxel.mouse_x, pyxel.mouse_y
                gx, gy = self.pre_mouse_x, self.pre_mouse_y
                dx, dy = sx - gx, sy - gy
                if abs(dx) >= abs(dy):
                    if sx < gx:
                        for tx in range(sx, gx):
                            if dy/dx > 0:
                                ty = int(dy/dx*(tx - sx)+sy + 0.5)
                            else:
                                ty = int(dy / dx * (tx - sx) + sy - 0.5)
                            self.draw_pixel(tx, ty)
                    else:
                        for tx in range(gx, sx):
                            if dy / dx > 0:
                                ty = int(dy / dx * (tx - sx) + sy + 0.5)
                            else:
                                ty = int(dy / dx * (tx - sx) + sy - 0.5)
                            self.draw_pixel(tx, ty)
                else:
                    if sy < gy:
                        for ty in range(sy, gy):
                            if dx / dy > 0:
                                tx = int(dx/dy*(ty - sy)+sx + 0.5)
                            else:
                                tx = int(dx / dy * (ty - sy) + sx - 0.5)
                            self.draw_pixel(tx, ty)
                    else:
                        for ty in range(gy, sy):
                            if dx / dy > 0:
                                tx = int(dx / dy * (ty - sy) + sx + 0.5)
                            else:
                                tx = int(dx / dy * (ty - sy) + sx - 0.5)
                            self.draw_pixel(tx, ty)
            else:
                self.draw_pixel(pyxel.mouse_x, pyxel.mouse_y)
                self.drawing = True
        else:
            self.drawing = True
        self.pre_mouse_x = pyxel.mouse_x
        self.pre_mouse_y = pyxel.mouse_y
        try:
            self.recv_data += str(self.s.recv(1024), 'utf-8')
            # print("recv", self.recv_data)
            data = self.recv_data[:self.recv_data.rfind('\n')]
            self.recv_data = self.recv_data[self.recv_data.rfind('\n')+1:]
            for line in data.rstrip().split('\n'):
                line = line.split(' ')
                if line[0] == 'conf':
                    id = int(line[1])
                    # print("delete", id)
                    for i, x, y, c in self.new_paint:
                        if i == id:
                            self.canvas[x][y] = c
                    self.new_paint = [p for p in self.new_paint if p[0] != id]
                elif line[0] == 'draw':
                    x, y, c = map(int, line[1:])
                    self.canvas[x][y] = c
                else:
                    raise ValueError
        except BlockingIOError:
            pass

    def draw(self):
        for x in range(WINDOW_SIZE):
            for y in range(WINDOW_SIZE):
                pyxel.pset(x, y, self.canvas[x][y])
        for p in self.new_paint:
            pyxel.pset(*p[1:])

    def load_canvas(self):
        load_success = False
        while not load_success:
            try:
                self.recv_data += str(self.s.recv(1024), 'utf-8')
                if '\n' in self.recv_data:
                    data = self.recv_data[:self.recv_data.find('\n')]
                    self.recv_data = self.recv_data[self.recv_data.find('\n') + 1:]
                    load_success = True
                    data = data.split(' ')
                    for i in range(WINDOW_SIZE):
                        self.canvas[i] = data[WINDOW_SIZE*i:WINDOW_SIZE*(i+1)+1]
            except BlockingIOError:
                pass

    def draw_pixel(self, x, y):
        self.new_paint.append((self.send_data_id, x, y, self.color))
        self.s.send(bytes(' '.join(map(str, (self.send_data_id, x, y, self.color))), 'utf-8'))
        self.s.send(b'\r\n')
        self.send_data_id += 1

if __name__ == '__main__':
    App()
