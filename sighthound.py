import copy
import http.client as httplib
import json
import os
import ssl
import numpy as np
from pathlib import Path
import base64

HEADERS = {"Content-type": "application/json", "X-Access-Token": "yHxNQWht4qeyrR1THlWTbY8XKvCB9gnI5Tut"}
CONN = httplib.HTTPSConnection("dev.sighthoundapi.com", context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))

def sighthound(dset, dpath, name):

	res_path = Path('sightound_result_' + dset)
	
	if(res_path.exists() == False):
		res_path.mkdir()
		
	res_path = Path(res_path, name + '.json')
	
	if(res_path.exists() == False):
		image_data = base64.b64encode(open(Path(dpath, name + ".png"), "rb").read()).decode()

		params = json.dumps({"image": image_data})
		CONN.request("POST", "/v1/recognition?objectType=licenseplate", params, HEADERS)
		response = CONN.getresponse()
		result = response.read()
		result1 = json.loads(result)
		#print(result1)
		result = str(result)
		
		
		with open(str(res_path), 'w') as f:
			json.dump(result, f)
			
	else:
		
		with open(str(res_path)) as f:
			file_content = f.read()
			result = json.loads(file_content)
		
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
	
def get_number_of_signs(sight_res):
	indx = sight_res.rfind("index")

	if(indx == -1):
		return 0
	
	indx = indx + 7
	res = int(sight_res[indx]) + 1
	#print('signs stated =', res)
	return res
	
def get_lp_signs(sight_res):
	indx1 = sight_res.find("name")
	indx1 = indx1 + 7
	
	indx2 = sight_res.find("confidence", indx1)
	indx2 = indx2 - 3
	
	if(indx1 == 6):
		lp = "not stated"
	else:
		lp = sight_res[indx1:indx2]
	#print('founded number =', lp)
	return lp		

def read_sigh_res(sight_res, signes_num):				#signes_num = 7 for brazil
	res_num = get_number_of_signs(sight_res)
	
	p = np.zeros((3, 2), int)					#4 points, 7 signes, 2 - x and y
	rect = np.zeros((4, signes_num), int)				#X, Y, x, y
	
	if(signes_num != res_num):
		return rect

	
	i = sight_res.rfind("characters")
	strlen = len(sight_res)

	
	
	for k in range(0, res_num):
		i = sight_res.find("vertices", i)
		p[0][0], p[0][1], i = find_point_in_res(i, sight_res, strlen)
		p[1][0], p[1][1], i = find_point_in_res(i, sight_res, strlen)
		p[2][0], p[2][1], i = find_point_in_res(i, sight_res, strlen)
		#p[3][k][0], p[3][k][1], i = find_point_in_res(i, sight_res, strlen)
		
		rect[1][k] = p[0][1]
		rect[0][k] = p[0][0]
		rect[3][k] = p[2][1] - p[0][1]
		rect[2][k] = p[1][0] - p[0][0]		

	return rect


def get_bin_matrix(sq, data, indx):
	y_img, x_img = data.get_img_size()	
	matrix = np.zeros((y_img, x_img))
	
	X = sq[0][indx]
	Y = sq[1][indx]
	x = sq[2][indx]
	y = sq[3][indx]
		
	for i in range(0, x + 1):
		for j in range(0, y + 1):
			matrix[y_img - 1 - Y + j][X + i] = 1	#may be error here
		
	#print(matrix)
	return matrix
	
