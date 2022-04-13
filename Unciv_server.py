#!/usr/bin/env python3

import http.server
import socketserver
import ssl
import os
import re
import argparse
import logging
from http import HTTPStatus


parser = argparse.ArgumentParser(description='This is a simple HTTP webserver for Unciv')

parser.add_argument('-p', '--port',
                    action='store',
                    default='80',
                    type=int,
                    help='Specifies the port on which the server should listen (default: %(default)s)'
                    )
parser.add_argument('-l', '--log-level',
                    default='WARNING',
                    choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                    help='Change logging level (default: %(default)s)'
                    )
parser.add_argument('-s', '--ssl',
                    action='store_true',
                    help='Starts a HTTPS server instead of HTTP'
                    )

args = parser.parse_args()

if 1 <= args.port <= 65535:
    port = args.port
else:
    parser.error('Port needs to be an integer between 1 and 65535')

logging.basicConfig(level=args.log_level, format='%(asctime)s - %(levelname)s - %(message)s')

regex_uuid = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
regex_path = '\/files\/'

suffix_preview_file = '_Preview'
suffix_lock_file = '_Lock'

regexc_main_game_file = re.compile(rf'^{regex_path}{regex_uuid}$')
regexc_preview_file = re.compile(rf'^{regex_path}{regex_uuid}{suffix_preview_file}$')
regexc_lock_file = re.compile(rf'^{regex_path}{regex_uuid}{suffix_lock_file}$')
regexc_all_game_files = re.compile(rf'^{regex_path}{regex_uuid}({suffix_preview_file}|{suffix_lock_file}|$)$')

max_path_length = 128
max_content_length = 1048576  # (1 MB is really enough)


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_file_content(self, path, client_ip):
        try:
            with open(path, 'r') as save_file:
                file_content = save_file.read()
            http_status = HTTPStatus.OK
            logging.info(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(file_content.encode())
        except FileNotFoundError:
            http_status = HTTPStatus.NOT_FOUND
            logging.warning(f'Client: {client_ip}, Request: "{self.requestline}", HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()
    
    def write_file_content(self, path, content_length, client_ip):
        # If the dir does not exist -> create it
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
                logging.info(f'Path {os.path.dirname(path)} created.')
            # If dir could not be created -> log the exception and send 500 Internal Server Error
            except Exception as e:
                logging.critical(f'Path {os.path.dirname(path)} could not be created. Exception: {e}')
                http_status = HTTPStatus.INTERNAL_SERVER_ERROR
                logging.critical(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                self.send_response_only(http_status)
                self.end_headers()

        # Write content to file
        try:
            with open(path, 'wb') as f:
                f.write(self.rfile.read(content_length))
            http_status = HTTPStatus.CREATED
            logging.info(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()
        # If file could not be created -> log the exception and send 500 Internal Server Error
        except Exception as e:
            logging.critical(f'File {path} could not be created. Exception: {e}')
            http_status = HTTPStatus.INTERNAL_SERVER_ERROR
            logging.critical(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    def delete_file(self, path, client_ip):
        if os.path.exists(path):
            os.remove(path)
            http_status = HTTPStatus.OK
            logging.info(f'Client: {client_ip}, Request: "{self.requestline}", HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()
        else:
            http_status = HTTPStatus.NOT_FOUND
            logging.warning(f'Client: {client_ip}, Request: "{self.requestline}", HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    def do_GET(self):
        # Check if X-Forwarded-For is present in headers -> use client IP out of it
        if self.headers['X-Forwarded-For']:
            client_ip = self.headers['X-Forwarded-For']
        else:
            client_ip = self.address_string()

        # Check path for game file names -> send file content
        if regexc_all_game_files.search(self.path):
            path = self.translate_path(self.path)
            self.send_file_content(path, client_ip)

        # Check for connection check and response with 'true'
        elif self.path.endswith('isalive'):
            http_status = HTTPStatus.OK
            logging.info(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("true".encode())

        # Everything else is not allowed
        else:
            http_status = HTTPStatus.FORBIDDEN
            logging.warning(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    def do_PUT(self):
        # Check if X-Forwarded-For is present in headers -> use client IP out of it
        if self.headers['X-Forwarded-For']:
            client_ip = self.headers['X-Forwarded-For']
        else:
            client_ip = self.address_string()

        # Check if path is not too long
        if len(self.path) <= max_path_length:

            # Check if Content-Length is not too big
            if int(self.headers['Content-Length']) <= max_content_length:
                content_length = int(self.headers['Content-Length'])

                # Check path for preview file name
                if regexc_preview_file.search(self.path):
                    path = self.translate_path(self.path)
                    self.write_file_content(path, content_length, client_ip)

                # Check path for main game file name
                elif regexc_main_game_file.search(self.path):
                    path = self.translate_path(self.path)
                    self.write_file_content(path, content_length, client_ip)

                # Check path for lock file name
                elif regexc_lock_file.search(self.path):
                    path = self.translate_path(self.path)
                    self.write_file_content(path, content_length, client_ip)

                # If path does not have the right file names -> send 403 FORBIDDEN
                else:
                    http_status = HTTPStatus.FORBIDDEN
                    logging.warning(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                    self.send_response_only(http_status)
                    self.end_headers()

            # If Content-Length is too long -> send 400 BAD REQUEST
            else:
                http_status = HTTPStatus.BAD_REQUEST
                logging.warning(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                self.send_response_only(http_status)
                self.end_headers()

        # If path length is too long -> send 400 BAD REQUEST
        else:
            http_status = HTTPStatus.BAD_REQUEST
            logging.warning(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()
    
    def do_DELETE(self):
        # Check if X-Forwarded-For is present in headers -> use client IP out of it
        if self.headers['X-Forwarded-For']:
            client_ip = self.headers['X-Forwarded-For']
        else:
            client_ip = self.address_string()

        # Check if path is not too long
        if len(self.path) <= max_path_length:

            # Check path for game file names
            if regexc_all_game_files.search(self.path):
                path = self.translate_path(self.path)
                self.delete_file(path, client_ip)

            # If path does not have the right file names -> send 403 FORBIDDEN
            else:
                http_status = HTTPStatus.FORBIDDEN
                logging.warning(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                self.send_response_only(http_status)
                self.end_headers()

        # If path length is too long -> send 400 BAD REQUEST
        else:
            http_status = HTTPStatus.BAD_REQUEST
            logging.warning(f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()


Handler = MyHttpRequestHandler

# If ssl is not set -> start HTTP server
if not args.ssl:
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f'HTTP server serving at port {port}')
            httpd.serve_forever()
    except OSError as error:
        if error.errno == 10048:
            logging.error(f'Port {port} is already used by any other service!')
        else:
            print(error)
# Else ssl is set -> start HTTPS server
else:
    try:
        context = ssl.create_default_context()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('localhost.crt', 'localhost.key')
        with socketserver.TCPServer(("", port), Handler) as httpsd:
            httpsd.socket = context.wrap_socket(httpsd.socket)
            print(f'HTTPS server serving at port {port}')
            httpsd.serve_forever()
    except OSError as error:
        if error.errno == 10048:
            logging.error(f'Port {port} is already used by any other service!')
        else:
            print(error)
