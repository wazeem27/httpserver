import os
import math
import logging
import cv2
import numpy as np


# Load prebuilt model for Frontal Face
CASCADE_PATH = "haarcascade_frontalface_default.xml"

# threshold values
MIN_TEMP_RANGE = 90.0
MAX_TEMP_RANGE = 100.0
DISTANCE_OFFSET = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


class ResponseHandler:
    
    def __init__(self, req_obj, data_type, data):
        self.req_obj = req_obj
        self.data_type = data_type
        self.post_data = data
        self.status_code = None
        self.message = None
        self.error = False
        self.process_post_data()
    
    def process_post_data(self):
        if self.data_type == 'invalid':
            error_message = "Invalid Input."
            self.response_setter(404, error_message)
        
        elif self.data_type == 'temp':
            self._set_temp_value()
        
        elif self.data_type == 'temp_array':
            self._set_temp_array()
        
        elif self.data_type == 'image':
            self._draw_bounding_box()
        else:
            self.response_setter(400, "Passing Empty Data.", error=True)
    
    def _set_temp_value(self):
        temp_value = bytes(self.post_data[:-1], encoding='utf8')
        self.req_obj.PlotData['temp_value'] = temp_value
        self.req_obj.PlotData['temp_float_value'] = float(self.post_data[:-1])
        logging.info("Got Temperature value --- {}\n".format(temp_value.decode()))
        self.response_setter(200, "Success")
    
    def _set_temp_array(self):
        # Expecting comma sep temperature float values
        try:
            temp_array = [float(value.strip()) for value in self.post_data.split(',') if value ]
            self.req_obj.PlotData['temp_array'] = temp_array
        except Exception as error:
            self.response_setter(500, error)
        else:
            self.response_setter(200, "Got temperature array --length={}".format(len(temp_array)))

    # def _plot_data_into_image(self):
    #     logging.info("Got Image data\n")
    
    def _draw_bounding_box(self):
        try:
            logging.info("Creating bounding boxes...")
            np_img = np.array(bytearray(self.post_data), dtype=np.uint8)

            # Encodes an image into a memory buffer.
            encoded_image = cv2.imdecode(np_img, 1)
            gray = cv2.cvtColor(encoded_image, cv2.COLOR_BGR2GRAY)

            # Create classifier from prebuilt model
            face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            #For each face in faces
            for x, y, w, h in faces:
                cv2.rectangle(encoded_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                dist = self.convert_pixel_to_distance(w) # Call function to find distance

                if (self.req_obj.PlotData['temp_float_value'] >= MIN_TEMP_RANGE and
                        self.req_obj.PlotData['temp_float_value'] <= MAX_TEMP_RANGE):
                    
                    self.req_obj.PlotData['distance'] = int(round(dist/22))

                    if not self.req_obj.PlotData['sample_temp']:
                        self.req_obj.PlotData['temperature'] = (self.req_obj
                                                                    .PlotData['temp_float_value'])
                    else:
                        self.req_obj.PlotData['temperature']  = self.req_obj.PlotData['sample_temp']

                    self.req_obj.PlotData['temperature'] += DISTANCE_OFFSET[self.req_obj.PlotData['distance']]
                    self.req_obj.PlotData['latest_max'] = self.req_obj.PlotData['temperature']

                    # Put text describe who is in the picture
                    cv2.putText(encoded_image, (str(round(dist/22))+" feet"), (x, y-30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                    temp_value = str(self.req_obj.PlotData['temperature']) + ' F'
                    cv2.putText(encoded_image, temp_value, (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                else:
                    # Put text describe who is in the picture
                    cv2.putText(encoded_image, (str(round(dist/22))+" feet"), (x, y-30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                    temp_value = str(self.req_obj.PlotData['latest_max']) + ' F'
                    cv2.putText(encoded_image, temp_value, (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            # Setting SAMPLE_TEMP_ARRAY 
            if len(self.req_obj.PlotData['sample_temp_array']) == 10:
                self.req_obj.PlotData['sample_temp_array'].pop(0)
                self.req_obj.PlotData['sample_temp_array'].append(self.req_obj.PlotData['temp_float_value'])
            else:
                self.req_obj.PlotData['sample_temp_array'].append(self.req_obj.PlotData['temp_float_value'])
            
            temp_array_sum = sum(self.req_obj.PlotData['sample_temp_array'])
            len_temp_array = len(self.req_obj.PlotData['sample_temp_array'])
            self.req_obj.PlotData['sample_temp'] = round(temp_array_sum/len_temp_array, 1)

            # Display the video frame with the bounded rectangle
            image_data = cv2.imencode('.jpg', encoded_image)[1].tobytes()
            logging.info("Bounding box creation completed.")
            self.req_obj.PlotData['image_data'] = image_data
            self.response_setter(200, "Success.")
        except Exception as err:
            self.response_setter(500, err, error=False)

    
    def response_setter(self, return_code, message, error=False):
        self.status_code = return_code
        self.message = message
        self.error = error

    @staticmethod
    def convert_pixel_to_distance(pixel_value):
        """
        Convert pixel value to distance in inches
        Args:
            pixel_value (int)
        Return distance in inches (float value)
        """
        val1 = 81.34
        val2 = -0.0039646
        return val1 * math.pow(math.e, val2*pixel_value)

    @property
    def response(self):
        return (self.status_code, self.message, self.error)
