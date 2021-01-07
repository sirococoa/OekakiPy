from collections import deque, defaultdict
import itertools

from twisted.internet import reactor, task
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

WINDOW_SIZE = 256


class OekakiServer(LineReceiver):
    def __init__(self, paint_que):
        super().__init__()
        self.paint_que = paint_que
        self.room = -1

    def connectionMade(self):
        print("接続受付", self.transport.client)
        self.factory.clientConnectionMade(self)

    def connectionLost(self, reason):
        print(self.transport.client, '接続解除')
        self.factory.clientConnectionLost(self)

    def lineReceived(self, line):
        print(line)
        if self.room == -1:
            number = int(str(line, 'utf-8'))
            if number >= 0:
                self.factory.enter_room(self, number)
        else:
            self.paint_que[self.room].append((self, ) + tuple(map(int, str(line, 'utf-8').split(' '))))


class OekakiFactory(Factory):
    def __init__(self):
        self.clients = []
        self.canvas = defaultdict(OekakiFactory.init_canvas)
        self.paint_que = defaultdict(deque)
        self.visitor_number = defaultdict(int)
        self.lc = task.LoopingCall(self.loop_process)
        self.lc.start(0.1)

    def loop_process(self):
        for room, visitors in self.visitor_number.items():
            if visitors == 0:
                continue
            while self.paint_que[room]:
                painter, id, x, y, color = self.paint_que[room].popleft()
                self.canvas[room][x][y] = color
                for client in self.clients:
                    if client.room != room:
                        continue
                    if client == painter:
                        client.sendLine(bytes('conf ' + str(id), 'utf-8'))
                    else:
                        client.sendLine(bytes('draw ' + " ".join(map(str, (x, y, color))), 'utf-8'))

    def enter_room(self, client, number):
        if number < 0:
            return -1
        client.room = number
        self.visitor_number[number] += 1
        self.send_canvas(client)

    def send_canvas(self, client):
        client.sendLine(bytes(' '.join(map(str, itertools.chain.from_iterable(self.canvas[client.room]))), 'utf-8'))

    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)
        if client.room >= 0:
            self.visitor_number[client.room] -= 1
        if self.visitor_number[client.room] == 0:
            self.canvas[client.room] = self.init_canvas()

    def buildProtocol(self, addr):
        protocol = OekakiServer(self.paint_que)
        protocol.factory = self
        return protocol

    @classmethod
    def init_canvas(cls):
        return [[0 for _ in range(WINDOW_SIZE)] for _ in range(WINDOW_SIZE)]


factory = OekakiFactory()

reactor.listenTCP(1234, factory)
reactor.run()
