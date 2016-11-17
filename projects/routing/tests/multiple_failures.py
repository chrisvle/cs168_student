"""
Test routing with multiple link failures.

Creates a topology like:

    Creates a topology with loops.

    It looks like:
             2    3
    h1     s4--s5--s6    h3
     1\ 1/     |     \ 1 / 1
       s1      |7     s2
     1/  \     |      / 1
    h2   3-s3--s7--s8
             6    1


Sends a ping from h1 to h2.
Waits a while.
Sends a ping from h1 to h3.
Waits a while.
Takes down the s5-s6 route.
             2    16
    h1     s4--s5  s6    h3
     1\ 1/     |     \ 1 / 1
       s1      |7      s2
     1/  \     |      / 1
    h2   3-s3--s7--s8
             6   1

Waits a while.
Sends a ping from h1 to h3 (should now take new route).
Waits a while.
Takes down the s1-s3 route.
             2    16
    h1     s4--s5  s6    h3
     1\ 1/     |     \ 1 / 1
       s1      |7      s2
     1/        |      / 1
    h2  16 s3--s7--s8
             6    1
Waits a while.
Sends a ping from h1-h3.
The test passes if h3 gets three pings and h2 gets one ping.

"""

import sim
import sim.api as api
import sim.basics as basics

from tests.test_simple import GetPacketHost


def launch():
    h1 = GetPacketHost.create("h1")
    h2 = GetPacketHost.create("h2")
    h3 = GetPacketHost.create("h3")

    s1 = sim.config.default_switch_type.create('s1')
    s2 = sim.config.default_switch_type.create('s2')
    s3 = sim.config.default_switch_type.create('s3')
    s4 = sim.config.default_switch_type.create('s4')
    s5 = sim.config.default_switch_type.create('s5')
    s6 = sim.config.default_switch_type.create('s6')
    s7 = sim.config.default_switch_type.create('s7')
    s8 = sim.config.default_switch_type.create('s8')

    s1.linkTo(h1, latency=1)
    s1.linkTo(h2, latency=1)
    s2.linkTo(h3, latency=1)

    s1.linkTo(s4, latency=1)
    s1.linkTo(s3, latency=3)

    s4.linkTo(s5, latency=2)
    s5.linkTo(s6, latency=3)
    s6.linkTo(s2, latency=1)

    s3.linkTo(s7, latency=6)
    s7.linkTo(s8, latency=1)
    s8.linkTo(s2, latency=1)

    s5.linkTo(s7, latency=7)

    def test_tasklet():
        t = 30
        yield t  # Wait for routing to converge
        api.userlog.debug("Sending test ping 1 (h1-h2)")
        h1.ping(h2)

        yield t

        api.userlog.debug("Sending test ping 2 (h1-h3)")
        h1.ping(h3)

        yield t

        api.userlog.debug("Failing s5-s6 link")
        s5.unlinkTo(s6)

        yield t

        api.userlog.debug("Sending test ping 3 (h1-h3)")
        h1.ping(h3)

        yield t

        api.userlog.debug("Failing s1-s3 link")
        s1.unlinkTo(s3)

        yield t

        api.userlog.debug("Sending test ping 4 (h1-h3)")
        h1.ping(h3)

        yield t

        if h3.pings != 3:
            api.userlog.error("h3 got %s packets instead of 3", h3.pings)
            good = False
        elif h2.pings != 1:
            api.userlog.error("h2 got %s packets instead of 1", h2.pings)
            good = False
        else:
            api.userlog.debug("Test passed successfully!")
            good = True

        # End the simulation and (if not running in interactive mode) exit.
        import sys
        sys.exit(0 if good else 1)

    api.run_tasklet(test_tasklet)
