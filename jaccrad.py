import cv2 as cv
import numpy as np
from pathlib import Path
import base64
import json
import os
import ssl
import copy
import http.client as httplib 
import dataset_class as dat
from sklearn.metrics import jaccard_score

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track01' )
HEADERS = {"Content-type": "application/json", "X-Access-Token": "yHxNQWht4qeyrR1THlWTbY8XKvCB9gnI5Tut"}
CONN = httplib.HTTPSConnection("dev.sighthoundapi.com", context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))

#input = np.array([1,0,0,1,1,1]) for exaple
def jaccard(pred, true):
	similarity = jaccard_score(pred, true)
	distance = jaccard(pred, true)
	return similarity, distance
	
def sighthound(image_data):
	params = json.dumps({"image": image_data})
	CONN.request("POST", "/v1/recognition?objectType=licenseplate", params, HEADERS)
	response = CONN.getresponse()
	result = response.read()
	return result
	
def find_point_in_res(start, sight_res, strlen):
	i = copy.copy(start)
	px = 0
	py = 0
	st = ''
	indx = 0
	
	for j in sight_res[start:strlen]:
		if j.isdigit():
			st = st + j
			indx = 1
		else:
			if indx == 1:
				if py == 0:
					indx = 0
					py = int(st)
					
					st = ''
				else:
					px = int(st)
					i = i + 1
					break
		i = i + 1
	#print(i)
					
	return px, py, i

def sigh_res_SSIG(sight_res):
	p = np.zeros((4, 7, 2), int)			#4 points, 7 signes, 2 - x and y
	i = sight_res.rfind("characters")
	strlen = len(sight_res)

	
	for k in range(0, 7):
		i = sight_res.find("vertices", i)
		p[0][k][0], p[0][k][1], i = find_point_in_res(i, sight_res, strlen)
		p[1][k][0], p[1][k][1], i = find_point_in_res(i, sight_res, strlen)
		p[2][k][0], p[2][k][1], i = find_point_in_res(i, sight_res, strlen)
		p[3][k][0], p[3][k][1], i = find_point_in_res(i, sight_res, strlen)
		#print(p[2][k][0], p[2][k][1])
	return p
	
def main():
	print('I am work')
	image_data = base64.b64encode(open(Path(PATH_TO_DATA1, 'Track1[01].png'), "rb").read()).decode()
	result = str(sighthound(image_data))
	print("Detection Results = " + result )
	
	data = dat.Dataset('Track1[01].txt', 'Track1[01].png', PATH_TO_DATA1)
	data.read_txt_SSIG()
	data.get_bin_matrix(1)
	
	points = sigh_res_SSIG(result)

if __name__ == "__main__":
	main()
	
