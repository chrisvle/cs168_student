"""
Tests that packets take the lowest-cost path.

Creates a topology like the following, where the s1-s4 link has 3 times the cost
of all the other links:

h1 -- s1 -- s2 -- s3 -- c1 -- h2
      

       \\                    //
        s4 ------------ c2 --     this arrives later

After routes have converged, sends a packet from h1 to h2. The test passes if
the packet takes the top path, which has more hops but a lower total cost. We
check which path the packet took using c1 and c2, which are CountingHubs.

"""

import sim
import sim.api as api
import sim.basics as basics

from tests.test_simple import GetPacketHost, NoPacketHost


class CountingHub(api.Entity):
    pings = 0

    def handle_rx(self, packet, in_port):
        self.send(packet, in_port, flood=True)
        if isinstance(packet, basics.Ping):
            api.userlog.debug('%s saw a ping' % (self.name, ))
            self.pings += 1


def launch():
    h1 = NoPacketHost.create('h1')
    h2 = GetPacketHost.create('h2')
    s1 = sim.config.default_switch_type.create('s1')
    s2 = sim.config.default_switch_type.create('s2')
    s3 = sim.config.default_switch_type.create('s3')
    c1 = CountingHub.create('c1')
    h1.linkTo(s1, latency=1)
    s1.linkTo(s2, latency=1)
    s2.linkTo(s3, latency=5)
    s3.linkTo(c1, latency=1)
    c1.linkTo(h2, latency=1)

    def test_tasklet():
        yield 20

        api.userlog.debug('Sending ping from h1 to h2')
        h1.ping(h2)

        yield 10

        if c1.pings == 1:
            api.userlog.debug('The ping took the right path')
            good = True
        else:
            api.userlog.error('idk what happened to ping lol theres no other way')
            good = False

        s4 = sim.config.default_switch_type.create('s4')
        c2 = CountingHub.create('c2')
        s1.linkTo(s4, latency=1)
    	s4.linkTo(c2, latency=1)
    	c2.linkTo(h2, latency=1)

    	yield 20

    	h1.ping(h2)

        yield 5

        if c1.pings == 1 and c2.pings == 1:
            api.userlog.debug('The ping took the right path')
            good2 = True
        elif c2.pings == 0 and c1.pings == 2:
            api.userlog.error('The ping took the wrong path')
            good2 = False
        else:
            api.userlog.error('Something strange happened to the ping')
            good2 = False


        import sys
        sys.exit(0 if good and good2 else 1)

    api.run_tasklet(test_tasklet)