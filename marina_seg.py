import json
import numpy as np
from pathlib import Path

import sys
sys.path.append('../../svn/trunk/prj.scripts/test/geometry/projective')
import __init__ as In

def get_marina_res(dset, name, img_format, path):

	json_path = Path(path, name + img_format + ".json" )
	#print(json_path)
	
	if(json_path.exists() == False):
		print("can`t find json for", name, "from", dset)
		return -1
	
	with open(str(json_path)) as f:
			file_content = f.read()
			result = json.loads(file_content)
	
	return result
	

def proj_matrix(frame):
	height = 130		#take it from template !!!
	width = 400
	
	In.init("/home/ekatrina/prog/svn/trunk/build/lib.linux64.release")
	prj_matrix = In.calc_projective_matrix_from_rect_to_quad(frame, width, height)	
	return prj_matrix


def points_transform(cell, prj_matrix):
	point1 = np.array([cell[0], cell[1]])
	point4 = np.array([cell[0] + cell[2], cell[1] + cell[3]])

	new_point1 = In.projective_transform_point(point1, prj_matrix)
	new_point4 = In.projective_transform_point(point4, prj_matrix)
	
	return new_point1, new_point4

def founded(mar_res)
	obj = mar_res['plates']
	
	for i in range(0, len(obj)):
		rej = obj[i]['rejected']	
		if rej == False:
			return True
			
	return False
	
	
def read_marina_res(mar_res, signes_num, move_X, move_Y, lp_x = 0, lp_y = 0):
	obj = mar_res['plates']
	lp_num = 0
	x_pos_lp = 4000
	y_pos_lp = 4000
	
	for i in range(0, len(obj)):
		x = obj[i]['rect'][0]
		y = obj[i]['rect'][1]
		rej = obj[i]['rejected']
		#print(x, y)
		if rej == False:										##to do check also position
			lp_num = i
			x_pos_lp = abs(lp_x - move_X - x)
			y_pos_lp = abs(lp_y - move_Y - y)
			
	symbol_rectangles = np.zeros((4, signes_num), int)							#X, Y, x, y

	##if regected return -1 ?
	
	frame = obj[lp_num]["frame"]
	
	x = obj[lp_num]['rect'][0]
	y = obj[lp_num]['rect'][1]


	if "fields" in obj[lp_num]:
		obj = obj[lp_num]["fields"]['number']['cells']
	else: 
		return symbol_rectangles
		
	prj_matrix = proj_matrix(frame)
	
	for k in range(0, signes_num):
		point1, point4 = points_transform(obj[k], prj_matrix)
		
		symbol_rectangles[1][k] = point1[1] + move_Y
		symbol_rectangles[0][k] = point1[0] + move_X
		symbol_rectangles[3][k] = point4[1] - point1[1]
		symbol_rectangles[2][k] = point4[0] - point1[0]		

	return symbol_rectangles
	
