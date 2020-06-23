#!/usr/bin/env python
import pika
import uuid
import json

class FibonacciRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='tasks', exchange_type='direct')
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        with open(n, "r") as read_file:
             data = json.load(read_file)
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='tasks',
            routing_key=data["destination"],
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(data))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


fibonacci_rpc = FibonacciRpcClient()

print(" [x] Requesting ")
response = fibonacci_rpc.call("hello.json")
print(" [.] Got %r" % response)
