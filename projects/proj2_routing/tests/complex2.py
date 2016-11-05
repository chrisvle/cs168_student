"""
A test of multiple hosts.
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
        self.pings = {}
        self.pongs = {}
    def handle_rx(self, packet, port):
        if (isinstance(packet, basics.Ping)):
            if packet.src not in self.pings:
                self.pings[packet.src] = 0
            self.pings[packet.src] += 1
        if (isinstance(packet, basics.Pong)):
            if packet.src not in self.pongs:
                self.pongs[packet.src] = 0
            self.pongs[packet.src] += 1
        sim.config.default_switch_type.handle_rx(self, packet, port)
    def clean(self):
        self.pings = {}
        self.pongs = {}

def check_router(router, from_host, num, ping=True):
    if ping:
        if from_host not in router.pings and num > 0:
            api.userlog.error("%s never received a ping from %s when it should have",
                    str(router), str(from_host))
            return False
        if num > 0 and router.pings[from_host] != num:
            api.userlog.error("%s received %d pings from %s but should be %d",
                    str(router), router.pings[from_host], str(from_host), num)
            return False
    else:
        if from_host not in router.pongs and num > 0:
            api.userlog.error("%s never received a pong from %s when it should have",
                    str(router), str(from_host))
            return False
        if num > 0 and router.pongs[from_host] != num:
            api.userlog.error("%s received %d pongs from %s but should be %d",
                    str(router), router.pongs[from_host], str(from_host), num)
            return False
    return True

def launch():
    h1 = Host.create("h1")
    h2 = Host.create("h2")
    s1 = Router.create("s1")
    s2 = Router.create("s2")
    s3 = Router.create("s3")
    h1.linkTo(s1)
    h1.linkTo(s2)
    h2.linkTo(s1)
    h2.linkTo(s3)
    s2.linkTo(s3)

    def test_tasklet_1():
        good = True

        yield 20
        api.userlog.debug("Sending test pings")
        h1.ping(h2)
        h2.ping(h1)
        yield 10
        if h1.pongs != 2 or h1.pings != 2:
            api.userlog.error("h1 got %s pings instead of 2", h1.pings)
            api.userlog.error("h1 got %s pongs instead of 2", h1.pongs)
            good = False
        if h2.pongs != 2 or h2.pings != 2:
            api.userlog.error("h2 got %s pings instead of 2", h2.pings)
            api.userlog.error("h2 got %s pongs instead of 2", h2.pongs)
            good = False
        good &= check_router(s1, h1, 1)
        good &= check_router(s1, h1, 1, False)
        good &= check_router(s1, h2, 1)
        good &= check_router(s1, h2, 1, False)
        good &= check_router(s2, h1, 1)
        good &= check_router(s2, h1, 1, False)
        good &= check_router(s2, h2, 1)
        good &= check_router(s2, h2, 1, False)
        good &= check_router(s3, h1, 1)
        good &= check_router(s3, h1, 1, False)
        good &= check_router(s3, h2, 1)
        good &= check_router(s3, h2, 1, False)
        s2.linkTo(s1)
        s2.unlinkTo(s3)
        s1.clean()
        s2.clean()
        yield 20
        h1.ping(h2)
        h2.ping(h1)
        yield 10
        if h1.pongs != 4 or h1.pings != 3:
            api.userlog.error("h1 got %s pings instead of 3", h1.pings)
            api.userlog.error("h1 got %s pongs instead of 3", h1.pongs)
            good = False
        if h2.pongs != 3 or h2.pings != 4:
            api.userlog.error("h2 got %s pings instead of 4", h2.pings)
            api.userlog.error("h2 got %s pongs instead of 3", h2.pongs)
            good = False
        good &= check_router(s1, h1, 2)
        good &= check_router(s1, h1, 1, False)
        good &= check_router(s1, h2, 1)
        good &= check_router(s1, h2, 2, False)
        good &= check_router(s2, h1, 1)
        good &= check_router(s2, h1, 0, False)
        good &= check_router(s2, h2, 0)
        good &= check_router(s2, h2, 0, False)
        import sys
        sys.exit(0 if good else 1)

    api.run_tasklet(test_tasklet_1)
