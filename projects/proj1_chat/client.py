import socket
import sys
import utils
import select


class Client:
    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = int(port)
        self.socket = socket.socket()
        try :
            self.socket.connect((self.address, self.port))
            self.socket.send(self.name)
        except :
            print 'Unable to connect'
            sys.exit()
        print 'Connected to remote host. You can start sending messages'
        sys.stdout.write('[Me] ')
        sys.stdout.flush()
        self.broadcast()

    def broadcast(self):
        while True:
            socket_list = [sys.stdin, self.socket]

            # Get the list sockets which are readable
            ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])

            for sock in ready_to_read:
                if sock == self.socket:
                    # incoming message from remote server, s
                    data = sock.recv(200)
                    if not data :
                        print '\nDisconnected from chat server'
                        sys.exit()
                    else :
                        #print data
                        sys.stdout.write(data)
                        # sys.stdout.write('[Me] ')
                        sys.stdout.flush()

                else :
                    # user entered a message
                    msg = sys.stdin.readline()
                    self.socket.send(msg)
                    sys.stdout.write('[Me] ')
                    sys.stdout.flush()


# if __name__ == "__main__":
args = sys.argv
if len(args) != 4:
    print "Please supply a name, server address, and port."
    sys.exit()
client = Client(args[1], args[2], args[3])
