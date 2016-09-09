import socket
import sys
import utils
import select

class Server:

    client_names = dict()
    sock_to_channels = dict()
    channels = set()
    sock_to_message = dict()
    SOCKET_LIST = []

    def __init__(self, port):
        self.port = int(port)
        self.socket = socket.socket()
        self.socket.bind(("localhost", self.port)) #### localhost????
        self.socket.listen(5)
        Server.SOCKET_LIST.append(self.socket)

        # ANYTHING PRINT ON INIT?

    def rec(self):
        while True:
            ready_to_read , ready_to_write, in_error = select.select(Server.SOCKET_LIST,[],[])
            for sock in ready_to_read:
                # a new connection request recieved
                if sock == self.socket:
                    sockfd, addr = self.socket.accept()
                    Server.SOCKET_LIST.append(sockfd)
                    name = sockfd.recv(utils.MESSAGE_LENGTH)
                    Server.client_names[sockfd] = name

                # a message from a client, not a new connection
                else:
                    # process data recieved from client,
                    try:
                        # receiving data from the socket.
                        data = sock.recv(utils.MESSAGE_LENGTH)
                        if data:
                            if sock in Server.sock_to_message:
                                if len ()
                            if len(data) < utils.MESSAGE_LENGTH:
                                if sock in Server.sock_to_message:
                                    Server.sock_to_message[sock] += data
                                else:
                                    Server.sock_to_message[sock] = data
                            else:
                                if data[0] == "/":
                                    split = data.split()
                                    print split

                                    if split[0] == "/list":
                                        for c in Server.channels:
                                            m = utils.CLIENT_WIPE_ME + "\r" + c + "\n"
                                            sock.send(self.pad(m))

                                    elif split[0] == "/create":
                                        if len(split) == 1:
                                            m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CREATE_REQUIRES_ARGUMENT + "\n"
                                            sock.send(self.pad(m))
                                        else:
                                            channel_name = split[1]
                                            if channel_name not in Server.channels:
                                                if sock in Server.sock_to_channels:
                                                    m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CLIENT_LEFT_CHANNEL.format(Server.client_names[sock]) + "\n"
                                                    self.broadcast(self.socket, sock, self.pad(m))
                                                Server.sock_to_channels[sock] = channel_name
                                                Server.channels.add(channel_name)
                                            else:
                                                m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CHANNEL_EXISTS.format(channel_name) + "\n"
                                                sock.send(self.pad(m))

                                    elif split[0] == "/join":
                                        if len(split) == 1:
                                            m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_JOIN_REQUIRES_ARGUMENT + "\n"
                                            sock.send(self.pad(m))
                                        else:
                                            channel_name = split[1]
                                            if channel_name not in Server.channels:
                                                m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_NO_CHANNEL_EXISTS.format(channel_name) + "\n"
                                                sock.send(self.pad(m))
                                            else:
                                                if sock in Server.sock_to_channels:
                                                    m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CLIENT_LEFT_CHANNEL.format(Server.client_names[sock]) + "\n"
                                                    self.broadcast(self.socket, sock, self.pad(m))
                                                Server.sock_to_channels[sock] = channel_name
                                                m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CLIENT_JOINED_CHANNEL.format(Server.client_names[sock]) + "\n"
                                                self.broadcast(self.socket, sock, self.pad(m))

                                    else:
                                        m = utils.SERVER_INVALID_CONTROL_MESSAGE.format(utils.CLIENT_WIPE_ME + "\r" + split[0]) + "\n"
                                        sock.send(self.pad(m))

                                elif sock in Server.sock_to_channels:
                                    m = utils.CLIENT_WIPE_ME + "\r" + "[" + Server.client_names[sock] + '] ' + data
                                    self.broadcast(self.socket, sock, self.pad(m))
                                else:
                                    m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CLIENT_NOT_IN_CHANNEL + "\n"
                                    sock.send(self.pad(m))
                        else:
                            # remove the socket that's broken
                            if sock in Server.SOCKET_LIST:
                                Server.SOCKET_LIST.remove(sock)
                            # at this stage, no data means probably the connection has been broken
                            if sock in Server.sock_to_channels:
                                m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CLIENT_LEFT_CHANNEL.format(Server.client_names[sock]) + "\n"
                                self.broadcast(self.socket, sock, self.pad(m))
                    # exception
                    except:
                        if sock in Server.sock_to_channels:
                            m = utils.CLIENT_WIPE_ME + "\r" + utils.SERVER_CLIENT_LEFT_CHANNEL.format(Server.client_names[sock]) + "\n"
                            self.broadcast(self.socket, sock, self.pad(m))
                        continue
        self.socket.close()

    def pad(self, m):
        return m + " " * (200 - len(m))

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
