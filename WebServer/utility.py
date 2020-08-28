import os
import math



def convert_pixel_to_distance(pix):
    """Converts pixel value to distance in inches"""
    val1 = 81.34
    val2 = -0.0039646
    distance = val1 * math.pow(math.e, val2*pix)
    # dans = (96.93 * (0.995**pix))
    return distance


def draw_bounding_box(image_data):
    """
    Draw bounding box for detected faces
    """
    try:
        logging.info("Creating bounding boxes...")
        np_img = np.array(bytearray(image_data), dtype=np.uint8)

        # Encodes an image into a memory buffer.
        encoded_image = cv2.imdecode(np_img, 1)
        gray = cv2.cvtColor(encoded_image, cv2.COLOR_BGR2GRAY)

        # Create classifier from prebuilt model
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        #For each face in faces
        for x, y, w, h in faces:
            cv2.rectangle(encoded_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            dist = convert_pixel_to_distance(w) # Call function to find distance
            if TEMP_FLOAT_VALUE >= MIN_TEMP_RANGE and TEMP_FLOAT_VALUE <= MAX_TEMP_RANGE:
                global DISTANCE
                DISTANCE = int(round(dist/22))
                global TEMPERATURE
                global SAMPLE_TEMP
                if not SAMPLE_TEMP:
                    TEMPERATURE = TEMP_FLOAT_VALUE
                else:
                    TEMPERATURE  = SAMPLE_TEMP

                TEMPERATURE = TEMPERATURE + DISTANCE_OFFSET[DISTANCE]
                global LATEST_MAX
                LATEST_MAX = TEMPERATURE
                # Put text describe who is in the picture
                cv2.putText(encoded_image, (str(round(dist/22))+" feet"), (x, y-30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                temp_value = str(TEMPERATURE) + ' F'
                cv2.putText(encoded_image, temp_value, (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            else:
                # Put text describe who is in the picture
                cv2.putText(encoded_image, (str(round(dist/22))+" feet"), (x, y-30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                temp_value = str(LATEST_MAX) + ' F'
                cv2.putText(encoded_image, temp_value, (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Setting SAMPLE_TEMP_ARRAY 
        global SAMPLE_TEMP_ARRAY
        if len(SAMPLE_TEMP_ARRAY) == 10:
            SAMPLE_TEMP_ARRAY.pop(0)
            SAMPLE_TEMP_ARRAY.append(TEMP_FLOAT_VALUE)
        else:
            SAMPLE_TEMP_ARRAY.append(TEMP_FLOAT_VALUE)

        SAMPLE_TEMP = round(sum(SAMPLE_TEMP_ARRAY)/len(SAMPLE_TEMP_ARRAY), 1)

        # Display the video frame with the bounded rectangle
        image_data = cv2.imencode('.jpg', encoded_image)[1].tobytes()
        logging.info("Bounding box creation completed.")
        global IMAGE_DATA
        IMAGE_DATA = image_data
        return 200, "Success."
    except Exception as error:
        return 500, error

