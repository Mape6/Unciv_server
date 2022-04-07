#!/usr/bin/env python3

import http.server
import socketserver
import os
import re
import argparse

parser = argparse.ArgumentParser(description='This is a simple HTTP webserver for Unciv')

parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Verbose output'
                    )
parser.add_argument('-p', '--port',
                    action='store',
                    default='8080',
                    type=int,
                    help='Specifies the port on which the server should listen'
                    )

args = parser.parse_args()

port = args.port
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
        # Check if path is not too long
        if len(self.path) <= 128:
            # Check path for preview or game file name
            if re.search(f'\/files\/{uuid_regex}_Preview$', self.path) or re.search(f'\/files\/{uuid_regex}$', self.path):
                path = self.translate_path(self.path)
                # Check if Content-Length is not too long
                # TODO: Check if the value is big enough
                if int(self.headers['Content-Length']) <= 1048576:
                    content_length = int(self.headers['Content-Length'])
                    self.write_file_content(path, content_length)
                # If Content-Length is too long -> send 401
                else:
                    self.send_response(401)
                    self.end_headers()
            # If path does not have the right file names -> send 401
            else:
                self.send_response(401)
                self.end_headers()
        # If path length is too long -> send 401
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
