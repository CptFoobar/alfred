#!/bin/env python

import argparse
import BaseHTTPServer
import ntpath
import os
import SimpleHTTPServer
import socket
import SocketServer
import sys
import tempfile
from netifaces import interfaces, ifaddresses, AF_INET
from time import gmtime, strftime

# Class to put ThreadingMixIn and HTTPServer together
class ThreadingSimpleServer(SocketServer.ThreadingMixIn,
                   BaseHTTPServer.HTTPServer):
    pass

# Run the threaded server
def threadedServer(port, directory, max_serve_count, force_port):
    # cd to given directory
    if directory is not None and len(directory) > 0:
        try:
            os.chdir(os.path.expanduser(directory))
        except OSError:
            print "Invalid path: {}".format(directory)
            print "Failed to start server."
            return

    # Interface name dictionary
    NAME = {
        'lo' : "localhost",
        'wlan0' : 'Wireless ',
        'eth0' : 'Ethernet'
    }

    # Init server, try 10 times if not forced to use given port
    attemptCount = 10 if not force_port else 1
    server = None
    while attemptCount > 0:
        try:
            server = ThreadingSimpleServer(('', port), SimpleHTTPServer.SimpleHTTPRequestHandler)
            break
        except socket.error as e:
            print "Failed to create server on port {0}, [Error {1}]: {2}".format(str(port), e.errno, e.strerror)
            port += 1
            attemptCount -= 1

    if not server:
        print "Failed to create server!"
        return

    try:
        print "Running server in {}...".format(directory or os.getcwd())
        addresses = []
        for ifaceName in interfaces():
            addresses.append((ifaceName, [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'x.x.x.x'}])]))
        for iface, address in addresses:
            if not address[0].startswith("x"):
                print "{0} {1}:{2}".format(NAME[iface] if iface in NAME else iface, str(address[0]), str(port))

        max_serve_count = max_serve_count if max_serve_count > 0 else 10000

        # Serve max_serve_count times
        while max_serve_count:
            max_serve_count -= 1
            sys.stdout.flush()
            server.handle_request()

    except KeyboardInterrupt:
        print("\rShutting down the server.")


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def main(args):
    dirname = os.getcwd()
    serving_file = False
    origin_dir = os.getcwd()

    if args.path and len(args.path) > 0:
        file_to_serve = ''
        if (os.path.isdir(args.path)):
            # Serving directory that is not cwd
            dirname = args.path
        elif (args.path in os.listdir(os.getcwd())):
            # Serving file from current directory
            file_to_serve = os.path.join(os.getcwd(), args.path)
            dirname = tempfile.mkdtemp(prefix=("alfred_" + strftime("%Y_%m_%d_%H_%M", gmtime())))
            os.symlink(file_to_serve, os.path.join(dirname, args.path))
            serving_file = True
        elif (os.path.isfile(args.path)):
            # Serving file in another directory
            file_to_serve = os.path.abspath(args.path)
            dirname = tempfile.mkdtemp(prefix=("alfred_" + strftime("%Y_%m_%d_%H_%M", gmtime())))
            os.symlink(file_to_serve, os.path.join(dirname, path_leaf(args.path)))
            serving_file = True
        else:
            print "Bad file path. Exiting."
            return -1

    # Start server
    threadedServer(args.port, dirname, args.count_max, args.force_port)

    #Cleanup
    if serving_file:
        os.chdir(origin_dir)
        for file_name in os.listdir(dirname):
            os.remove(os.path.join(dirname, file_name))
        os.rmdir(dirname)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # for aesthetics, so that command looks like 'alfred serve [options]'
    parser.add_argument("serve")

    # option for setting port
    parser.add_argument("-p", "--port", type=int, default=8021,
                        help="specify port to host server on (default: 8021)")

    # option for setting maximum serve count
    parser.add_argument("-c", "--count-max", type=int, default=10000,
                        help="maximum number of times directory can be served (default: 10000)")

    # option for forcing a port
    parser.add_argument("-f", "--force-port", action="store_true",
                        help="force the server to run on specified port (server won't start if port unavailable)")

    # option for serving only a particular file
    parser.add_argument("-P", "--path", type=str,
                        help="specify path (file or directory) to be served (overrides --directory)")

    args = parser.parse_args()

    ret = main(args)
    print "Return status: " + str(ret)
