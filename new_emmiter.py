import pika
import json
import sys

connection = pika.BlockingConnection(pika.URLParameters("amqp://hi:hi@pi-point:5672"))
channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='direct')
ins = json.load(sys.stdin)
channel.basic_publish(exchange = 'logs', routing_key='pi-point', body  = json.dumps(ins))
print("[x] Sent %r" % ins)
connection.close()
