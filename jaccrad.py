import cv2 as cv
import numpy as np
from pathlib import Path
import base64
import json
import os
import ssl
import http.client as httplib 
import dataset_class as dat
from sklearn.metrics import jaccard_score

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track01' )
HEADERS = {"Content-type": "application/json", "X-Access-Token": "yHxNQWht4qeyrR1THlWTbY8XKvCB9gnI5Tut"}
CONN = httplib.HTTPSConnection("dev.sighthoundapi.com", context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))

class Point:
	x = 0
	y = 0

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
	
#def find_point_in_res(start, sight_res)

def sigh_res_SSIG(sight_res):
	p1 = np.array(7, Point)
	p2 = np.array(7, Point)
	p3 = np.array(7, Point)
	p4 = np.array(7, Point)
	
	i = sight_res.rfind("characters")
	print(i)
	
def main():
	print('I am work')
	image_data = base64.b64encode(open(Path(PATH_TO_DATA1, 'Track1[01].png'), "rb").read()).decode()
	result = str(sighthound(image_data))
	print("Detection Results = " + result )
	
	data = dat.Dataset('Track1[01].txt', 'Track1[01].png', PATH_TO_DATA1)
	data.read_txt_SSIG()
	data.get_bin_matrix(1)
	
	sigh_res_SSIG(result)

if __name__ == "__main__":
	main()
	
