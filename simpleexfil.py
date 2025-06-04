import http.server
import socketserver
import os
import cgi
import sys

DEFAULT_PORT = 8000

port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        html = '''
        <html>
        <head>
        <title>Upload File</title>
        </head>
        <body>
        <form enctype="multipart/form-data" method="post">
        <input name="file" type="file"/>
        <input type="submit" value="Upload"/>
        </form>
        </body>
        </html>
        '''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        filename = os.path.basename(form['file'].filename)
        file_data = form['file'].file.read()

        base, ext = os.path.splitext(filename)
        target = filename
        counter = 1
        while os.path.exists(target):
            target = f"{base}_{counter}{ext}"
            counter += 1

        with open(target, 'wb') as f:
            f.write(file_data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Uploaded {filename}\n".encode('utf-8'))

with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    print(f"serving at port {port}")
    httpd.serve_forever()
