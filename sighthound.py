import copy
import http.client as httplib
import json
import os
import ssl
import numpy as np
from pathlib import Path
import base64
from matplotlib import path as fig
import dataset_class as Dat
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
HEADERS = {"Content-type": "application/json", "X-Access-Token": "HmR8TJhLukXa1oAoxODcjAhW3UJYwijqrFx8"}
CONN = httplib.HTTPSConnection("dev.sighthoundapi.com", context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def sighthound(dset, dpath, name, img_format, data, cut):

	res_path = Path('sighthound_answ_' + dset)
	
	if(res_path.exists() == False):
		res_path.mkdir()
		
	res_path = Path(res_path, name + '.json')
	
	if(res_path.exists() == False):
		
		if(type(data) == int):
			image_data = base64.b64encode(open(Path(dpath, name + img_format), "rb").read()).decode()
		else:
			image_data, lp_X, lp_Y = data.cut_img(cut)

		params = json.dumps({"image": image_data})
		CONN.request("POST", "/v1/recognition?objectType=licenseplate", params, HEADERS)
		response = CONN.getresponse()
		result = response.read()
		result = json.loads(result)
		#obj = (result['objects'])[0]['licenseplateAnnotation']['attributes']['system']['characters'][0]['bounding']['vertices'][0]
		#print(obj)	
		
		with open(str(res_path), 'w') as f:
			json.dump(result, f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=2)
			
	else:
		
		with open(str(res_path)) as f:
			file_content = f.read()
			result = json.loads(file_content)
			
			
	if 'error' in result:
	
			print(name, "have an error:", result['error'])
	
			if result['error'] == "ERROR_OVER_THROTTLE":
				#print(result)
				os.remove(res_path)
				return sighthound(dset, dpath, name, img_format, image_data, cut)
				
			if result['error'] == "ERROR_USAGE":
				os.remove(res_path)
				return sighthound(dset, dpath, name, img_format, image_data, cut)
			
			return -1
		
	return result
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------	
def get_number_of_signs(sight_res):
	indx = sight_res.rfind("index")

	if(indx == -1):
		return 0

	indx = indx + 8
	res = int(sight_res[indx]) + 1
	#print('signs stated =', res)
	return res
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------	
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
#------------------------------------------------------------------------------------------------------------------------
#signes_num = 7 for brazil
#------------------------------------------------------------------------------------------------------------------------
def read_sigh_res(sight_res, signes_num, move_X, move_Y, lp_x = 0, lp_y = 0):					

	obj = sight_res['objects']
	lp_num = 0
	res_num = 0
	x_pos_lp = int(sight_res['image']['width'])
	y_pos_lp = int(sight_res['image']['height'])

	for i in range(0, len(obj)):
		num = get_number_of_signs(str(obj[i]))
		x = obj[i]['licenseplateAnnotation']['bounding']['vertices'][0]['x']
		y = obj[i]['licenseplateAnnotation']['bounding']['vertices'][0]['y']
		#print(x, y)
		if num == signes_num and abs(lp_x - x) < x_pos_lp and abs(lp_y - y) < y_pos_lp:
			lp_num = i
			res_num = num
			x_pos_lp = abs(lp_x - move_X - x)
			y_pos_lp = abs(lp_y - move_Y - y)
			
	symbol_rectangles = np.zeros((4, signes_num), int)							#X, Y, x, y

	if(signes_num != res_num):
		return symbol_rectangles

	obj = obj[lp_num]['licenseplateAnnotation']['attributes']['system']['characters']			#[0]['bounding']['vertices'][0]

	for k in range(0, signes_num):
		symbol_rectangles[1][k] = obj[k]['bounding']['vertices'][0]['y'] + move_Y
		symbol_rectangles[0][k] = obj[k]['bounding']['vertices'][0]['x'] + move_X
		symbol_rectangles[3][k] = obj[k]['bounding']['vertices'][2]['y'] - obj[k]['bounding']['vertices'][0]['y']
		symbol_rectangles[2][k] = obj[k]['bounding']['vertices'][1]['x'] - obj[k]['bounding']['vertices'][0]['x']		

	return symbol_rectangles
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def get_bin_matrix(rect, data, indx, cut = 0):
	if(cut != 0):
		move_x, move_y, no, nop = data.data.get_lp_position(cut)
	else:
		move_x = 0
		move_y = 0
		
	

	y_img, x_img = data.get_img_size()	
	matrix = np.zeros((y_img, x_img))
	
	X = rect[0][indx] + move_x
	Y = rect[1][indx] + move_y
	x = rect[2][indx]
	y = rect[3][indx]
		
	for i in range(0, x):
		for j in range(0, y):
			matrix[y_img - 1 - Y - j][X + i] = 1	#may be error here
		
	#print(matrix)
	return matrix
##------------------------------------------------------------------------------------------------------------------------
def get_bin_matrixx(rect, data, indx):
	y_img, x_img = data.get_img_size()
	
	points_4 =  np.zeros((4, 2), int)
	
	points_4[0][0] = rect[0][indx]
	points_4[0][1] = rect[1][indx]
	
	points_4[1][0] = rect[0][indx] + rect[2][indx] - 1
	points_4[1][1] = rect[1][indx]
	
	points_4[2][0] = rect[0][indx]
	points_4[2][1] = rect[1][indx] + rect[3][indx] - 1
	
	points_4[3][0] = rect[0][indx] + rect[2][indx] - 1
	points_4[3][1] = rect[1][indx] + rect[3][indx] - 1
	
	matrix = np.zeros((y_img, x_img))
	p = fig.Path([points_4[0], points_4[1], points_4[3], points_4[2], points_4[0]])
	
	#print([points_4[0], points_4[1], points_4[3], points_4[2], points_4[0]])
	
	#print(p)
	
	min_x = min(points_4[0][0], points_4[1][0], points_4[2][0], points_4[3][0])
	max_x = max(points_4[0][0], points_4[1][0], points_4[2][0], points_4[3][0])
	min_y = min(points_4[0][1], points_4[1][1], points_4[2][1], points_4[3][1])
	max_y = max(points_4[0][1], points_4[1][1], points_4[2][1], points_4[3][1])
	
	for i in range(min_x, max_x + 1):
		for j in range(min_y, max_y + 1):
			point = np.array([i, j])
			
			if(p.contains_point([i, j]) or np.array_equal(point, points_4[0]) or np.array_equal(point, points_4[1]) or np.array_equal(point, points_4[2]) or np.array_equal(point, points_4[3])):
				matrix[y_img - 1 - j][i] = 1
	
				
	return matrix
