import sys
import re
import string
import SimpleHTTPServer
import SocketServer
import urllib

# Custom library
from python.wiki_data import do_wiki_call

PORT = 3000

SimpleHandler = SimpleHTTPServer.SimpleHTTPRequestHandler


class Handler(SimpleHandler):

    def do_GET(self):
        try:
            print self.path
            pattern = re.compile('^/py/.+')

            if pattern.match(self.path):
                print '[>] Got a match'
                out = string.replace(self.path, '/py/', '')
                out = urllib.unquote_plus(out)
                print out
                foo = do_wiki_call(out)

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(foo)
                return

            else:
                return SimpleHandler.do_GET(self)

        except IOError:
            self.send_error(404, 'foobar foo')

httpd = SocketServer.TCPServer(("", PORT), Handler)


def main():

    # port is 3000 by default
    port = PORT

    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    try:
        print "[!] Serving at port: ", port
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "[!] Stopping server."
        httpd.socket.close()

if __name__ == '__main__':
    main()
