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
		result = json.loads(result)
		#obj = (result['objects'])[0]['licenseplateAnnotation']['attributes']['system']['characters'][0]['bounding']['vertices'][0]
		#print(obj)	
		
		with open(str(res_path), 'w') as f:
			json.dump(result, f)
			
	else:
		
		with open(str(res_path)) as f:
			file_content = f.read()
			result = json.loads(file_content)
			
	if 'error' in result:
			if result['error'] == "ERROR_OVER_THROTTLE":
				os.remove(res_path)
				result = sighthound(dset, dpath, name)
				
			else:
				print(name, "have an error:", result['error'])
				return -1
		
	return result
	
def get_number_of_signs(sight_res):
	indx = sight_res.rfind("index")

	if(indx == -1):
		return 0

	indx = indx + 8
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

	obj = sight_res['objects']
	lp_num = 0
	res_num = 0

	for i in range(0, len(obj)):
		res_num = get_number_of_signs(str(obj[i]))
		if res_num == signes_num:
			lp_num = i

	rect = np.zeros((4, signes_num), int)				#X, Y, x, y
	
	if(signes_num != res_num):
		return rect

	obj = obj[lp_num]['licenseplateAnnotation']['attributes']['system']['characters']			#[0]['bounding']['vertices'][0]

	for k in range(0, signes_num):
		rect[1][k] = obj[k]['bounding']['vertices'][0]['y']
		rect[0][k] = obj[k]['bounding']['vertices'][0]['x']
		rect[3][k] = obj[k]['bounding']['vertices'][2]['y'] - obj[k]['bounding']['vertices'][0]['y']
		rect[2][k] = obj[k]['bounding']['vertices'][1]['x'] - obj[k]['bounding']['vertices'][0]['x']		

	return rect


def get_bin_matrix(sq, data, indx):
	y_img, x_img = data.get_img_size()	
	matrix = np.zeros((y_img, x_img))
	
	X = sq[0][indx]
	Y = sq[1][indx]
	x = sq[2][indx]
	y = sq[3][indx]
		
	for i in range(0, x):
		for j in range(0, y):
			matrix[y_img - 1 - Y + j][X + i] = 1	#may be error here
		
	#print(matrix)
	return matrix
	
