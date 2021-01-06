from collections import deque

from twisted.internet import reactor, task
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


class OekakiServer(LineReceiver):
    def __init__(self):
        super().__init__()
        self.paint_que = deque()

    def connectionMade(self):
        print("接続受付", self.transport.client)
        self.factory.clientConnectionMade(self)

    def connectionLost(self, reason):
        print(self.transport.client, '接続解除')
        self.factory.clientConnectionLost(self)

    def lineReceived(self, line):
        print(line)
        self.paint_que.append(tuple(map(int, str(line, 'utf-8').split(' '))))

    def confirm_paint(self):
        while self.paint_que:
            id, x, y, color = self.paint_que.popleft()
            print("delete", id)
            self.sendLine(bytes('s' + str(id), 'utf-8'))


class OekakiFactory(Factory):
    protocol = OekakiServer

    def __init__(self):
        self.clients = []
        self.lc = task.LoopingCall(self.loop_process)
        self.lc.start(0.1)

    def loop_process(self):
        for client in self.clients:
            client.confirm_paint()

    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)


factory = OekakiFactory()

reactor.listenTCP(1234, factory)
reactor.run()
