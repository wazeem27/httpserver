"""
Simple HTTP Server.

This module builds on HTTPServer by implementing the standard GET
and POST requests in a fairly straightforward manner.
"""

from http.server import BaseHTTPRequestHandler
import logging 
import re

from utility import ResponseHandler


# Data for serving on GET requests
DATA = {
    "temp_value": bytes(), "image_data": bytes(), "temp_float_value": float(),
    "temperature": float(), "temp_array": [], "sample_temp": float(),
    "distance": int(), "cal_temp_value": float(), "latest_max": float(),
    "sample_temp_array": []
}


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET and POST commands."""

    PlotData = DATA  # For storing image and temp data

    def _set_response(self, status_code, message, error=False, content_type=None):
        """
        Set reponse for sending back to the client.
        Args:
            status_code (str): response status code
            message (str): message for logging
            error (boolean): False by default
            content_type (str): override default content type
        Return response object
        """
        if error:
            logging.error(message)
        else:
            logging.info(message)

        self.send_response(status_code)
        if content_type:
            # If content type then send image response
            logging.info("Sending image response to {}:{}".format(*self.client_address))
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(self.PlotData['image_data'])

    def do_GET(self):
        """
        Handles GET request
        """
        if self.path == '/':
            if not self.PlotData['image_data']:
                self._set_response(404, "File Not Found.")
            else:
                self._set_response(200, "Success", content_type="image/jpg")
        else:
            self._set_response(404, "Path {} Not Found.".format(self.path), error=True)

    def do_POST(self):
        """
        Handles POST request
        """
        if self.path == '/':
            logging.info("POST request,\nPath: {}\nHeaders:\n{}".format(self.path, self.headers))
            # Parse POST data
            parsed_data = self._parse_incoming_data()
            response_handler = ResponseHandler(self, *parsed_data)
            return_code, message, error = response_handler.response
            self._set_response(return_code, message, error=error)
        else:
            self._set_response(404, "Path {} Not Found.".format(self.path), error=True) 

    def _parse_incoming_data(self):
        """
        Parse the incoming input data (the data should be binary buffer format)
        
        Use re for finding the whether the uploaded data is image, temperature or
        temperature array.
        
        Return tuple with (string (denotes type), data (parsed bytes string))
        """
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        if isinstance(post_data, bytes):
            try:
                post_data = post_data.decode().strip()
            except UnicodeDecodeError as error:
                # Incoming data is image
                return 'image', post_data
            if len(post_data) == 0:
                return 'invalid', post_data
            elif re.search("^[0-9]+\.[0-9]+F$", post_data):
                return 'temp', post_data
            elif re.search("[0-9\.\s,]+$", post_data):
                return 'temp_array', post_data
            else:
                return "invalid", post_data
        else:
            return 'invalid', post_data

