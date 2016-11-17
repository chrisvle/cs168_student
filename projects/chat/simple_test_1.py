""" A simple test that verifies that messages between two clients are received. """

import select
import sys
import time
from subprocess import Popen, PIPE
import utils

SLEEP_SECONDS = 0.1

class SimpleTest():
    def run(self, port):
        # self.setup_test_two_clients(port)
        # try:
        #   self.test_two_clients()
        # finally:
        #   self.tear_down()

        # self.setup_test(port)
        # try:
        #   self.test()
        # finally:
        #   self.tear_down()
        #
        # time.sleep(SLEEP_SECONDS)

        # self.setup_test(port)
        # try:
        #   self.test2()
        # finally:
        #   self.tear_down()
        #
        # time.sleep(SLEEP_SECONDS)
        #
        # self.setup_test(port)
        # try:
        #   self.test3()
        # finally:
        #     print "done"
        #   self.tear_down()
        #
        # self.setup_test(port)
        # try:
        #   self.test4()
        # finally:
        #     print "done"
        #   self.tear_down()
        #
        self.setup_test(port)
        try:
          self.test5()
        finally:
            print "done"
        #   self.tear_down()

    def setup_test(self, port, host="localhost"):
        """Sets up a server and three clients."""
        self.server = Popen(["python", "server.py", str(port)])
        # Give the server time to come up.
        time.sleep(SLEEP_SECONDS)

        self.rodhika_client = Popen(["python", "client.py", "Rodhika", host, str(port)], stdin=PIPE, stdout=PIPE)
        self.kay_client = Popen(["python", "client.py", "Kay", host, str(port)], stdin=PIPE, stdout=PIPE)
        self.panda_client = Popen(["python", "client.py", "Panda", host, str(port)], stdin=PIPE, stdout=PIPE)

        time.sleep(SLEEP_SECONDS)

    def setup_test_two_clients(self, port, host="localhost"):
        """Sets up a server and four clients."""
        self.server = Popen(["python", "server.py", str(port)])
        # Give the server time to come up.
        time.sleep(SLEEP_SECONDS)

        self.alice_client = Popen(["python", "client.py", "Alice", host, str(port)], stdin=PIPE, stdout=PIPE)
        self.kay_client = Popen(["python", "client.py", "Kay", host, str(port)], stdin=PIPE, stdout=PIPE)

        time.sleep(SLEEP_SECONDS)

    def tear_down(self):
        """ Stops the clients and server. """
        try:
            self.alice_client.kill()
            self.kay_client.kill()
            self.server.kill()
        except:
            print "tear_down fail"

    def get_message_from_buffer(self, buf):
        """Strips all formatting, including [Me] and whitespace."""
        s =  "".join(buf).replace('[Me]', '').strip()
        return s

    def check_for_output(self, client, expected_output, check_formatting=False):
        """ Verifies that the given client's stdout matches the given output."""
        output_buffer = []
        end_time = time.time() + 1

        char = ""

        while (char != "\n" and time.time() < end_time):
                select_timeout = end_time - time.time()
                ready_to_read, ready_to_write, in_error = select.select(
                    [client.stdout], [], [], select_timeout)
                for readable_socket in ready_to_read:
                    char = readable_socket.read(1)
                    output_buffer.append(char)

        message = self.get_message_from_buffer(output_buffer)
        if message != expected_output:
            raise Exception("Client output:\n{}; expected:\n{}".format(
                repr(message), repr(expected_output)))

    def test_two_clients(self):
        self.alice_client.stdin.write("/create tas\n")

        time.sleep(SLEEP_SECONDS)

        self.kay_client.stdin.write("/join tas\n")

        time.sleep(SLEEP_SECONDS)
        self.kay_client.stdin.write("/join tass\n")
        self.check_for_output(self.kay_client, utils.SERVER_NO_CHANNEL_EXISTS.format("tass"))
        time.sleep(SLEEP_SECONDS)
        # Alice should get a message that Kay joined.
        self.check_for_output(self.alice_client, utils.SERVER_CLIENT_JOINED_CHANNEL.format("Kay"))

        # When Kay sends a message, Alice should receive it.
        self.kay_client.stdin.write("Hi!\n")
        self.check_for_output(self.alice_client, "[Kay] Hi!")

        # When Alice sends a message, Kay should receive it.
        self.alice_client.stdin.write("Hello!\n")
        self.check_for_output(self.kay_client, "[Alice] Hello!")

        print "                            PASSED TEST_TWO_CLIENTS!"

    def test(self):
        self.kay_client.stdin.write("/list\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)

        self.kay_client.stdin.write("list my ramen\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, utils.SERVER_CLIENT_NOT_IN_CHANNEL)
        time.sleep(SLEEP_SECONDS)

        self.kay_client.stdin.write("/create dinner\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)

        self.kay_client.stdin.write("/list\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "dinner")
        time.sleep(SLEEP_SECONDS)

        self.kay_client.stdin.write("I'm going to Cheeseboard for dinner. anyone want to come? \n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)


        self.rodhika_client.stdin.write("/list\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, "dinner")
        time.sleep(SLEEP_SECONDS)

        self.rodhika_client.stdin.write("/join dinner\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "Rodhika has joined")
        time.sleep(SLEEP_SECONDS)


        self.rodhika_client.stdin.write("I'd like to go to house of curries. Anyone interested?\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "[Rodhika] I'd like to go to house of curries. Anyone interested?")
        time.sleep(SLEEP_SECONDS)


        self.kay_client.stdin.write("Yum, sounds good\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, "[Kay] Yum, sounds good")
        time.sleep(SLEEP_SECONDS)

        self.panda_client.stdin.write("/list\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, "dinner")
        time.sleep(SLEEP_SECONDS)

        self.panda_client.stdin.write("/create dessert\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, "")
        time.sleep(SLEEP_SECONDS)

        self.panda_client.stdin.write("/list\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, "dessert")
        self.check_for_output(self.panda_client, "dinner")
        time.sleep(SLEEP_SECONDS)

        self.panda_client.stdin.write("Yumm I love dessert! I want a Tiramisu\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, "")
        time.sleep(SLEEP_SECONDS)

        self.kay_client.stdin.write("I love dinner! I hate dessert\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, "[Kay] I love dinner! I hate dessert")
        time.sleep(SLEEP_SECONDS)
        self.kay_client.stdin.write("/joir dinner\n")
        self.check_for_output(self.kay_client, utils.SERVER_INVALID_CONTROL_MESSAGE.format("/joir"))

        self.kay_client.stdin.write("/join dessert\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, "Kay has joined")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.rodhika_client, utils.SERVER_CLIENT_LEFT_CHANNEL.format("Kay"))


        print "                            PASSED TEST!"

    def test2(self):
        self.rodhika_client.kill()
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, "")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, "")
        self.kay_client.stdin.write("/create\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, utils.SERVER_CREATE_REQUIRES_ARGUMENT)

        self.kay_client.stdin.write("/create dessert\n")
        time.sleep(SLEEP_SECONDS)
        self.kay_client.stdin.write("/create dessert\n")
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.kay_client, utils.SERVER_CHANNEL_EXISTS.format("dessert"))
        time.sleep(SLEEP_SECONDS)
        self.panda_client.stdin.write("/join dessert\n")
        time.sleep(SLEEP_SECONDS)


        self.kay_client.kill()
        time.sleep(SLEEP_SECONDS)
        self.check_for_output(self.panda_client, utils.SERVER_CLIENT_LEFT_CHANNEL.format("Kay"))
        time.sleep(SLEEP_SECONDS)

        print "                            PASSED TEST2!"

    def test3(self):
        self.kay_client.stdin.write("/join \n")
        self.check_for_output(self.kay_client, utils.SERVER_JOIN_REQUIRES_ARGUMENT)

        print "                            PASSED TEST3!"

    def test4(self):
        self.server.kill()
        self.check_for_output(self.kay_client, utils.CLIENT_SERVER_DISCONNECTED.format("localhost", port))

        print "                            PASSED TEST4!"

    def test5(self):
        # self.server.kill()
        # self.kay_client.stdin.write(utils.CLIENT_SERVER_DISCONNECTED.format("234.234.234.234", port))
        self.kay_client = Popen(["python", "client.py", "Kay", "234.234.234.234", str(port)], stdin=PIPE, stdout=PIPE)
        self.check_for_output(self.kay_client, utils.CLIENT_CANNOT_CONNECT.format("234.234.234.234", port))


        print "                            PASSED TEST5!"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python simple_test.py <port>"
        sys.exit(1)

    port = int(sys.argv[1])
    SimpleTest().run(port)
