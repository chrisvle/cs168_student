"""
A test of multiple hosts pinging a single host.
"""

import sim
import sim.api as api
import sim.basics as basics

class Host(basics.BasicHost):
    def __init__(self):
        basics.BasicHost.__init__(self)
        self.pings = 0
        self.pongs = 0
    def handle_rx(self, packet, port):
        if (isinstance(packet, basics.Ping)):
            self.pings += 1
        if (isinstance(packet, basics.Pong)):
            self.pongs += 1
        basics.BasicHost.handle_rx(self, packet, port)

class Router(sim.config.default_switch_type):
    def __init__(self):
        sim.config.default_switch_type.__init__(self)
        self.packets = {} # {src_host : number of packets}
    def handle_rx(self, packet, port):
        if isinstance(packet, basics.Ping):
            if packet.src not in self.packets:
                self.packets[packet.src] = 0
            self.packets[packet.src] += 1
        sim.config.default_switch_type.handle_rx(self, packet, port)

def launch():
    h1 = Host.create("h1")
    h2 = Host.create("h2")
    h3 = Host.create("h3")
    h4 = Host.create("h4")
    h5 = Host.create("h5")
    s1 = Router.create("s1")
    s2 = Router.create("s2")
    s3 = Router.create("s3")
    s4 = Router.create("s4")
    s5 = Router.create("s5")
    h1.linkTo(s5)
    s5.linkTo(s1)
    s5.linkTo(s2)
    s5.linkTo(s3)
    s5.linkTo(s4)
    h2.linkTo(s1)
    h3.linkTo(s2)
    h4.linkTo(s3)
    h5.linkTo(s4)
    s1.linkTo(s2)
    s2.linkTo(s3)
    s3.linkTo(s4)

    def check_ping_pong(host, pings, pongs):
        good = True
        if host.pings != pings:
            api.userlog.error("%s got %d pings instead of %d", str(host), host.pings, pings)
            good = False
        if host.pongs != pongs:
            api.userlog.error("%s got %d pongs instead of %d", str(host), host.pongs, pongs)
            good = False
        return good

    def check_router(router, host, num):
        if host not in router.packets:
            if num > 0:
                api.userlog.error("%s got %d packets from %s instead of %d",
                        str(router), 0, str(host), num)
                return False
            else:
                return True
        if router.packets[host] != num:
            api.userlog.error("%s got %d packets from %s instead of %d",
                    str(router), router.packets[host], str(host), num)
            return False
        return True

    def refresh():
        for router in [s1, s2, s3, s4, s5]:
            router.packets = {}
        for host in [h1, h2, h3, h4, h5]:
            host.pings = 0
            host.pongs = 0

    def test_tasklet_1():
        good = True

        yield 10
        api.userlog.debug("Sending test pings")
        h2.ping(h1)
        h3.ping(h1)
        h4.ping(h1)
        h5.ping(h1)
        yield 10
        good &= check_ping_pong(h2, 0, 1)
        good &= check_ping_pong(h3, 0, 1)
        good &= check_ping_pong(h4, 0, 1)
        good &= check_ping_pong(h5, 0, 1)
        good &= check_router(s4, h5, 1)
        good &= all([check_router(s4, host, 0) for host in [h4, h3, h2, h1]])
        good &= check_router(s3, h4, 1)
        good &= all([check_router(s3, host, 0) for host in [h5, h3, h2, h1]])
        good &= check_router(s2, h3, 1)
        good &= all([check_router(s2, host, 0) for host in [h5, h4, h2, h1]])
        good &= check_router(s1, h2, 1)
        good &= all([check_router(s1, host, 0) for host in [h5, h3, h4, h1]])
        good &= all([check_router(s5, host, 1) for host in [h5, h4, h3, h2]])
        good &= check_router(s5, h1, 0)

        s1.unlinkTo(s5)
        yield 5
        refresh()
        h2.ping(h1)
        h3.ping(h1)
        h4.ping(h1)
        h5.ping(h1)
        yield 10
        good &= check_ping_pong(h2, 0, 1)
        good &= check_ping_pong(h3, 0, 1)
        good &= check_ping_pong(h4, 0, 1)
        good &= check_ping_pong(h5, 0, 1)
        good &= check_router(s4, h5, 1)
        good &= all([check_router(s4, host, 0) for host in [h4, h3, h2, h1]])
        good &= check_router(s3, h4, 1)
        good &= all([check_router(s3, host, 0) for host in [h5, h3, h2, h1]])
        good &= check_router(s2, h3, 1)
        good &= check_router(s2, h2, 1)
        good &= all([check_router(s2, host, 0) for host in [h5, h4, h1]])
        good &= check_router(s1, h2, 1)
        good &= all([check_router(s1, host, 0) for host in [h5, h3, h4, h1]])
        good &= all([check_router(s5, host, 1) for host in [h5, h4, h3, h2]])
        good &= check_router(s5, h1, 0)

        s2.unlinkTo(s5)
        yield 10
        refresh()
        h2.ping(h1)
        h3.ping(h1)
        h4.ping(h1)
        h5.ping(h1)
        yield 15
        good &= check_ping_pong(h2, 0, 1)
        good &= check_ping_pong(h3, 0, 1)
        good &= check_ping_pong(h4, 0, 1)
        good &= check_ping_pong(h5, 0, 1)
        good &= check_router(s4, h5, 1)
        good &= all([check_router(s4, host, 0) for host in [h4, h3, h2, h1]])
        good &= check_router(s3, h4, 1)
        good &= check_router(s3, h3, 1)
        good &= check_router(s3, h2, 1)
        good &= all([check_router(s3, host, 0) for host in [h5, h1]])
        good &= check_router(s2, h3, 1)
        good &= check_router(s2, h2, 1)
        good &= all([check_router(s2, host, 0) for host in [h5, h4, h1]])
        good &= check_router(s1, h2, 1)
        good &= all([check_router(s1, host, 0) for host in [h5, h3, h4, h1]])
        good &= all([check_router(s5, host, 1) for host in [h5, h4, h3, h2]])
        good &= check_router(s5, h1, 0)

        s3.unlinkTo(s5)
        yield 15
        refresh()
        h2.ping(h1)
        h3.ping(h1)
        h4.ping(h1)
        h5.ping(h1)
        yield 15
        good &= check_ping_pong(h2, 0, 1)
        good &= check_ping_pong(h3, 0, 1)
        good &= check_ping_pong(h4, 0, 1)
        good &= check_ping_pong(h5, 0, 1)
        good &= all([check_router(s4, host, 1) for host in [h4, h3, h2, h5]])
        good &= check_router(s4, h1, 0)
        good &= all([check_router(s3, host, 1) for host in [h2, h3, h4]])
        good &= check_router(s3, h5, 0)
        good &= check_router(s3, h1, 0)
        good &= check_router(s2, h3, 1)
        good &= check_router(s2, h2, 1)
        good &= all([check_router(s2, host, 0) for host in [h5, h4, h1]])
        good &= check_router(s1, h2, 1)
        good &= all([check_router(s1, host, 0) for host in [h5, h3, h4, h1]])
        good &= all([check_router(s5, host, 1) for host in [h5, h4, h3, h2]])
        good &= check_router(s5, h1, 0)
        import sys
        sys.exit(0 if good else 1)

    api.run_tasklet(test_tasklet_1)
