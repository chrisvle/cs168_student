import socket
import sys
import utils
import select

class Server:

    clients = dict()
    sock_to_channels = dict()
    channels = set()
    SOCKET_LIST = []

    def __init__(self, port):
        self.port = int(port)
        self.socket = socket.socket()
        self.socket.bind(("localhost", self.port))
        self.socket.listen(5)

        Server.SOCKET_LIST.append(self.socket)
        print "Chat server started on port " + str(port)


    def rec(self):
        while True:
            ready_to_read , ready_to_write, in_error = select.select(Server.SOCKET_LIST,[],[])
            for sock in ready_to_read:
                # a new connection request recieved
                if sock == self.socket:
                    sockfd, addr = self.socket.accept()
                    Server.SOCKET_LIST.append(sockfd)
                    name = sockfd.recv(utils.MESSAGE_LENGTH)
                    Server.clients[sockfd] = name
                    print "Client (%s, %s) connected" % addr
                # a message from a client, not a new connection
                else:
                    # process data recieved from client,
                    try:
                        # receiving data from the socket.
                        data = sock.recv(utils.MESSAGE_LENGTH)
                        if data:
                            print data
                            split = data.split(" ")

                            if data == "/list" or data == "/list\n":
                                print "Inside list"
                                sock.send(utils.CLIENT_WIPE_ME + "\r")
                                for c in Server.channels:
                                    sock.send(c)
                                sock.send(utils.CLIENT_MESSAGE_PREFIX)


                            elif split[0] == "/create" or split[0] == "/create\n": # handle return as the channel name?
                                if len(split) == 1:
                                    sock.send(utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CREATE_REQUIRES_ARGUMENT + "\n" + utils.CLIENT_MESSAGE_PREFIX)
                                else:
                                    channel_name = split[1]
                                    if channel_name not in Server.channels:
                                        print "Inside Create"
                                        Server.sock_to_channels[sock] = channel_name
                                        Server.channels.add(channel_name)
                                    else:
                                        sock.send(utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CHANNEL_EXISTS + "\n" + utils.CLIENT_MESSAGE_PREFIX)

                            elif split[0] == "/join" or split[0] == "/join\n":
                                if len(split) == 1:
                                    sock.send(utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_JOIN_REQUIRES_ARGUMENT + "\n" + utils.CLIENT_MESSAGE_PREFIX)
                                else:
                                    channel_name = split[1]
                                    if channel_name not in Server.channels:
                                        sock.send(utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_NO_CHANNEL_EXISTS.format(channel_name) + "\n" + utils.CLIENT_MESSAGE_PREFIX)
                                    else:
                                        Server.sock_to_channels[sock] = channel_name
                                        self.broadcast(self.socket, sock, utils.CLIENT_WIPE_ME + "\r" + Server.clients[sock] + " has joined\n" + utils.CLIENT_MESSAGE_PREFIX)


                            # there is something in the socket
                            elif sock in Server.sock_to_channels:
                                self.broadcast(self.socket, sock, "\r" + "[" + Server.clients[sock] + '] ' + data + utils.CLIENT_MESSAGE_PREFIX)
                            else:
                                sock.send(utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CLIENT_NOT_IN_CHANNEL + "\n" + utils.CLIENT_MESSAGE_PREFIX)
                        else:
                            # remove the socket that's broken
                            if sock in Server.SOCKET_LIST:
                                Server.SOCKET_LIST.remove(sock)
                            # at this stage, no data means probably the connection has been broken
                            self.broadcast(self.socket, sock, "Client (%s, %s) is offline\n" % addr)
                    # exception
                    except:
                        self.broadcast(self.socket, sock, "Client (%s, %s) is offline\n" % addr)
                        continue
        self.socket.close()

    # broadcast chat messages to all connected clients
    def broadcast(self, server_socket, sock, message):
        if sock in Server.sock_to_channels:
            channel = Server.sock_to_channels[sock]
        same_channel = list()
        for s in Server.sock_to_channels:
            if Server.sock_to_channels[s] == channel and s != sock:
                same_channel.append(s)
        for socket in same_channel:
            # send the message only to peer
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

# if __name__ == "__main__":
args = sys.argv
if len(args) != 2:
    print "Please supply a port."
    sys.exit()
server = Server(args[1])
server.rec()
