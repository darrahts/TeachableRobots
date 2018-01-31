import argparse
import imutils
import cv2

#ArgParse provides command line interface to the script 
#https://docs.python.org/dev/library/argparse.html (super cool)
#So type python3 shapeCenter.py -i PATH_TO_IMAGE_GOES_HERE 
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image", required=True, help="Path to the input image")
args = vars(parser.parse_args())

#Process the image.  First to gayscale, then blurr the image, then 
#apply a threshold to binarize the image
#the first line reads the value passed to the -i or --image argument 
cImage = cv2.imread(args["image"]) 
rImage = cv2.imread(args["image"])
grayedImage = cv2.cvtColor(cImage, cv2.COLOR_BGR2GRAY)
blurredImage = cv2.GaussianBlur(grayedImage, (5, 5), 0) #5x5 kernel
binImage = cv2.threshold(blurredImage, 60, 255, cv2.THRESH_BINARY)[1]

#returns a set of contours on the shapes.  Always use both lines
contours = cv2.findContours(binImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if imutils.is_cv2() else contours[1]

#used below to apply the contours to the image


#Uncomment this and see what the set of contours looks like
#for x in contours: 
#	print(x)


for c in contours:
	#Compute the center of each contour.
	#moments characterize the shape of an image like area, centroid,
	#orientation, other statistical properties.  Here we can see
	#the indicies of the array are string keys
	moments = cv2.moments(c)
	cX = int(moments["m10"] / (moments["m00"] + 1))
	cY = int(moments["m01"] / (moments["m00"] + 1))

	#Draw the contour and center of the shape on the image
	cv2.drawContours(cImage, [c], -1, (0, 255, 0), 2)
	cv2.circle(cImage, (cX, cY), 7, (255, 255, 255), -1)
	cv2.putText(cImage, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
	#cv2.imshow("Processed Image", cImage)
	#cv2.waitKey(0)
#Display the images with the first one shown to the user called last
cv2.imshow("ProcessedImage", cImage)
cv2.imshow("Binary Image", binImage)
cv2.imshow("Blurred Image", blurredImage)
cv2.imshow("Gray Image", grayedImage)
cv2.imshow("Raw Image", rImage)
cv2.waitKey(0)
cv2.destroyAllWindows()
