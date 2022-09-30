import json
import numpy as np
from pathlib import Path
from matplotlib import path as fig

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
	point2 = np.array([cell[0], cell[1] + cell[3]])
	point3 = np.array([cell[0] + cell[2], cell[1]])
	point4 = np.array([cell[0] + cell[2], cell[1] + cell[3]])

	new_point1 = In.projective_transform_point(point1, prj_matrix)
	new_point2 = In.projective_transform_point(point2, prj_matrix)
	new_point3 = In.projective_transform_point(point3, prj_matrix)
	new_point4 = In.projective_transform_point(point4, prj_matrix)
	
	return new_point1, new_point2, new_point3, new_point4

def founded(mar_res):
	obj = mar_res['plates']
	
	for i in range(0, len(obj)):
		rej = obj[i]['rejected']	
		if rej == False:
			return True
			
	return False
	
	
def read_marina_res(mar_res, signes_num, lp_x = 0, lp_y = 0):
	obj = mar_res['plates']
	lp_num = 0
	
	for i in range(0, len(obj)):
		rej = obj[i]['rejected']
		#print(x, y)
		if rej == False:										##to do check also position
			lp_num = i
			
	symbol_rectangles = np.zeros((4, signes_num), int)							#X, Y, x, y

	##if regected return -1 ?
	
	frame = obj[lp_num]["frame"]

	if "fields" in obj[lp_num]:
		obj = obj[lp_num]["fields"]['number']['cells']
	else: 
		return symbol_rectangles
		
	prj_matrix = proj_matrix(frame)
	
	for k in range(0, signes_num):
		points = points_transform(obj[k], prj_matrix)
		
		symbol_rectangles[1][k] = points[0][1]
		symbol_rectangles[0][k] = points[0][0]
		symbol_rectangles[3][k] = points[3][1] - points[0][1]
		symbol_rectangles[2][k] = points[3][0] - points[0][0]		

	return symbol_rectangles
	

def get_points(mar_res, signes_num):
	obj = mar_res['plates']
	lp_num = 0

	for i in range(0, len(obj)):
		rej = obj[i]['rejected']
		#print(x, y)
		if rej == False:				
			lp_num = i
			
	points = np.zeros((signes_num, 4, 2), int)

	##if regected return -1 ?
	
	frame = obj[lp_num]["frame"]

	if "fields" in obj[lp_num]:
		obj = obj[lp_num]["fields"]['number']['cells']
	else: 
		return points
		
	prj_matrix = proj_matrix(frame)
	
	for k in range(0, signes_num):
		point_4 = points_transform(obj[k], prj_matrix)
		for j  in range(0, 4):
			points[k][j] = point_4[j]		

	return points


def get_binary_matrix(points_4, y_img, x_img):
	
	matrix = np.zeros((y_img, x_img))
	p = fig.Path([points_4[0], points_4[1], points_4[3], points_4[2]])
	
	min_x = min(points_4[0][0], points_4[1][0], points_4[2][0], points_4[3][0])
	max_x = max(points_4[0][0], points_4[1][0], points_4[2][0], points_4[3][0])
	min_y = min(points_4[0][1], points_4[1][1], points_4[2][1], points_4[3][1])
	max_y = max(points_4[0][1], points_4[1][1], points_4[2][1], points_4[3][1])
	
	for i in range(min_x - 1, max_x + 1):
		for j in range(min_y - 1, max_y + 1):
 			if(p.contains_points([(i, j)])):
 				matrix[y_img - 1 - j][i] = 1
 				
	return matrix
 	
