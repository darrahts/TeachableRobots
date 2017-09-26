from VideoStream import *
import cv2

if __name__ == "__main__":
    # demo = Demo(0, 1000, True)
    # demo.StartRegular()
    # demo.StartThreaded()
    try:
        vs = WebcamVideoStream(0).start()
        while True:
            frame = vs.read()
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("c"):
                cv2.imwrite("testPic.png", frame)
                print("captured.")

    except:
        vs.close()
