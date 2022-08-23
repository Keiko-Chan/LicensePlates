import json
from openalpr import Alpr
from pathlib import Path
import subprocess
import numpy as np
import base64
import os
import cv2 as cv

#PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track23' )
#results = alpr.recognize_file(str(Path(PATH_TO_DATA1, "Track23[03].png")))

def save_openalpr_res(path, name, img_format, image_data):
	#print(str(Path(path, img_name)))
	
	res_path = Path('openalpr_res')
	
	if(res_path.exists() == False):
		res_path.mkdir()
	
	if(type(image_data) == int):
		res_path = Path(res_path, name + '.json')
	
		if(res_path.exists() == False):
			subprocess.run(["alpr" , '-c' , 'br', str(Path(path, (name + img_format)))])
	
	else:
		res_path = Path(res_path, name + '_lp' + '.json')
		
		if(res_path.exists() == False):
			im_bytes = base64.b64decode(image_data)
			im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
			img = cv.imdecode(im_arr, flags=cv.IMREAD_COLOR)
			
			img_path = str(Path('openalpr_res', name + '_lp' + img_format))
			cv.imwrite(img_path, cv.cvtColor(img, cv.COLOR_RGB2BGR)) 
			
			#cv.imshow("written", img)
			#cv.waitKey(0)
			
			subprocess.run(["alpr", '-c' , 'br', img_path])
			
			try: 
    				os.remove(img_path)
			except: pass
		
	with open(str(res_path)) as f:
		file_content = f.read()
		result = json.loads(file_content)
		
			
	if 'error' in result:			
		return 0
			
	return result
	
def read_openalpr_res(openalpr_res, signes_count):

	characters = openalpr_res['characters']
	
	points = np.zeros((4, signes_count, 2), int)			#4 points, 7 signes, 2 - x and y
	
	if(len(characters) != signes_count):
		return points
	
	for k in range(0, signes_count):
		for i in range(0, 4):
			points[i][k][0] = characters[k]['points'][i]['x']
			points[i][k][1] = characters[k]['points'][i]['y']
		
		#print(p[2][k][0], p[2][k][1])
	return points
	
def points_to_rectangle(points, signes_count, move_X, move_Y):
	symbol_rectangles = np.zeros((4, signes_count), int)
	
	if(points[0][0][1] == 0 and points[0][0][0] == 0 and points[0][1][1] == 0 and points[0][1][0] == 0):
		return symbol_rectangles
	
	for k in range(0, signes_count):
		symbol_rectangles[1][k] = points[0][k][1] + move_Y
		symbol_rectangles[0][k] = points[0][k][0] + move_X
		symbol_rectangles[3][k] = points[2][k][1] - points[0][k][1]
		symbol_rectangles[2][k] = points[1][k][0] - points[0][k][0]
		
	return symbol_rectangles
	
def get_bin_matrix(points, data, indx):
	y_img, x_img = data.get_img_size()	
	matrix = np.zeros((y_img, x_img))
	
	min_y = min(points[0][indx][1], points[1][indx][1], points[2][indx][1], points[3][indx][1])
	min_x = min(points[0][indx][0], points[1][indx][0], points[2][indx][0], points[3][indx][0])
	max_y = max(points[0][indx][1], points[1][indx][1], points[2][indx][1], points[3][indx][1])
	max_x = max(points[0][indx][0], points[1][indx][0], points[2][indx][0], points[3][indx][0])
		
	for i in range(min_x, max_x):
		for j in range(min_y, max_y):
			matrix[y_ing - 1 -j][i] = 1	#may be error here
		
	#print(matrix)
	return matrix
