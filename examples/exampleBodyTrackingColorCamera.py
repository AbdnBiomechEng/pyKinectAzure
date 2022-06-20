import sys
import cv2
import pandas as pd
import json

sys.path.insert(1, '../')
import pykinect_azure as pykinect

if __name__ == "__main__":

    def __str__(self):

        """Print the current settings and a short explanation"""
        message = (
            f"#{self.name} Joint info: \n"
            f"\tposition: [{self.position.x},{self.position.y},{self.position.z}]\n"
            f"\torientation: [{self.orientation.w},{self.orientation.x},{self.orientation.y},{self.orientation.z}]\n"
            f"\tconfidence: {self.confidence_level} \n\n")
        return message

	# Overriding joint to string method so we can seperate joints by # for the csv
    pykinect.k4abt.Joint.__str__ = __str__

    # Initialize the library, if the library is not found, add the library path as argument
    pykinect.initialize_libraries(track_body=True)

    # Modify camera configuration
    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
    # print(device_config)

    # Start device
    device = pykinect.start_device(config=device_config)

    # Start body tracker
    bodyTracker = pykinect.start_body_tracker()

    cv2.namedWindow('Color image with skeleton', cv2.WINDOW_NORMAL)
    while True:

        # Get capture
        capture = device.update()

        # Get body tracker frame
        body_frame = bodyTracker.update()

		# Get frame timestamp
        fTimestamp = body_frame.get_device_timestamp_usec()

        print(f"frame time stamp is {fTimestamp}")

        # Get the color image
        ret, color_image = capture.get_color_image()

        num_bodies = body_frame.get_num_bodies()

        print(f'number of bodies is {num_bodies}')

		# Get frame info as string
        frameMsg = body_frame.get_body().__str__()

		# Split frame by # i.e. each joint tracked into array
        splits = frameMsg.split("#");

		# Add timestamp to start of each frame
        splits.insert(0, "time stamp" + str(fTimestamp))

        df = pd.DataFrame(splits)

		# Save frame to csv
        df.to_csv('JointsTracked.csv', mode='a')

        if not ret:
            continue

        # Draw the skeletons into the color image
        color_skeleton = body_frame.draw_bodies(color_image, pykinect.K4A_CALIBRATION_TYPE_COLOR)

        # Overlay body segmentation on depth image
        cv2.imshow('Color image with skeleton', color_skeleton)

        # Press q key to stop
        if cv2.waitKey(1) == ord('q'):
            break