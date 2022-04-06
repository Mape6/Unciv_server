import http.server
import socketserver
import os
import re

port = 8080
uuid_regex = r'[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}'


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_file_content(self, path):
        try:
            with open(path, 'r') as save_file:
                file_content = save_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(file_content.encode())
        except FileNotFoundError:
            self.send_response(404, "File not found")
            self.end_headers()
            self.wfile.write("File not found".encode())
    
    def write_file_content(self, path, content_length):
        try:
            os.makedirs(os.path.dirname(path))
        except FileExistsError:
            pass
        with open(path, 'wb') as f:
            f.write(self.rfile.read(content_length))
        self.send_response(201, "Created")
        self.end_headers()

    def do_GET(self):
        # Response for connection check
        if self.path.endswith('isalive'):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("true".encode())
        # Response with game preview file
        elif re.search(f'\/files\/{uuid_regex}_Preview$', self.path):
            path = self.translate_path(self.path)
            self.send_file_content(path)
        # Response with game file
        elif re.search(f'\/files\/{uuid_regex}$', self.path):
            path = self.translate_path(self.path)
            self.send_file_content(path)
        else:
            self.send_response(401)
            self.end_headers()

    def do_PUT(self):
        # Check if path ends with '/' that is not allowed
        if self.path.endswith('/'):
            self.send_response(405)
            self.end_headers()
        # Check for preview file name
        elif re.search(f'\/files\/{uuid_regex}_Preview$', self.path):
            path = self.translate_path(self.path)
            content_length = int(self.headers['Content-Length'])
            self.write_file_content(path, content_length)
        # Check for game file name
        elif re.search(f'\/files\/{uuid_regex}$', self.path):
            path = self.translate_path(self.path)
            content_length = int(self.headers['Content-Length'])
            self.write_file_content(path, content_length)
        # Everything else is not allowed
        else:
            self.send_response(401)
            self.end_headers()


Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f'HTTP server serving at port {port}')
    httpd.serve_forever()
