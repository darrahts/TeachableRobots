import numpy as np
import argparse
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image", help = "path to image file")
args = vars(parser.parse_args())

image = cv2.imread(args["image"])

#define upper and lower points in the BGR (not RGB, openCV stores with BGR)
lower = np.array([0, 0, 0]) #pure black
upper = np.array([15, 15, 15]) #mostly black in varying shades

#This will black out everything outside of this range
maskedImage = cv2.inRange(image, lower, upper)
#binImage = cv2.threshold(maskedImage, 60, 255, cv2.THRESH_BINARY)[1]

contours = cv2.findContours(maskedImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cv2.imshow("Black Shapes", maskedImage)

for c in contours:					#green
	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)

cv2.imshow("Found Shapes", image)
cv2.waitKey(0)
