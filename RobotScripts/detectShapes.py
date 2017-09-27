from ShapeDetector import ShapeDetector
import argparse
import imutils
import cv2

#ArgParse provides command line interface to the script 
#https://docs.python.org/dev/library/argparse.html (super cool)
#So type python3 shapeCenter.py -i PATH_TO_IMAGE_GOES_HERE 
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image", required=True, help="Path to the input image")
args = vars(parser.parse_args())

#read the image 
image = cv2.imread(args["image"])
rImage = cv2.imread(args["image"])
ratio = image.shape[0] / float(image.shape[0])

#Preprocess the image
grayedImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurredImage = cv2.GaussianBlur(grayedImage, (5, 5), 0)
binImage = cv2.threshold(blurredImage, 60, 255, cv2.THRESH_BINARY)[1]

#Create a shape detector
#shapeDetector = ShapeDetector()

#returns a set of contours on the shapes.  Always use both lines
contours = cv2.findContours(binImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if imutils.is_cv2() else contours[1]

for c in contours:
	#Compute the center of each contour.
	#moments characterize the shape of an image like area, centroid,
	#orientation, other statistical properties.  Here we can see
	#the indicies of the array are string keys
	print(len(c))
	moments = cv2.moments(c)
	cX = int(moments["m10"] / (moments["m00"] * ratio)) if moments["m00"] != 0 else 0
	cY = int(moments["m01"] / (moments["m00"] * ratio)) if moments["m00"] != 0 else 0
	perimeter = cv2.arcLength(contour, True)
	shapeVertices = cv2.approxPolyDP(contour, .04*perimeter, True)
    if len(shapeVertices) == 4: #square or rectangle
        (x, y, w, h) = cv2.boundingRect(shapeVertices)
        aspectRatio = w / float(h) 
        shape = "square" if aspectRatio >= .95 and aspectRatio <= 1.05 else "rectangle"		
	
	#Resize the contours to the original image size
	c = c.astype("float")
	c *= ratio
	c = c.astype("int")
	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
	cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
	
cv2.imshow("Processed Image", image)
cv2.waitKey(0)





