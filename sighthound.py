import copy
import http.client as httplib
import json
import os
import ssl
import numpy as np

HEADERS = {"Content-type": "application/json", "X-Access-Token": "yHxNQWht4qeyrR1THlWTbY8XKvCB9gnI5Tut"}
CONN = httplib.HTTPSConnection("dev.sighthoundapi.com", context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))

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

def get_bin_matrix(p, data, indx):
	y_img, x_img = data.get_img_size()	
	matrix = np.zeros((y_img, x_img))
	
	Y = p[0][indx][1]
	X = p[0][indx][0]
	y = p[2][indx][1] - p[0][indx][1]
	x = p[1][indx][0] - p[0][indx][0]
		
	for i in range(0, x):
		for j in range(0, y):
			matrix[y_img - 1 - Y + j][X + i] = 1	#may be error hear
		
	#print(matrix)
	return matrix
	
