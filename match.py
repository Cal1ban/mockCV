
# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2
import subprocess
import fileinput
import sys

def dataWriter(startX,startY,endX,endY):
		#solution for coords, is startY = top, startX = left, endX - startX = width, endY - startY = height
	top = str(startY)
	left = str(startX)
	width = str(endX - startX)
	height = str(endY - startY)

	with open ("/Users/georgeseed/hackathon/template.html", "r") as myfile:
	    data = myfile.read()

	f = open('/Users/georgeseed/hackathon/images/index.html','w')

	f.write(data)
	f.close()

	def replaceAll(file,searchExp,replaceExp):
	    for line in fileinput.input(file, inplace=1):
	        if searchExp in line:
	            line = line.replace(searchExp,replaceExp)
	        sys.stdout.write(line)

	replaceAll( "/Users/georgeseed/hackathon/images/index.html",
	"""position: relative;top: 420px;left: 326px;width: 722px;height: 463px;""",
	"""             position: relative;
	                top: """+top+"""px;
	                left: """+left+"""px;
	                width: """+width+"""px;
	                height: """+height+"""px;
	""")


subprocess.call(["phantomjs","--ssl-protocol=any","/Users/georgeseed/hackathon/imageBot.js"])

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--template", required=True, help="Path to template image")
ap.add_argument("-i", "--images", required=True, help="Path to images where template will be matched")
ap.add_argument("-v", "--visualize", help="Flag indicating whether or not to visualize each iteration")
args = vars(ap.parse_args())
print('1')
# load the image image, convert it to grayscale, and detect edges
template = cv2.imread(args["template"])
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
cv2.imshow("Template", template)
print('2')
# loop over the images to find the template in
for imagePath in glob.glob(args["images"] + "/*.jpg"):
	# load the image, convert it to grayscale, and initialize the
	# bookkeeping variable to keep track of the matched region
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	found = None
	print('3')

	# loop over the scales of the image
	for scale in np.linspace(0.2, 1.0, 20)[::-1]:
		# resize the image according to the scale, and keep track
		# of the ratio of the resizing
		resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
		r = gray.shape[1] / float(resized.shape[1])

		# if the resized image is smaller than the template, then break
		# from the loop
		if resized.shape[0] < tH or resized.shape[1] < tW:
			break

		# detect edges in the resized, grayscale image and apply template
		# matching to find the template in the image
		print('3')
		edged = cv2.Canny(resized, 50, 200)
		result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
		(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

		# check to see if the iteration should be visualized
		if args.get("visualize", False):
			# draw a bounding box around the detected region
			clone = np.dstack([edged, edged, edged])
			cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
			(maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
			cv2.imshow("Visualize", clone)
			cv2.waitKey(0)

		# if we have found a new maximum correlation value, then ipdate
		# the bookkeeping variable
		if found is None or maxVal > found[0]:
			found = (maxVal, maxLoc, r)

	# unpack the bookkeeping varaible and compute (x, y) coordinates
	print('4')
	(_, maxLoc, r) = found
	(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
	(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
	dataWriter(startX,startY,endX,endY)
