"""
Main method for running httpserver

Usage:
    
    python run.py
    Advanced usage ==> python httpserver --ip "127.0.0.1" --port 8000

    Send a GET request:
        curl -X GET http://<IP>:<PORT>
    
    Send a POST request (Temperature data):
        curl -X PORT http://<IP>:<PORT> --data "98.5F"

    Send a POST request (Temperature array)
        curl -X POST http://<IP>:<PORT> --data "34.6,45.8,78.9"

    Send a POST request (image data):
        curl -X POST http://<IP>:<PORT> --data-binary "@<image.jpg>"

"""

import argparse
from http.server import HTTPServer

from httpserver import SimpleHTTPRequestHandler


def main(server=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    # Create parser object
    parser = argparse.ArgumentParser(allow_abbrev=False,
                                     description=("A simple http server for image processing."))

    parser.add_argument("--ip", default='127.0.0.1', help="Ip address", type=str)
    parser.add_argument("--port", default=8080, help="port to listen", type=int)
    args = parser.parse_args()

    # binding command line args
    ip_address = args.ip
    port_number = args.port

    # Setting server
    server_address = (ip_address, port_number)
    logging.basicConfig(level=logging.INFO)
    
    httpd = server(server_address, handler_class)
    logging.info('Starting httpd... {}:{}\n'.format(*server_address))
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    main()

