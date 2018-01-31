import numpy as np
import argparse
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image", help = "path to image")
args = vars(parser.parse_args())

image = cv2.imread(args["image"])

#Color boundaries in BGR format red, blue, yellow, gray. Add more in the future.
#Notice how this is an array of tuples of arrays lol that just sounds funny
colorBoundaries = [([17, 15, 100], [50, 56, 200]), ([86, 31, 4], [220, 88, 50]), ([25, 146, 190], [62, 174, 250]), ([103, 86, 65], [145, 133, 128])]


for (lower, upper) in colorBoundaries:
	lower = np.array(lower, dtype="uint8")
	upper = np.array(upper, dtype="uint8")
	
	#this image filters out any pixel outside of the lower/upper range of color
	maskedImage = cv2.inRange(image, lower, upper)
	
	#this image results from the pixel comparison of the original image
	#and the mask.  It returns like pixels
	output = cv2.bitwise_and(image, image, mask=maskedImage)
	
	cv2.imshow("images", np.hstack([image, output]))
	cv2.waitKey(0)
