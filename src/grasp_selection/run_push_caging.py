import numpy as np
import os
import sys
import csv
sys.path.append("/home/jmahler/sherdil_working/GPIS/src/grasp_selection/control/DexControls")

from DexAngles import DexAngles
from DexConstants import DexConstants
from DexController import DexController
from DexRobotZeke import DexRobotZeke
from ZekeState import ZekeState
from TurntableState import TurntableState

sys.path.append('/home/jmahler/sherdil_working/GPIS/src/grasp_selection')
import similarity_tf as stf
import tfx

import pdb


def is_float(string):
    try:
        float(string)
	return True
    except ValueError:
        return False

def convert_frame(object_x, object_y, object_theta):
    #This t's offset is in meters. Everything is in meters.
    t = np.array([0.0649615, 0.0, 0.0])
    R = np.array([[0, 1, 0],
                  [1, 0, 0],
                  [0, 0, 1]])
    grip_to_sim = stf.SimilarityTransform3D(pose=tfx.pose(R, t), scale=1.0, from_frame="gripper", to_frame="sim")

    t = np.array([object_x, object_y, 0.0])
    #We need offsets in meters, not pixels!
    t = t*pixels_to_meters
    R = np.array([[np.sin(object_theta), np.cos(object_theta), 0],
                  [np.cos(object_theta), -np.sin(object_theta), 0],
                  [0, 0, 1]])
    object_to_sim = stf.SimilarityTransform3D(pose=tfx.pose(R, t), scale=1.0, from_frame="object", to_frame="sim")
    #The other way was easier, but we actually need sim to object...
    sim_to_object = object_to_sim.inverse()

    t = np.array([0.0, 0.0, z_offset])
    R = np.eye(3)
    object_to_world = stf.SimilarityTransform3D(pose=tfx.pose(R, t), scale=1.0, from_frame="object", to_frame="world")

    grip_to_object = sim_to_object.dot(grip_to_sim)
    grip_to_world = object_to_world.dot(grip_to_object)
    
    return grip_to_world




if __name__ == '__main__':

    #ALL UNITS ARE IN METERS!
    #All of the projected objects are about the same height
    z_offset = 0.02755
    #All of the sim stuff is in pixels, which we need to convert to meters.
    #Ratio of meters/pixels
    pixels_to_meters = float(0.077)/float(65) 
    ctrl = DexController()

    argc = len(sys.argv)
    data_dir = sys.argv[1]
    for root, dirs, files in os.walk(data_dir):
        for f in files:
	    if f.endswith('.csv'):
                target_poses = []
		filename = os.path.join(root, f)
		csv_contents = csv.reader(open(filename))

		for row in csv_contents:
		    #A lot of the rows of the csv are headers that don't have actual data...
		    if (is_float(row[0])):
		        target = convert_frame(float(row[1]), float(row[2]), float(row[3]))
                        target_poses.append(target)

                
		if len(target_poses) != 0:
		    #Now that we've converted the poses from the csv, run experiemts!
		    print("")
		    print("Running experiments from following result file: ")
		    print(f)
		    print("")
		    for idx, target in enumerate(target_poses):
                        ctrl.reset()
			# prompt for object placement
                        print("")
		        yesno = raw_input('Place object for this file. Hit [ENTER] when done')
		        print("Running Pose " + str(idx + 1) + " of " + str(len(target_poses)))

		        #Actual control code
		        ctrl.do_grasp(target)
                
