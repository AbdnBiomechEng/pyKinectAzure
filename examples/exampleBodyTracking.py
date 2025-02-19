import sys
import cv2
import json
import numpy as np
sys.path.insert(1, '../')
import pykinect_azure as pykinect
import datetime
import math
import time

# Writes the data in a TRC file
def writeTRC(data, file):

	# Write header
	file.write("PathFileType\t4\t(X/Y/Z)\toutput.trc\n")
	file.write("DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n")
	file.write("%d\t%d\t%d\t%d\tmm\t%d\t%d\t%d\n" % (data["DataRate"], data["CameraRate"], data["NumFrames"],
													 data["NumMarkers"], data["OrigDataRate"],
													 data["OrigDataStartFrame"], data["OrigNumFrames"]))

	# Write labels
	file.write("Frame#\tTime\t")
	for i, label in enumerate(data["Labels"]):
		if i != 0:
			file.write("\t")
		# file.write("\t\t%s" % (label))
		file.write("%s\t\t" % (label))
	file.write("\n")
	file.write("\t")
	for i in range(len(data["Labels"]*3)):
		file.write("\t%c%d" % (chr(ord('X')+(i%3)), math.ceil((i+1)/3)))
	file.write("\n")

	# Write data
	for i in range(len(data["Data"])):
		file.write("%d\t%f" % (i, data["Timestamps"][i]))
		for l in range(len(data["Data"][0])):
			# file.write("\t%f\t%f\t%f" % tuple(data["Data"][l][i]))
			file.write("\t%f\t%f\t%f" % tuple(data["Data"][i][l]))
		file.write("\n")


if __name__ == "__main__":
	time.sleep(3)
	# Initialize the library, if the library is not found, add the library path as argument
	pykinect.initialize_libraries(track_body=True)

	# Modify camera configuration
	device_config = pykinect.default_configuration
	device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
	device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
	device_config.synchronized_images_only = True

	device_config.wired_sync_mode = 1

	print(device_config)

	# Start device
	device = pykinect.start_device(config=device_config)

	# Start body tracker
	bodyTracker = pykinect.start_body_tracker()

	cv2.namedWindow('Depth image with skeleton',cv2.WINDOW_NORMAL)
	runtimeseconds = 9
	fps = 0
	joints = np.zeros(shape=(0, 18, 3))
	# joints = np.zeros(shape=(0, 32, 3))
	endTime = datetime.datetime.now() + datetime.timedelta(seconds=runtimeseconds)
	skips = 0


	import numpy as np

	data = {'DataRate': 20,
			'CameraRate': 20,
			'NumFrames': runtimeseconds * 20,
			'NumMarkers': 18,
			'OrigDataRate': 20,
			'OrigDataStartFrame': 1,
			'OrigNumFrames': 1,
			'Labels': [
					   'K4ABT_JOINT_PELVIS',
					   'K4ABT_JOINT_SPINE_NAVEL',
					   'K4ABT_JOINT_SPINE_CHEST',
					   'K4ABT_JOINT_NECK',
					   'K4ABT_JOINT_CLAVICLE_LEFT',
					   'K4ABT_JOINT_SHOULDER_LEFT',
					   'K4ABT_JOINT_ELBOW_LEFT',
					   'K4ABT_JOINT_WRIST_LEFT',
					   'K4ABT_JOINT_HAND_LEFT',
					   'K4ABT_JOINT_HANDTIP_LEFT',
					   'K4ABT_JOINT_THUMB_LEFT',
					   'K4ABT_JOINT_CLAVICLE_RIGHT',
					   'K4ABT_JOINT_SHOULDER_RIGHT',
					   'K4ABT_JOINT_ELBOW_RIGHT',
					   'K4ABT_JOINT_WRIST_RIGHT',
					   'K4ABT_JOINT_HAND_RIGHT',
					   'K4ABT_JOINT_HANDTIP_RIGHT',
					   'K4ABT_JOINT_THUMB_RIGHT',
					   # 'K4ABT_JOINT_HIP_LEFT',
					   # 'K4ABT_JOINT_KNEE_LEFT',
					   # 'K4ABT_JOINT_ANKLE_LEFT',
					   # 'K4ABT_JOINT_FOOT_LEFT',
					   # 'K4ABT_JOINT_HIP_RIGHT',
					   # 'K4ABT_JOINT_KNEE_RIGHT',
					   # 'K4ABT_JOINT_ANKLE_RIGHT',
					   # 'K4ABT_JOINT_FOOT_RIGHT',
					   # 'K4ABT_JOINT_HEAD',
					   # 'K4ABT_JOINT_NOSE',
					   # 'K4ABT_JOINT_EYE_LEFT',
					   # 'K4ABT_JOINT_EAR_LEFT',
					   # 'K4ABT_JOINT_EYE_RIGHT',
					   # 'K4ABT_JOINT_EAR_RIGHT'
					   ],
			'Data': [],
			'Timestamps': []
			}

	while fps < (runtimeseconds * 30):
		# if datetime.datetime.now() >= endTime:
		# 	break
		# Get capture
		capture = device.update()

		# Get body tracker frame
		body_frame = bodyTracker.update()

		# Get the color depth image from the capture
		ret, depth_color_image = capture.get_colored_depth_image()

		# Get the colored body segmentation
		ret2, body_image_color = body_frame.get_segmentation_image()

		if not ret:
			skips = skips + 1
			continue




		# with open("C:/Users/bradl/Documents/GitHub/occlusion-study/calibration/testPrettyPrint1.json", "w") as write_file:
		# 	json.dump(body_frame.json(), write_file, indent=4)
		# 	print("json in file")
		try:
			bodies = body_frame.get_bodies()[0].numpy()


			fps = fps + 1
			bodies = np.delete(bodies, np.s_[18:], axis=0)
			#
			# bodies = np.reshape(bodies,(1,14,3))



			# bodies = np.reshape(bodies,(1,32,3))
			bodies = np.reshape(bodies, (1, 18, 3))
			joints = np.vstack((joints, bodies))


			#
			# https: // github.com / ibaiGorordo / pyKinectAzure / blob / 538111
			# ccbe1c0c19151ed742e143bf32a0d90978 / pykinect_azure / k4abt / _k4abtTypes.py  # L25


			# Combine both images
			combined_image = cv2.addWeighted(depth_color_image, 0.6, body_image_color, 0.4, 0)

			# Draw the skeletons
			combined_image = body_frame.draw_bodies(combined_image)

			# Overlay body segmentation on depth image
			cv2.imshow('Depth image with skeleton',combined_image)
		except:
			skips = skips + 1



		# Press q key to stop
		if cv2.waitKey(1) == ord('q'):
			break
	cv2.destroyAllWindows()

	print("joints shape before")
	print(joints.shape)

	print("before joints row")
	import c3d
	writer = c3d.Writer()

	for row in joints:
		data['Data'].append(row)
		print(row)
		print("next row/TIMESTAMP ")
	print("after joints row")

	print(f"length of data is {len(data['Data'])} which is number of frames")
	print(f"length of data 0 is {len(data['Data'][0])}  which is number of markers")

	print("joints shape")
	print(joints.shape)
	print(f"fps {fps}")
	print(f"skips {skips}")

	timestamps = list(range(0, fps))

	data['Timestamps'] = timestamps
	data['DataRate'] = fps/runtimeseconds
	data['CameraRate'] = fps/runtimeseconds
	data['OrigDataRate'] = fps/runtimeseconds
	# data['NumMarkers']= 27
	data['NumFrames'] = fps

	fname = input("Please enter a filename: ")
	print("C:/Users/bradl/Documents/GitHub/occlusion-study/c3d/: " + fname + ".trc")

	outname = "C:/Users/bradl/Documents/GitHub/occlusion-study/c3d/"
	ext = ".trc"

	fullname = outname + fname + ext
	# outputfile = open("C:/Users/bradl/Documents/GitHub/occlusion-study/c3d/tmp.trc", "w")

	outputfile = open(fullname, "w")
	# Write the data into the TRC file
	writeTRC(data, outputfile)



	# Clean up
	outputfile.close()
	print("fin")


	# use frames for time not clock time as this will depend on processor speed
	quit()