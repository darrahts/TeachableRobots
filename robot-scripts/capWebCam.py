#cv2.cvtColor(yourImage, typeOfConversion) COLOR_BGR2GRAY COLOR_BGR2HSV 
import numpy as np
import cv2

boundaries = [
	(np.uint8([[[17, 15, 100]]]), np.uint8([[[50, 56, 200]]])),
	(np.uint8([[[86, 31, 4]]]), np.uint8([[[220, 88, 50]]])),
	([25, 146, 190], [62, 174, 250]),
	([103, 86, 65], [145, 133, 128])
]

red = boundaries[0]
blue = boundaries[1]

hsvRedLower = cv2.cvtColor(red[0], cv2.COLOR_BGR2HSV)
hsvRedUpper = cv2.cvtColor(red[1], cv2.COLOR_BGR2HSV)

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
        
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #cv2.imshow('frame, q to quit',hsvFrame)
    
    #grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('grayed frame, q to quit', grayFrame)
    #blurredFrame = cv2.GaussianBlur(grayFrame, (5, 5), 0)
	#blurredFrame = cv2.GaussianBlur(frame, (5, 5), 0)
	#cv2.imshow('blurred frame, q to quit', blurredFrame)
	
    #binaryFrame = cv2.threshold(frame, 60, 255, cv2.THRESH_BINARY)[1]
    #binaryFrame = cv2.threshold(hsvFrame, 60, 255, cv2.THRESH_BINARY)[1]
    #binaryFrame = cv2.threshold(grayFrame, 60, 255, cv2.THRESH_BINARY)[1]
    #cv2.imshow('binary frame, q to quit', binaryFrame)
    
    lowBlue = np.array([110, 50, 50])
    upBlue = np.array([130, 255, 255])
    
    #mask = cv2.inRange(frame, red[0], red[1])
    #mask = cv2.inRange(frame, blue[0], blue[1])
    
    #mask = cv2.inRange(hsvFrame, hsvRedLower, hsvRedUpper)
    mask = cv2.inRange(hsvFrame, lowBlue, upBlue)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    
    cv2.imshow('frame', frame)
    cv2.imshow('mask', mask)
    cv2.imshow('res', res)
    
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
    	break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()














