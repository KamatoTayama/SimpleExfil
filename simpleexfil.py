import http.server
import socketserver
import os
import cgi
import sys
import logging

DEFAULT_PORT = 8000

port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

        try:
            filename = form['file'].filename
            file_data = form['file'].file.read()
        except Exception as e:
            logging.error("Failed to read uploaded file: %s", e)
            self.send_error(400, "Invalid upload")
            return

        logging.info("Upload attempt from %s for %s", self.client_address[0], filename)

        try:
            with open(filename, 'wb') as f:
                f.write(file_data)
        except Exception as e:
            logging.error("Failed to save %s: %s", filename, e)
            self.send_error(500, "Failed to save file")
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Uploaded {filename}\n".encode('utf-8'))

with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    print(f"serving at port {port}")
    httpd.serve_forever()
