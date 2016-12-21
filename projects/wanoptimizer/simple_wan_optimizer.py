import wan_optimizer
import utils
import tcp_packet

class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into fixed-size blocks.

    This WAN optimizer should implement part 1 of project 4.
    """

    # Size of blocks to store, and send only the hash when the block has been
    # sent previously
    BLOCK_SIZE = 8000

    def __init__(self):
        wan_optimizer.BaseWanOptimizer.__init__(self)
        # Add any code that you like here (but do not add any constructor arguments).
        self.storage = {}
        self.buffer = {}

    def receive(self, packet):
        """ Handles receiving a packet.

        Right now, this function simply forwards packets to clients (if a packet
        is destined to one of the directly connected clients), or otherwise sends
        packets across the WAN. You should change this function to implement the
        functionality described in part 1.  You are welcome to implement private
        helper fuctions that you call here. You should *not* be calling any functions
        or directly accessing any variables in the other middlebox on the other side of
        the WAN; this WAN optimizer should operate based only on its own local state
        and packets that have been received.
        """
        if packet.src not in self.buffer:
            self.buffer[packet.src] = {}

        if packet.dest not in self.buffer[packet.src]:
            self.buffer[packet.src][packet.dest] = ''

        if packet.dest in self.address_to_port:
            # The packet is destined to one of the clients connected to this middlebox;
            # send the packet there.
            if not packet.is_raw_data:
                data = self.storage[packet.payload]
                self.split_and_send(data, packet, False, packet.is_fin)
            else:
                self.process(packet, False)

        else:
            # The packet must be destined to a host connected to the other middlebox
            # so send it across the WAN.
            self.process(packet, True)

    def process(self, packet, to_wan):
        total = len(self.buffer[packet.src][packet.dest]) + len(packet.payload)
        data = self.buffer[packet.src][packet.dest] + packet.payload

        if total < WanOptimizer.BLOCK_SIZE:
            self.buffer[packet.src][packet.dest] = data
            if packet.is_fin:
                self.check_fin(packet, data, to_wan)

        elif total >= WanOptimizer.BLOCK_SIZE:
            remainder = data[WanOptimizer.BLOCK_SIZE:]
            ready = data[0:WanOptimizer.BLOCK_SIZE]
            self.buffer[packet.src][packet.dest] = remainder
            my_hash = utils.get_hash(ready)

            if my_hash in self.storage and to_wan:
                self.send(tcp_packet.Packet(packet.src, packet.dest, False, False, my_hash), self.wan_port)

            else:
                self.storage[my_hash] = ready
                self.split_and_send(ready, packet, to_wan, False)

            if packet.is_fin:
                self.check_fin(packet, remainder, to_wan)

    def check_fin(self, packet, data, to_wan):
        my_hash = utils.get_hash(data)
        if my_hash in self.storage and to_wan:
            self.send(tcp_packet.Packet(packet.src, packet.dest, False, True, my_hash), self.wan_port)

        else:
            self.storage[my_hash] = data
            self.split_and_send(data, packet, to_wan, True)

        self.buffer[packet.src][packet.dest] = ''

    def split_and_send(self, data, packet, wan, fin):
        if wan:
            out = self.wan_port
        else:
            out = self.address_to_port[packet.dest]

        i = 0
        packets = []
        while (i + utils.MAX_PACKET_SIZE) < len(data):
            packets.append(data[i:i+1500])
            i += 1500

        for p in packets:
            piece = tcp_packet.Packet(packet.src, packet.dest, True, False, p)
            self.send(piece, out)
        final = tcp_packet.Packet(packet.src, packet.dest, True, fin, data[i:])
        self.send(final, out)