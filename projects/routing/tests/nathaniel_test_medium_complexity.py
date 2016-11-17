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
    h3 = GetPacketHost.create('h3')
    s1 = sim.config.default_switch_type.create('s1')
    s2 = sim.config.default_switch_type.create('s2')
    s3 = sim.config.default_switch_type.create('s3')
    s4 = sim.config.default_switch_type.create('s4')
    s5 = sim.config.default_switch_type.create('s5')
    s6 = sim.config.default_switch_type.create('s6')
    c1 = CountingHub.create('c1')
    c2 = CountingHub.create('c2')
    c3 = CountingHub.create('c3')
    c4 = CountingHub.create('c4')
    c5 = CountingHub.create('c5')
    h1.linkTo(s4, latency=1)
    h2.linkTo(s5, latency=1)
    h3.linkTo(s6, latency=1)
    s4.linkTo(c1, latency=1)
    s4.linkTo(c3, latency=1)
    c1.linkTo(s1, latency=1)
    c3.linkTo(s3, latency=10)
    s1.linkTo(s3, latency=8)
    s1.linkTo(c5, latency=1)
    c5.linkTo(s5, latency=1)
    s1.linkTo(c2, latency=1)
    s5.linkTo(s2, latency=1)
    c2.linkTo(s2, latency=1)
    s3.linkTo(s2, latency=8)
    s3.linkTo(c4, latency=10)
    c4.linkTo(s6, latency=10)
    s2.linkTo(s6, latency=1)

    def test_tasklet():
        yield 20

        api.userlog.debug('Sending ping from h1 to h2')
        h1.ping(h2)

        yield 5

        if c1.pings == 1 and c2.pings == 0 and c3.pings == 0 and c4.pings == 0 and c5.pings == 1:
            api.userlog.debug('The ping took the right path')
            good = True
        elif not c1.pings == 1 or not c2.pings == 0 or not c3.pings == 0 or not c4.pings == 0 or not c5.pings == 1:
            api.userlog.error('The ping took the wrong path')
            good = False
        else:
            api.userlog.error('Something strange happened to the ping')
            good = False

        api.userlog.debug('Sending ping from h1 to h3')
        h1.ping(h3)

        yield 5

        if c1.pings == 2 and c2.pings == 1 and c3.pings == 0 and c4.pings == 0 and c5.pings == 1:
            api.userlog.debug('The ping took the right path')
            good2 = True
        elif not c1.pings == 2 or not c2.pings == 1 or not c3.pings == 0 or not c4.pings == 0 or not c5.pings == 1:
            api.userlog.error('The ping took the wrong path')
            good2 = False
        else:
            api.userlog.error('Something strange happened to the ping')
            good2 = False

        import sys
        sys.exit(0 if good and good2 else 1)

    api.run_tasklet(test_tasklet)
