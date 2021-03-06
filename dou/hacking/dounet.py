import sys
import os
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

DFT_BUFFEER_SIZE = 4096

def usage():
    print 'douglas\'s net tool'
    print
    print 'Usage: dounet.py -t targe_host -p port'
    print '-l --listen                  - listen on [host]:[port] for incoming connection'
    print '-e --execute=file_to_tun     - excute the given file upon receiving a connection'
    print '-c --command                 - intialize a command shell'
    print
    print 'Examples:'
    print 'dounet.py -t 192.168.0.1 -p 5555 -l -c'
    print 'dounet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe'
    print 'dounet.py -t 192.168.0.1 -p 5555 -l -e=\'cat /etc/passwd\''
    print 'echo \'ABCDEFG\' | ./dounet.py -t 192.168.0.1 -p 135'
    sys.exit(-1)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hle:t:p:cu:',
                ['help', 'lsiten', 'execute', 'targe', 'port', 'command', 'upload'])
    except getopt.GetoptError as error:
        print str(error)
        usage()

    for o,a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-e', '--execute'):
            execute = a
        elif o in ('-c', '--command'):
            command = True
        elif o in ('-u', '--upload'):
            upload_destination = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        else:
            assert False, 'unrecognized handler'

    if not listen and len(target) and port > 0:
        buf = sys.stdin.read()
        client_sender(buf)

    if listen:
        server_loop()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)
        while True:
            recv_len = 1
            response = ''
            while recv_len:
                data = client.recv(DFT_BUFFEER_SIZE)
                recv_len = len(data)
                response += data
                if recv_len < DFT_BUFFEER_SIZE:
                    break
            print response,

            buffer = raw_input('')
            buffer += '\n'
            client.send(buffer)

    except Exception, e:
        print 'exception caught:[%s]' % str(e)
        client.close()

def server_loop():
    global target
    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print 'get new connection'
        #client_handler(client_socket)
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    command = command.rstrip()
    print 'get command[%s]' % command
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except Exception, e:
        output = 'fail to execute command[%s], e[%s]' % (command, str(e))
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer = ''
    
        while True:
            data = client_socket.recv(DFT_BUFFEER_SIZE)

            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send('succeed to send save file to [%s]\n' % upload_destination)
        except Exception, e:
            client_socket.send('fail to save file to [%s]\n' % upload_destination)

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)


    if command:
        while True:
            client_socket.send('<dounet:> ')
            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(DFT_BUFFEER_SIZE)

            response = run_command(cmd_buffer)

            client_socket.send(response)


if __name__ == '__main__':
    main()
