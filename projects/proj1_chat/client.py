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
            self.socket.send(self.pad(self.name))
        except :
            sys.stdout.write(utils.CLIENT_CANNOT_CONNECT.format(address, port))
            sys.stdout.flush()
            sys.exit()
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()
        self.broadcast()

    def broadcast(self):
        cache = ""
        while True:
            socket_list = [sys.stdin, self.socket]

            # Get the list sockets which are readable
            ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])

            for sock in ready_to_read:
                if sock == self.socket:
                    # incoming message from remote server, s
                    data = sock.recv(utils.MESSAGE_LENGTH - len(cache))
                    if not data:
                        sys.stdout.write(utils.CLIENT_WIPE_ME + "\r" + utils.CLIENT_SERVER_DISCONNECTED.format(self.address, str(self.port)) + "\n")
                        sys.stdout.flush()
                        sys.exit()
                    else:

                        if len(data) < utils.MESSAGE_LENGTH:
                            cache += data
                            if len(cache) == utils.MESSAGE_LENGTH:
                                sys.stdout.write(cache.rstrip() + "\n")
                                sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                                sys.stdout.flush()
                                cache = ""
                        else:
                            data = data.rstrip()
                            sys.stdout.write(data + "\n")
                            sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                            sys.stdout.flush()

                else :
                    # user entered a message
                    msg = sys.stdin.readline()
                    self.socket.send(self.pad(msg))
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()


    def pad(self, m):
        return m + " " * (utils.MESSAGE_LENGTH - len(m))


args = sys.argv
if len(args) != 4:
    print "Please supply a name, server address, and port."
    sys.exit()
client = Client(args[1], args[2], args[3])
