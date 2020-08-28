from http.server import BaseHTTPRequestHandler


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET and POST commands."""

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
            self.wfile.write(IMAGE_DATA)

    def do_GET(self):
        """
        Handles GET request
        """
        if self.path == '/':
            if not IMAGE_DATA:
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
            pass
        else:
            self._set_response(404, "Path {} Not Found.".format(self.path), error=True) 

    def _parse_incoming_data(self, content_length):
        """
        Parse the incoming input data
        """
        data = self.rfile.read(content_length)
        if isinstance(data, bytes) or isinstance(data, str):
            if isinstance(data, bytes):
                try:
                    data = data.decode().strip()
                except UnicodeDecodeError as error:
                    # Incoming data is image
                    return 'image', data
            if len(data) == 0:
                return 'invalid', data
            elif re.search("^[0-9]+\.[0-9]+F$", data):
                return 'temp', data
            elif re.search("[0-9\.\s,]+$", data):
                return 'temp_array', data
            else:
                return "invalid", data
        else:
            return 'invalid', data

