import socket

import pyxel

WINDOW_SIZE = 256


def center(text, width):
    '''
    文章を中央揃えで表示する際のx座標を返す
    :param text: 座標を得たい文章
    :param width: 画面の幅
    :return:
    '''
    TEXT_W = 4
    return width // 2 - len(text) * TEXT_W // 2


class App:
    INPUT_COLL_TIME = 3

    def __init__(self):
        pyxel.init(WINDOW_SIZE, WINDOW_SIZE)
        self.canvas = [[0 for _ in range(WINDOW_SIZE)] for _ in range(WINDOW_SIZE)]
        self.new_paint = []
        self.color = 7
        self.s = socket.socket()
        host = socket.gethostname()
        self.s.connect((host, 1234))
        self.s.setblocking(False)
        self.send_data_id = 0
        self.recv_data = ''
        self.pre_mouse_x = pyxel.mouse_x
        self.pre_mouse_y = pyxel.mouse_y
        self.drawing = False
        self.state = 'lobby'
        self.room_number = ''
        self.input_cool_time = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.state == 'lobby':
            if self.input_cool_time == 0:
                for key, number in ((pyxel.KEY_0, 0), (pyxel.KEY_1, 1), (pyxel.KEY_2, 2), (pyxel.KEY_4, 4), (pyxel.KEY_3, 3), (pyxel.KEY_5, 5), (pyxel.KEY_6, 6), (pyxel.KEY_7, 7), (pyxel.KEY_8, 8), (pyxel.KEY_9, 9)):
                    if pyxel.btn(key):
                        self.room_number = str(number) + self.room_number
                        self.input_cool_time = self.INPUT_COLL_TIME
                        break
            else:
                self.input_cool_time -= 1
            if len(self.room_number) == 3:
                self.s.send(bytes(self.room_number, 'utf-8'))
                self.s.send(b'\r\n')
                self.state = 'room'
                self.load_canvas()
        elif self.state == 'room':
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
                if self.drawing:
                    sx, sy = pyxel.mouse_x, pyxel.mouse_y
                    gx, gy = self.pre_mouse_x, self.pre_mouse_y
                    dx, dy = sx - gx, sy - gy
                    if abs(dx) >= abs(dy):
                        if sx < gx:
                            for tx in range(sx, gx):
                                if dy / dx > 0:
                                    ty = int(dy / dx * (tx - sx) + sy + 0.5)
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
                                    tx = int(dx / dy * (ty - sy) + sx + 0.5)
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

            self.color += pyxel.mouse_wheel
            self.color = self.color % 16

            try:
                self.recv_data += str(self.s.recv(1024), 'utf-8')
                # print("recv", self.recv_data)
                data = self.recv_data[:self.recv_data.rfind('\n')]
                self.recv_data = self.recv_data[self.recv_data.rfind('\n') + 1:]
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
        if self.state == 'lobby':
            pyxel.cls(0)
            msg = 'enter the room number!'
            pyxel.text(center(msg, WINDOW_SIZE), WINDOW_SIZE//4, msg, 7)
            msg = ('___' + self.room_number)[-3:]
            pyxel.text(center(msg, WINDOW_SIZE), WINDOW_SIZE//2, msg, 7)
        elif self.state == 'room':
            for x in range(WINDOW_SIZE):
                for y in range(WINDOW_SIZE):
                    pyxel.pset(x, y, self.canvas[x][y])
            for p in self.new_paint:
                pyxel.pset(*p[1:])
            if pyxel.frame_count % 10 < 5:
                for i, j in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    pyxel.pset(pyxel.mouse_x + i, pyxel.mouse_y + j, self.color)

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
                        self.canvas[i] = data[WINDOW_SIZE * i:WINDOW_SIZE * (i + 1) + 1]
            except BlockingIOError:
                pass

    def draw_pixel(self, x, y):
        self.new_paint.append((self.send_data_id, x, y, self.color))
        self.s.send(bytes(' '.join(map(str, (self.send_data_id, x, y, self.color))), 'utf-8'))
        self.s.send(b'\r\n')
        self.send_data_id += 1


if __name__ == '__main__':
    App()
