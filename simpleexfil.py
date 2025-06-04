import http.server
import socketserver
import os
import cgi
import sys

DEFAULT_PORT = 8000

port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.path = '/static/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        filename = form['file'].filename
        file_data = form['file'].file.read()
        with open(filename, 'wb') as f:
            f.write(file_data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Uploaded {filename}\n".encode('utf-8'))

with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    print(f"serving at port {port}")
    httpd.serve_forever()
