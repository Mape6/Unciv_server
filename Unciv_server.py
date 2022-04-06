import http.server
import socketserver
import os
import re

port = 8080
uuid_regex = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'


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
            self.send_response(404)
            self.end_headers()
            self.wfile.write("File not found".encode())
    
    def write_file_content(self, path, content_length):
        try:
            os.makedirs(os.path.dirname(path))
        except FileExistsError:
            pass
        with open(path, 'wb') as f:
            f.write(self.rfile.read(content_length))
        self.send_response(201)
        self.end_headers()

    def do_GET(self):
        # Check for preview file name and send content to client
        if re.search(f'\/files\/{uuid_regex}_Preview$', self.path):
            path = self.translate_path(self.path)
            self.send_file_content(path)
        # Check for game file name and send content to client
        elif re.search(f'\/files\/{uuid_regex}$', self.path):
            path = self.translate_path(self.path)
            self.send_file_content(path)
        # Check for connection check and response with 'true'
        elif self.path.endswith('isalive'):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("true".encode())
        # Everything else is not allowed
        else:
            self.send_response(401)
            self.end_headers()

    def do_PUT(self):
        # Check for preview file name and write content to file
        if len(self.path) <= 128:
            if re.search(f'\/files\/{uuid_regex}_Preview$', self.path) or re.search(f'\/files\/{uuid_regex}$', self.path):
                path = self.translate_path(self.path)
                if int(self.headers['Content-Length']) <= 1048576:
                    content_length = int(self.headers['Content-Length'])
                    self.write_file_content(path, content_length)
                else:
                    self.send_response(401)
                    self.end_headers()
            # Everything else is not allowed
            else:
                self.send_response(401)
                self.end_headers()
        else:
            self.send_response(401)
            self.end_headers()
    
    def do_DELETE(self):
        # TODO: write method for deleting a game file
        pass


Handler = MyHttpRequestHandler

try:
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f'HTTP server serving at port {port}')
        httpd.serve_forever()
except OSError as error:
    if error.errno == 10048:
        print(f'ERROR: Port {port} is already used by any other service!')
    else:
        print(error)
