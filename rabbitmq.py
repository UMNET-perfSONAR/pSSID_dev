#!/usr/bin/python
"""
Send a result to RabbitMQ.
"""
import pika
import datetime
import sys

log_prefix="archiver-rabbitmq"

#Stuff from the pscheduler archiver. Might be used later
'''class PikaConnectionChannelPair:
    """
    This class implements a RabbitMQ connection and channel pair
    """

    def __init__(self, data):

        self.connection = pika.BlockingConnection(pika.URLParameters(data["_url"]))
        self.channel = self.connection.channel()
        self.exchange = data.get("exchange", "")
        self.routing_key = data.get("routing-key", "")

    def publish(self, message):

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.routing_key,
                                   body=message)

    def __del__(self):

        self.channel.close()
        seld.connection.close()
'''

connection = pika.BlockingConnection(pika.URLParameters("amqp://elastic:elastic@elastic"))
channel = connection.channel()
message = input("Enter the message: ")
channel.basic_publish("", "pscheduler_raw", body = message)
channel.close()
connection.close()
