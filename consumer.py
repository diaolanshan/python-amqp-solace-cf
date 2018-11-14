from __future__ import print_function
import optparse
from proton.handlers import MessagingHandler
from proton.reactor import Container

"""
Proton event handler class
Creates an amqp connection using PLAIN authentication.
Then attaches a receiver link to conusme messages from the broker.
"""

class Recv(MessagingHandler):
    def __init__(self, urls, queue_name, expected, username, password):
        super(Recv, self).__init__()
        self.urls = urls

        # amqp node address
        self.username = username
        self.password = password
        self.queue_name = queue_name

        self.expected = expected
        self.received = 0

    def on_start(self, event):
        conn = event.container.connect(urls=self.urls,
                                       user=self.username,
                                       password=self.password,
                                       allow_insecure_mechs=True)
        event.container.create_receiver(conn, source=self.queue_name)

    def on_message(self, event):
        if event.message.id and event.message.id < self.received:
            # ignore duplicate message
            return
        if self.expected == 0 or self.received < self.expected:
            print(event.message.body)
            self.received += 1
            if self.received == self.expected:
                event.receiver.close()
                event.connection.close()

    # the on_transport_error event catches socket and authentication failures
    def on_transport_error(self, event):
        print("Transport error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)

    def on_disconnected(self, event):
        print("Disconnected")