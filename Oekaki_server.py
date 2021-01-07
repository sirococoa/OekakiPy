from collections import deque

from twisted.internet import reactor, task
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


class OekakiServer(LineReceiver):
    def __init__(self, paint_que):
        super().__init__()
        self.paint_que = paint_que

    def connectionMade(self):
        print("接続受付", self.transport.client)
        self.factory.clientConnectionMade(self)

    def connectionLost(self, reason):
        print(self.transport.client, '接続解除')
        self.factory.clientConnectionLost(self)

    def lineReceived(self, line):
        print(line)
        self.paint_que.append((self, ) + tuple(map(int, str(line, 'utf-8').split(' '))))


class OekakiFactory(Factory):
    def __init__(self):
        self.clients = []
        self.paint_que = deque()
        self.lc = task.LoopingCall(self.loop_process)
        self.lc.start(0.1)

    def loop_process(self):
        while self.paint_que:
            painter, id, x, y, color = self.paint_que.popleft()
            for client in self.clients:
                if client == painter:
                    client.sendLine(bytes('conf ' + str(id), 'utf-8'))
                else:
                    client.sendLine(bytes('draw ' + " ".join(map(str, (x, y, color))), 'utf-8'))

    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)

    def buildProtocol(self, addr):
        protocol = OekakiServer(self.paint_que)
        protocol.factory = self
        return protocol


factory = OekakiFactory()

reactor.listenTCP(1234, factory)
reactor.run()
