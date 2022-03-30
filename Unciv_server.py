import http.server
import socketserver
import os
import re

port = 8080


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('favicon.ico'):
            self.send_response(404)
            self.end_headers()
        elif self.path.endswith('isalive'):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("true".encode())
        elif re.search(r'\/files\/[a-zA-Z0-9-_]+$', self.path):
            path = self.translate_path(self.path)
            if path.endswith('/'):
                self.send_response(405, "Method Not Allowed")
                self.wfile.write("PUT not allowed on a directory\n".encode())
                return
            else:
                try:
                    with open(path, 'r') as f:
                        file_content = f.read()
                        self.send_response(200)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        self.wfile.write(file_content.encode())
                except FileNotFoundError:
                    self.send_response(404, "File not found")
                    self.wfile.write("File not found\n".encode())
                
                # return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_response(404)
            self.end_headers()
    def do_PUT(self):
        path = self.translate_path(self.path)
        if path.endswith('/'):
            self.send_response(405, "Method Not Allowed")
            self.wfile.write("PUT not allowed on a directory\n".encode())
            return
        else:
            try:
                os.makedirs(os.path.dirname(path))
            except FileExistsError:
                pass
            length = int(self.headers['Content-Length'])
            with open(path, 'wb') as f:
                f.write(self.rfile.read(length))
            self.send_response(201, "Created")
            self.end_headers()


Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f'HTTP server serving at port {port}')
    httpd.serve_forever()
