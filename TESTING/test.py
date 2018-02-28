from VideoStream import *
import cv2
import imutils
import numpy as np

def showPixelValue(event,x,y,flags,param):
    global frame, combinedResult, placeholder
    
    if event == cv2.EVENT_MOUSEMOVE:
        # get the value of pixel from the location of mouse in (x,y)
        bgr = frame[y,x]

        # Convert the BGR pixel into other colro formats
        ycb = cv2.cvtColor(np.uint8([[bgr]]),cv2.COLOR_BGR2YCrCb)[0][0]
        lab = cv2.cvtColor(np.uint8([[bgr]]),cv2.COLOR_BGR2Lab)[0][0]
        hsv = cv2.cvtColor(np.uint8([[bgr]]),cv2.COLOR_BGR2HSV)[0][0]
        
        # Create an empty placeholder for displaying the values
        placeholder = np.zeros((frame.shape[0],400,3),dtype=np.uint8)

        # fill the placeholder with the values of color spaces
        cv2.putText(placeholder, "BGR {}".format(bgr), (20, 70), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(placeholder, "HSV {}".format(hsv), (20, 140), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(placeholder, "YCrCb {}".format(ycb), (20, 210), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(placeholder, "LAB {}".format(lab), (20, 280), cv2.FONT_HERSHEY_COMPLEX, .9, (255,255,255), 1, cv2.LINE_AA)
        
        # Combine the two results to show side by side in a single image
        combinedResult = np.hstack([frame,placeholder])
        
        cv2.imshow("Frame",combinedResult)


def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def FindSquares(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    for gray in cv2.split(img):
        for thrs in range(0, 255, 26):
            if thrs == 0:
                bin1 = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin1 = cv2.dilate(bin1, None)
            else:
                _retval, bin1 = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            bin1, contours, _hierarchy = cv2.findContours(bin1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 186000 and cv2.contourArea(cnt) < 188000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in range(4)])
                    if max_cos < 0.1:
                        print(type(cnt))
                        return cnt


if __name__ == "__main__":
    # demo = Demo(0, 1000, True)
    # demo.StartRegular()
    # demo.StartThreaded()
    lowGreen = (116, 134,73)
    highGreen = (158, 179, 120)
    #lowGreen = (70, 130, 77)
    #highGreen = (145, 170, 122)
    lowGreen = (75, 128, 75)
    highGreen = (157, 166, 117)



    lowBlue = (98, 100, 70)
    highBlue = (115, 240, 150)
    
    cv2.namedWindow("Frame")
    #cv2.setMouseCallback("Frame",showPixelValue)
    try:
        vs = WebcamVideoStream(0).start()
        avgAreas = 0
        feeds = 0
        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=640, height=480)     
            (fX, fY) = ((frame.shape[1] // 2) + 24, (frame.shape[0] // 2) + 12)
       

            #square = FindSquares(frame)
            square = np.ndarray([4,2], dtype=int)
            square[0] = [125, 32]
            square[1] = [136, 459]
            square[2] = [550, 455]
            square[3] = [555, 37]
           
            

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            green = cv2.inRange(frame, lowGreen, highGreen)
            erode = cv2.erode(green, None, iterations=2)
            dialate = cv2.dilate(erode, None, iterations=2)
            #blue = cv2.inRange(frame1, lowBlue, highBlue)
            frame3 = frame #cv2.bitwise_and(frame,frame,mask=green)
            contours = cv2.findContours(dialate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            if(len(contours) > 0):
                cont = max(contours, key=cv2.contourArea)
                print(cont.shape)
                M = cv2.moments(cont)
                #print(type(cont))                
                (cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                x,y,w,h = cv2.boundingRect(cont)
                
                rect = cv2.minAreaRect(cont)
                box = cv2.boxPoints(rect)
                box = np.int0(box)                
                #cv2.rectangle(frame3,(x,y),(x+w,y+h),(0,255,0),1)
                #rect = cv2.minAreaRect(cont)
                #box = cv2.boxPoints(rect)
                #((x, y), radius) = cv2.minEnclosingCircle(cont)
                if(cv2.contourArea(cont) > 100):
                    ellipse = cv2.fitEllipse(cont)
                #print(len(ellipse))
                    cv2.ellipse(frame3, ellipse, (0,255,0), 2)
                #cv2.circle(frame3, (cX,cY), 2, (0,0,255), 2)
                #cv2.drawContours(frame3, [box], 0, (0,0,255), 2)
                (rX,rY) = (x - fX), (fY -y)
                #cv2.putText(frame3, str((rX//10,rY//10)), (x,y+30), cv2.FONT_HERSHEY_SIMPLEX, .45, (0,255,0), 2)
            cv2.putText(frame3, str((fX,fY)), (fX,fY+30), cv2.FONT_HERSHEY_SIMPLEX, .45, (0,255,0), 2)
      
            cv2.drawContours(frame3, [square], -1, (0, 255, 0), 2)
            #cv2.circle(frame, (cX, cY), 15, (0,255,0), 2)
            cv2.circle(frame3, (fX, fY), 15, (0,255,255), 2)
            cv2.circle(frame, (125, 32), 2, (0,255,0), 2)
            cv2.circle(frame, (136, 459), 2, (0,255,0), 2)
            cv2.circle(frame, (550, 455), 2, (0,255,0), 2)
            cv2.circle(frame, (555, 37), 2, (0,255,0), 2)
            cv2.imshow("Frame",frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                finished = True
                break
            elif key == ord("c"):
                cv2.imwrite("/home/tdarrah/Documents/TeachableRobots/ApplicationCode/test.jpg", frame)
                print("captured.")

    except KeyboardInterrupt:
        pass
















