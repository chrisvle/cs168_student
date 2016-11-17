"""

Creates the following Topology:

          h1             h2
         1 \\  1     2  // 2
            r1 - c12 - r2
           5||         ||2
            c13       c23
            5 \\     // 2
                 r3
                 || 2
                 h3

Sends a ping from h1 to h3, which should take the path:

h1 - R1 - c12 - R2 - c23 - r3 - h3

Sends a ping from h2 to h3, which should take the path:

h2 - R2 - c23 - r3 - h3


Then removes the R1 - R2 link:

   h1             h2
  1 \\           // 2
     r1         r2
    5||         ||2
     c13       c23
     5 \\     // 2
          r3
          || 2
          h3

Sends a ping from h1 to h2, which should take the path:

h1 - R1 - c13 - R3 - c23 - R2 - h2

"""

import sim
import sim.api as api
import sim.basics as basics

from tests.test_link_weights import CountingHub

def launch():
    h1 = basics.BasicHost.create("h1")
    h2 = basics.BasicHost.create("h2")
    h3 = basics.BasicHost.create("h3")

    c12 = CountingHub.create('c12')
    c13 = CountingHub.create('c13')
    c23 = CountingHub.create('c23')

    r1 = sim.config.default_switch_type.create("r1")
    r2 = sim.config.default_switch_type.create('r2')
    r3 = sim.config.default_switch_type.create('r3')

    r1.linkTo(h1, latency=1)

    r1.linkTo(c12, latency=1)
    c12.linkTo(r2, latency=2)

    r1.linkTo(c13, latency=5)
    c13.linkTo(r3, latency=5)

    r2.linkTo(c23, latency=2)
    c23.linkTo(r3, latency=2)

    r2.linkTo(h2, latency=2)
    r3.linkTo(h3, latency=1)


    def test_tasklet():
        yield 20

        api.userlog.debug('Sending ping from h1 to h3')
        h1.ping(h3)

        yield 10

        if c13.pings == 0 and c12.pings == 1 and c23.pings == 1:
            api.userlog.debug('The ping took the right path')
            good = True
        else:
            api.userlog.error('The ping took the wrong path')
            good = False



        api.userlog.debug('Sending ping from h2 to h3')
        h2.ping(h3)

        yield 10

        if c13.pings == 0 and c12.pings == 1 and c23.pings == 2:
            api.userlog.debug('The ping took the right path')
            good = good and True
        else:
            api.userlog.error('The ping took the wrong path')
            good = False


        api.userlog.debug('Link R1 - R2 goes down')
        r1.unlinkTo(c12)
        c12.unlinkTo(r2)

        yield 20

        api.userlog.debug('Sending ping from h1 to h2')
        h1.ping(h2)

        yield 15

        if c13.pings == 1 and c12.pings == 1 and c23.pings == 3:
            api.userlog.debug('The ping took the right path')
            good = good and True
        else:
            api.userlog.error('The ping took the wrong path')
            good = False


        import sys
        sys.exit(0 if good else 1)


    api.run_tasklet(test_tasklet)
