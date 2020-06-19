import os
import signal
import time
import argparse
import random
import psutil


#the arguments are optional
parser = argparse.ArgumentParser(description='fork')
parser.add_argument('-t', action='store',
  help='timelimit')
parser.add_argument('-w', action='store',
  help='waitlimit')
args = parser.parse_args()



child_exited = False

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
   



while 1:
    sleep_time = random.randint(1, 10)
    pid_child = os.fork()
    
    if(pid_child !=0):
        signal.signal(signal.SIGCHLD, sigh)
        #XXX: rabbitmq signal handler here (a gloabl bool within to know rabbitmq signal received)
        
        #debug reasons
        print("")
        print("PARENT CHILD: %d %d"% (os.getpid(), pid_child))        
        list_child()
        
        time.sleep(5)
        
        #XXX: if rabbitmq signal recieved (global bool):
                #do something
        
        
        #XXX: resume parent sleep if necessary

        if not child_exited:
          print ("***kill child***", pid_child)
          os.kill(pid_child, signal.SIGKILL) 

        
        #debug reasons
        list_child()
        
        #XXX: switch back rabbitmq bool
        child_exited = False
        continue

    
    
    if pid_child == 0:
        print("CHILD SLEEP: %d %d" % (os.getpid(),sleep_time))
        time.sleep(sleep_time)
        exit(0)
          
    









