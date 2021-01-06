from collections import deque

from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory


class OekakiServer(Protocol):
    def __init__(self):
        super().__init__()
        self.paint_que = deque()

    def connectionMade(self):
        print("接続受付", self.transport.client)

    def connectionLost(self, reason):
        print(self.transport.client, '接続解除')

    def dataReceived(self, data):
        print(data)
        self.paint_que.append(tuple(map(int, str(data, 'utf-8').split(' '))))


factory = Factory()
factory.protocol = OekakiServer

reactor.listenTCP(1234, factory)
reactor.run()
