from __future__ import print_function, unicode_literals
import optparse
from proton import Message
from proton.handlers import MessagingHandler

"""
Proton event Handler class
Establishes an amqp connection and creates an amqp sender link to transmit messages
"""


class MessageProducer(MessagingHandler):
    def __init__(self, urls, queue_name, total, username, password):
        super(MessageProducer, self).__init__()

        # the solace message broker amqp url
        self.urls = urls
        # authentication credentials
        self.username = username
        self.password = password

        # the prefix amqp address for a solace topic
        self.queue_name = queue_name

        self.total = total
        self.sent = 0
        self.confirmed = 0

    def on_start(self, event):
        conn = event.container.connect(urls=self.urls,
                                       user=self.username,
                                       password=self.password,
                                       allow_insecure_mechs=True)

        # creates sender link to transfer message to the broker
        event.container.create_sender(conn, target=self.queue_name)

    def on_sendable(self, event):
        while event.sender.credit and self.sent < self.total:
            # the durable property on the message sends the message as a persistent message
            body = "Message from smoke test app " + str(self.sent)
            event.sender.send(Message(body, durable=True))
            self.sent += 1

    def on_accepted(self, event):
        self.confirmed += 1
        if self.confirmed == self.total:
            print('confirmed all messages')
            event.connection.close()

    def on_rejected(self, event):
        print("Broker", self.urls, "Reject message:", event.delivery.tag, "Remote disposition:",
              event.delivery.remote.condition)
        if self.confirmed == self.total:
            event.connection.close()

    # receives socket or authentication failures
    def on_transport_error(self, event):
        print("Transport failure for amqp broker:", self.urls, "Error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)
