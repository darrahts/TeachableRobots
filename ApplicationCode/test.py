from VideoStream import *



if __name__ == "__main__":
#    demo = Demo(0, 1000, True)
    #demo.StartRegular()
#    demo.StartThreaded()

	vs = WebcamVideoStream(0).start()
	while True:
		frame = vs.read()
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
