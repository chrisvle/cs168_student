"""
Your learning switch warm-up exercise for CS-168.

Start it up with a commandline like...

  ./simulator.py --default-switch-type=learning_switch topos.rand --links=0

"""

import sim.api as api
import sim.basics as basics


class LearningSwitch(api.Entity):
    """
    A learning switch.

    Looks at source addresses to learn where endpoints are.  When it doesn't
    know where the destination endpoint is, floods.

    This will surely have problems with topologies that have loops!  If only
    someone would invent a helpful poem for solving that problem...

    """

    def __init__(self):
        self.lookup = {}

    def handle_link_down(self, port):
        """
        Called when a port goes down (because a link is removed)

        You probably want to remove table entries which are no longer
        valid here.

        """
        toDel = []
        for dest in self.lookup:
            if self.lookup[dest] == port:
                toDel.append(dest)
        for d in toDel:
            del self.lookup[d]

    def handle_rx(self, packet, in_port):
        """
        Called when a packet is received.

        You most certainly want to process packets here, learning where
        they're from, and either forwarding them toward the destination
        or flooding them.

        """
        # learn from source
        src = packet.src
        if src not in self.lookup:
            self.lookup[packet.src] = in_port
            
        if isinstance(packet, basics.HostDiscoveryPacket):
            # Don't forward discovery messages
            return
        else:
            dest = packet.dst
            if dest in self.lookup:
                self.send(packet, self.lookup[dest], flood=False)
            else:
                # Flood out all ports except the input port
                self.send(packet, in_port, flood=True)
