"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    POISON_MODE = False # Can override POISON_MODE here
    DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate
        self.ports = {}
        self.routing_table = {}
        self.direct = {}

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        for r in self.routing_table:
            new_route_packet = basics.RoutePacket(r, latency)
            self.send(new_route_packet, port)

        if port not in self.ports:
            self.ports[port] = latency
        else:
            if self.ports[port] > latency:
                self.ports[port] = latency

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        dest = []

        for r in self.routing_table:
            if self.routing_table[r][1] == port:
                dest.append(r)

        if DVRouter.POISON_MODE:
            for d in dest:
                new_route_packet = basics.RoutePacket(d, INFINITY)
                self.send(new_route_packet, port, flood=True)

        if port in self.ports:
            del self.ports[port]

        for d in dest:
            if d in self.routing_table:
                del self.routing_table[d]

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):

            total = packet.latency + self.ports[port]

            if packet.destination not in self.routing_table and packet.latency != INFINITY:
                self.routing_table[packet.destination] = [packet.src, port, total, api.current_time()]

            elif packet.destination not in self.routing_table and packet.latency == INFINITY:
                return

            else:
                if packet.latency == INFINITY and port == self.routing_table[packet.destination][1]: #TEST THIS LATER!!
                    if packet.destination in self.direct:
                        self.routing_table[packet.destination] = [packet.destination, self.direct[packet.destination][0], self.direct[packet.destination][1], api.current_time()]
                    else:
                        new_route_packet = basics.RoutePacket(packet.destination, INFINITY)
                        self.send(new_route_packet, flood=True) #packet.src
                        del self.routing_table[packet.destination]

                elif self.routing_table[packet.destination][2] > total:
                    self.routing_table[packet.destination] = [packet.src, port, total, api.current_time()]

                elif packet.src == self.routing_table[packet.destination][0] and total > self.routing_table[packet.destination][2]:
                    self.routing_table[packet.destination][2] = total

                elif packet.src == self.routing_table[packet.destination][0] and total == self.routing_table[packet.destination][2]:
                    self.routing_table[packet.destination][3] = api.current_time()

        elif isinstance(packet, basics.HostDiscoveryPacket): # do we always link up before discovery packet
            self.routing_table[packet.src] = [packet.src, port, self.ports[port], api.current_time()]
            self.direct[packet.src] = [port, self.ports[port]]

        else:
            if packet.dst in self.routing_table:
                if self.routing_table[packet.dst][1] == port:
                    return

                else:
                    if packet.dst in self.direct:
                        if self.routing_table[packet.dst][2] <= self.direct[packet.dst][1]:
                            self.send(packet, self.routing_table[packet.dst][1])
                        else:
                            self.send(packet, self.direct[packet.dst][0])
                    else:
                        self.send(packet, self.routing_table[packet.dst][1])

            else:
                if packet.dst in self.direct:
                    self.send(packet, self.direct[packet.dst][0])
                else:
                    return

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        delete = []
        for r in self.routing_table:
            if api.current_time() - self.routing_table[r][3] > self.ROUTE_TIMEOUT:
                if not isinstance(self.routing_table[r][0], api.HostEntity):
                    delete.append(r)
                else:
                    self.routing_table[r][3] = api.current_time()
            else:
                latency = self.routing_table[r][2]
                new_route_packet = basics.RoutePacket(r, latency)
                self.send(new_route_packet, self.routing_table[r][1], flood=True)
        for k in delete:
            del self.routing_table[k]
