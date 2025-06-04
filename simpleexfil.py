import http.server
import socketserver
import os
from email import message_from_binary_file
from email.policy import default
from io import BytesIO
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
        codex/switch-to-email.message_from_binary_file
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        ct = self.headers.get('Content-Type', '')

        msg_bytes = b'Content-Type: ' + ct.encode() + b"\r\n\r\n" + body
        msg = message_from_binary_file(BytesIO(msg_bytes), policy=default)

        filename = None
        file_data = None
        for part in msg.walk():
            if part.get_content_disposition() == 'form-data':
                if part.get_param('name', header='Content-Disposition') == 'file':
                    filename = part.get_filename()
                    file_data = part.get_payload(decode=True)
                    break

        if filename and file_data is not None:
            with open(filename, 'wb') as f:
                f.write(file_data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Uploaded {filename}\n".encode('utf-8'))

with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    print(f"serving at port {port}")
    httpd.serve_forever()
