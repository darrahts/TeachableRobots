import cv2

class ShapeDetector:
	def __init__(self):
		pass
		
	
	def detect(self, contour):
		shape = "unidentified"
		perimeter = cv2.arcLength(contour, True)
		shapeVertices = cv2.approxPolyDP(contour, .04*perimeter, True)
		
		if len(shapeVertices) < 3:
			shape = "NaS"
		
		elif len(shapeVertices) == 3:
			shape = "triangle"
			
		elif len(shapeVertices) == 4: #square or rectangle
			(x, y, w, h) = cv2.boundingRect(shapeVertices)
			aspectRatio = w / float(h) 
			shape = "square" if aspectRatio >= .95 and aspectRatio <= 1.05 else "rectangle"
			
		elif len(shapeVertices) == 5:
			shape = "pentagon"
		
		elif len(shapeVertices) == 6:
			shape = "septagon"
			
		else:
			shape = "circle"
			
		return shape
