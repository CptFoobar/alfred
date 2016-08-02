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
import urllib
import cgi
import shutil
import mimetypes
import posixpath
from StringIO import StringIO
from netifaces import interfaces, ifaddresses, AF_INET
from time import gmtime, strftime

# Class to put ThreadingMixIn and HTTPServer together
class ThreadingSimpleServer(SocketServer.ThreadingMixIn,
                   BaseHTTPServer.HTTPServer):
    pass

class AlfredHTTPServer(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def getPageHeader(self, pageTitle, dirTitle):
        head = '''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Alfred serving /</title>
                <style>
                    body {
                        margin: 0px;
                        background-color: #F3E5F5;
                        overflow-x: hidden;
                    }
                    .alfred-title {
                        min-height: 10%;
                        max-height: 10%;
                        background-color: #9C27B0;
                        width: 100%;
                        text-align: center;
                        padding: 20px;
                        font-size: 25px;
                        font-family: monospace;
                        color: rgb(255, 140, 219);
                    }
                    .alfred-content {
                        padding: 20px;
                        font-size: 20px;
                        font-family: monospace;
                        line-height: 1.75em;
                        margin-left: 5%;
                    }
                    .alfred-dir-title {
                        font-size: 1.25em;
                    }
                    .alfred-dir-listing > ul {
                        list-style-type: decimal-leading-zero;
                        list-style-position: inside;
                    }
                    .alfred-footer {
                        position: absolute;
                        bottom: 0;
                        right: 0;
                        font-size: 15px;
                        font-family: monospace;
                        padding: 15px;
                    }

                    @media only screen and (max-width: 992px) {
                        .alfred-title {
                            min-height: 10%;
                            max-height: 10%;
                            background-color: #9C27B0;
                            width: 100%;
                            text-align: center;
                            padding: 20px;
                            font-size: 4.5em;
                            font-family: monospace;
                            color: rgb(255, 140, 219);
                        }
                        .alfred-content {
                            padding: 20px;
                            font-size: 3.5em;
                            font-family: monospace;
                            line-height: 1.75em;
                            margin-left: 5%;
                        }
                        .alfred-dir-title {
                            font-size: 1.25em;
                        }
                        .alfred-footer {
                            position: absolute;
                            bottom: 0;
                            right: 0;
                            font-size: 2.75em;
                            font-family: monospace;
                            padding: 15px;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="alfred-title">
                    <h2>Alfred</h2>
                </div>
                <div class="alfred-content">
                    <div class="alfred-dir-title">
                        <h3>Serving /</h3>
                    </div>
                    <div class="alfred-dir-listing">
                        <ul>
        '''
        head = head.replace("%pageTitle%", pageTitle)
        head = head.replace("%dirTitle%", dirTitle)
        return str(head)

    def getPageFooter(self):
        footer = '''
                        </ul>
                    </div>
                </div>
                <div class="alfred-footer">
                    Alfred @ <a href="https://github.com/tigerkid001/alfred">Github</a>
                    || 
                    <a href="http://sidhant.io">sidhant.io</a>
                </div>
            </body>
        </html>
        '''
        return str(footer)

    def list_directory(self, path):
            """
            Override default index.html generator for better UI
            Helper to produce a directory listing (absent index.html).

            Return value is either a file object, or None (indicating an
            error).  In either case, the headers are sent, making the
            interface the same as for send_head().

            """
            try:
                list = os.listdir(path)
            except os.error:
                self.send_error(404, "No permission to list directory")
                return None
            list.sort(lambda a, b: cmp(a.lower(), b.lower()))
            f = StringIO()
            f.write(self.getPageHeader(self.path, self.path))
            for name in list:
                fullname = os.path.join(path, name)
                displayname = linkname = name = cgi.escape(name)
                # Append / for directories or @ for symbolic links
                if os.path.isdir(fullname):
                    displayname = name + "/"
                    linkname = name + "/"
                if os.path.islink(fullname):
                    displayname = name + "@"
                    # Note: a link to a directory displays with @ and links with /
                f.write('<li><a href="%s">%s</a>\n' % (linkname, displayname))
            f.write(self.getPageFooter())
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            return f


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
            server = ThreadingSimpleServer(('', port), AlfredHTTPServer)
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
    
# Symlink method for Windows, since default os.symlink doesn't work 
def symlink_ms(source, link_name):
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source.replace('/', '\\'), flags) == 0:
            print "Failed to serve file..."
            
def main(args):
    dirname = os.getcwd()
    serving_file = False
    origin_dir = os.getcwd()
    
    if (args.text and len(args.text) > 0):
        print "Serving " + args.text
        # Write text to temp file and serve
        dirname = tempfile.mkdtemp(prefix=("alfred_" + strftime("%Y_%m_%d_%H_%M", gmtime())))
        # Write to html so file can be opened in browser itself
        text_file = open(os.path.join(dirname, "text.html"), 'w')
        text_file.write(args.text)
        text_file.close()
        file_to_serve = os.path.join(dirname, "text")
        serving_file = True
    elif args.path and len(args.path) > 0:
        file_to_serve = ''
        # Set os.symlink function to work for Windows
        os_symlink = getattr(os, "symlink", None)
        if callable(os_symlink):
            pass
        else:
            os.symlink = symlink_ms
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

    # option for serving only text
    parser.add_argument("-t", "--text", type=str,
                        help="specify text to be served (enter text in quotes)")

    args = parser.parse_args()

    ret = main(args)
    print "Return status: " + str(ret)
