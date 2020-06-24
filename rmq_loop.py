import os
import signal
import time
import argparse
import random
import psutil
import pika

#the arguments are optional
parser = argparse.ArgumentParser(description='fork')
parser.add_argument('-t', action='store',
  help='timelimit')
parser.add_argument('-w', action='store',
  help='waitlimit')
args = parser.parse_args()



global child_exited

def list_child():
    current_process = psutil.Process()
    children = current_process.children(recursive=True)


    if not children:
        print("NO CHILDREN")

    for child in children:
        print('Child pid is {}'.format(child.pid))


def sigh(signum, frame):
    global child_exited

    if signum == signal.SIGCHLD:
        (pid, status) = os.waitpid(-1, 0)
        print ("(SIGCHLD) child exited with status: " + str(os.WEXITSTATUS(status)), pid)
        child_exited = True


#connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',blocked_connection_timeout=5))
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel=connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='direct')
result=channel.queue_declare(queue='',exclusive=True)
channel.queue_bind(exchange='logs', queue=result.method.queue, routing_key='pi-point')

child_exited = False
while 1:
    sleep_time = random.randint(3,6 )
    pid_child = os.fork()

    if(pid_child !=0):
        # set up SIGCHLD signal handler
        signal.signal(signal.SIGCHLD, sigh)

        # process diagnostics
        print("")
        print("PARENT CHILD: %d %d"% (os.getpid(), pid_child))
        list_child()

        # RMQ step 1: add RMqueue cheching to this call (signal? function?, etc.)
        # YYY can RMQ use a blocking connection with a timeout and catch SIGCHLD?
        #time.sleep(5)
        for method, properties, body in channel.consume('', inactivity_timeout =4.5):
                print("consume over")
                if(body)!=None:
                        print(body)
                break
        # set up connection variables like timeout
        # connection = pika.BlockingConnection()

        # we are here if one of three things are true
        # 1. we need to receive a RabbitMQ message
        # 2. we need to kill our child process because it's running too long
        # 3. We received a SIGCHLD and need to clean up
        # RMQ step 2: consume all messages from queue, print to screen
        #XXX: if rabbitmq signal recieved (global bool):
                # print out mesage to screen
                # continue (don't worry about sleep time calc)

        if not child_exited:
          print ("***kill child***", pid_child)
          os.kill(pid_child, signal.SIGKILL)


        #debug reasons
        list_child()

        #XXX: switch back rabbitmq bool
        child_exited = False
        continue


    # no changes to child for RabbitMQ at the moment
    if pid_child == 0:
        print("CHILD SLEEP: %d %d" % (os.getpid(),sleep_time))
        time.sleep(sleep_time)
        print("CHILD SLEEP DONE")
        exit(0)
