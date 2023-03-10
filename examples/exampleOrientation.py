import sys
import cv2
import json
import numpy as np
from scipy.spatial.transform import Rotation as R
sys.path.insert(1, '../')
import pykinect_azure as pykinect
import datetime

import pandas as pd
import csv




if __name__ == "__main__":

    video_filename = "1frontalabdsidesto180.mkv"

    # Initialize the library, if the library is not found, add the library path as argument
    pykinect.initialize_libraries(track_body=True)

    # Start playback
    playback = pykinect.start_playback(video_filename)

    playback_config = playback.get_record_configuration()
    # print(playback_config)

    playback_calibration = playback.get_calibration()

    # Start body tracker
    bodyTracker = pykinect.start_body_tracker(calibration=playback_calibration)

    cv2.namedWindow('Depth image with skeleton', cv2.WINDOW_NORMAL)

    runtimeseconds = 9
    fps = 0
    joints = np.zeros(shape=(0, 18, 3))
    # joints = np.zeros(shape=(0, 32, 3))
    endTime = datetime.datetime.now() + datetime.timedelta(seconds=runtimeseconds)
    skips = 0
    timestamps = []
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
    # Open CSV file for writing
    with open('orientations-shoulderabd0to180frontal.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Shoulder W', 'Shoulder X', 'Shoulder Y', 'Shoulder Z',
                         'Clavicle W', 'Clavicle X', 'Clavicle Y', 'Clavicle Z',
                         'Spine W', 'Spine X', 'Spine Y', 'Spine Z',
                         'Elbow W', 'Elbow X', 'Elbow Y', 'Elbow Z'])

        while playback.isOpened():

            # Get camera capture
            capture = playback.update()

            # Get body tracker frame
            body_frame = bodyTracker.update(capture=capture)

            # Get the colored depth
            ret, depth_color_image = capture.get_colored_depth_image()

            # Get the colored body segmentation
            ret, body_image_color = body_frame.get_segmentation_image()

            if not ret:
                continue

            # testing depth

            try:
                # bodies = body_frame.get_bodies()[0].numpy()
                bodies = body_frame.get_bodies()[0]
                shoulder = None
                clavicle = None
                spine = None
                elbow = None
                for joint in bodies.joints:
                    if joint.name == "right elbow":
                        elbow = joint.orientation
                    if joint.name == 'right shoulder':
                        # print("found shoulder")
                        shoulder = joint.orientation
                        print("try shoulder")
                        print(shoulder.w)
                        print(shoulder)
                    if joint.name == "right clavicle":
                        # print("found right clavicle")
                        clavicle = joint.orientation
                    if joint.name == "spine - chest":
                        # print("found spine - chest")
                        spine = joint.orientation
                if shoulder is not None and clavicle is not None and spine is not None and elbow is not None:
                    print(f"in the row loop {shoulder.w}")
                    writer.writerow([shoulder.w, shoulder.x, shoulder.y, shoulder.z,
                                     clavicle.w, clavicle.x, clavicle.y, clavicle.z,
                                     spine.w, spine.x, spine.y, spine.z,
                                     elbow.w, elbow.x, elbow.y, elbow.z])


                # get timestamp in usec
                fTimestamp = body_frame.get_device_timestamp_usec()
                timestamps.append(fTimestamp)
                # print(fTimestamp)

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
                cv2.imshow('Depth image with skeleton', combined_image)
            except:
                skips = skips + 1

            # end testing depth

            # Combine both images
            combined_image = cv2.addWeighted(depth_color_image, 0.6, body_image_color, 0.4, 0)

            # Draw the skeletons
            combined_image = body_frame.draw_bodies(combined_image)

            # Overlay body segmentation on depth image
            cv2.imshow('Depth image with skeleton', combined_image)

            # Press q key to stop
            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()


    # # Write the angles to the CSV file
    # with open('abd2jointcords.csv', mode='a', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(angles)

    print("done with angles csv")
