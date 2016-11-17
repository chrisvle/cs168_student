"""
Tests that the router correctly uses its own, longer path to a directly
attached host if a shorter path gets disconnected.

Creates a topology like the following:

    h1
     \
      s1 - c1 - s2
      5 \      /
           h2
After routes have converged, sends a ping from h1 to h2, which should use the
route going through s2. Then disconnects s2 from h2, waits for the routes to
converge again, and then sends another ping from h1 to h2. Should still get
through.

"""

import sim
import sim.api as api
import sim.basics as basics
import sys

from tests.test_simple import GetPacketHost, NoPacketHost
from tests.test_link_weights import CountingHub


def launch():
    h1 = NoPacketHost.create('h1')
    h2 = GetPacketHost.create('h2')
    s1 = sim.config.default_switch_type.create('s1')
    s2 = sim.config.default_switch_type.create('s2')
    c1 = CountingHub.create('c1')
    h1.linkTo(s1)
    s1.linkTo(c1)
    c1.linkTo(s2)
    h2.linkTo(s1, latency=5)
    h2.linkTo(s2)

    def test_tasklet():
        yield 15

        api.userlog.debug('Sending ping from h1 to h2 - it should get through')
        h1.ping(h2)

        yield 5

        if c1.pings != 1:
            api.userlog.error("The first ping didn't go through s2")
            sys.exit(1)
        if h2.pings != 1:
            api.userlog.error("The first ping didn't get through")
            sys.exit(1)

        api.userlog.debug('Disconnecting s2 and h2')
        s2.unlinkTo(h2)

        api.userlog.debug('Waiting for routes to expire')
        yield 20

        api.userlog.debug(
            'Sending ping from h1 to h2 - should still get through and not' +
            'try to go through c1')
        h1.ping(h2)

        yield 7

        if c1.pings != 1:
            api.userlog.error(
                's1 forwarded the ping through c1 instead of directly to h2')
            sys.exit(1)
        elif h2.pings != 2:
            api.userlog.error(
                'h2 did not receive the second ping')
            sys.exit(1)
        else:
            api.userlog.debug('yay')
            sys.exit(0)

    api.run_tasklet(test_tasklet)
