import wan_optimizer
import utils
import tcp_packet

class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into variable-sized
    blocks based on the contents of the file.

    This WAN optimizer should implement part 2 of project 4.
    """

    # The string of bits to compare the lower order 13 bits of hash to
    GLOBAL_MATCH_BITSTRING = '0111011001010'

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
        functionality described in part 2.  You are welcome to implement private
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
        start = max(len(self.buffer[packet.src][packet.dest]) - 48, 0)
        end = start + 48
        self.buffer[packet.src][packet.dest] += packet.payload
        curr_window = self.buffer[packet.src][packet.dest][start:end]

        while end <= len(self.buffer[packet.src][packet.dest]):
            curr_hash = utils.get_hash(curr_window)
            if utils.get_last_n_bits(curr_hash, 13) == WanOptimizer.GLOBAL_MATCH_BITSTRING:
                data = self.buffer[packet.src][packet.dest][:end]
                my_hash = utils.get_hash(data)

                if my_hash in self.storage and to_wan:
                    self.send(tcp_packet.Packet(packet.src, packet.dest, False, False, my_hash), self.wan_port)
                else:
                    self.storage[my_hash] = data
                    self.split_and_send(data, packet, to_wan, False)

                self.buffer[packet.src][packet.dest] = self.buffer[packet.src][packet.dest][end:]
                start = 0
                end = 48
            else:
                start += 1
                end += 1

            curr_window = self.buffer[packet.src][packet.dest][start:end]

        if packet.is_fin:
            data = self.buffer[packet.src][packet.dest]
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
