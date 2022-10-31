import json
import numpy as np
from pathlib import Path
from matplotlib import path as fig

import sys
sys.path.append('../../svn/trunk/prj.scripts/test/geometry/projective')
import __init__ as In
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
CPP_PROJ_LIB_PATH = "/home/ekatrina/prog/svn/trunk/build/lib.linux64.release"
TEMPLATE_PATH = "/home/ekatrina/prog/svn/trunk/data/templates/brazilian"
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def proj_matrix(frame, moto):

	if(moto == "motorcycle"):
		template_path = Path(TEMPLATE_PATH, "brazilian_moto.json")
	else:
		template_path = Path(TEMPLATE_PATH, "brazilian.json")
		
	with open(str(template_path)) as f:
			file_content = f.read()
			template = json.loads(file_content)

	#height = 130		#take it from template !!!
	#width = 400
	
	height = int(template["size"][1])
	width = int(template["size"][0])
	
	In.init(CPP_PROJ_LIB_PATH)
	prj_matrix = In.calc_projective_matrix_from_rect_to_quad(frame, width, height)	
	return prj_matrix
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def transform(points_4, prj_matrix):
	new_points_4 = np.zeros((4, 2))
	
	for i in range(0, 4):
		new_points_4[i] = In.projective_transform_point(points_4[i], prj_matrix)
		
	#print(new_points_4)
	
	return new_points_4
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def to_points_transform(cell, prj_matrix):
	points_4 = np.zeros((4, 2))
	
	points_4[0] = np.array([cell[0], cell[1]])
	points_4[1] = np.array([cell[0], cell[1] + cell[3]])
	points_4[2] = np.array([cell[0] + cell[2], cell[1]])
	points_4[3] = np.array([cell[0] + cell[2], cell[1] + cell[3]])

	new_points_4 = transform(points_4, prj_matrix)
	
	return new_points_4	
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def new_proj_matrix(frame, prj_matrix, height, width):
	In.init(CPP_PROJ_LIB_PATH)
	new_prj_matrix = In.calc_projective_matrix_from_quad_to_rect(frame, width, height)	
	
	return new_prj_matrix	
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def founded(mar_res):
	obj = mar_res['plates']
	
	for i in range(0, len(obj)):
		rej = obj[i]['rejected']	
		if rej == False:
			return True
			
	return False
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------	
def read_marina_res(mar_res, signes_num, moto, lp_widht, lp_height, lp_x = 0, lp_y = 0):
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
		
	prj_matrix = proj_matrix(frame, moto)
	new_prj_matrix = new_proj_matrix(frame, prj_matrix, lp_height, lp_widht)
	
	for k in range(0, signes_num):
		points = to_points_transform(obj[k], prj_matrix)
		points = transform(points, new_prj_matrix)
		
		symbol_rectangles[1][k] = points[0][1] + lp_y
		symbol_rectangles[0][k] = points[0][0] + lp_x
		symbol_rectangles[3][k] = points[3][1] - points[0][1]
		symbol_rectangles[2][k] = points[3][0] - points[0][0]		

	print(symbol_rectangles)

	return symbol_rectangles
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def get_points(mar_res, signes_num, moto):
	obj = mar_res['plates']
	lp_num = 0

	for i in range(0, len(obj)):
		rej = obj[i]['rejected']
		#print(x, y)
		if rej == False:				
			lp_num = i
			
	points = np.zeros((signes_num, 4, 2), int)
	
	if(obj[lp_num]['rejected'] == True):
		print("rejected")
		return points

	##if regected return -1 ?
	
	frame = obj[lp_num]["frame"]

	if "fields" in obj[lp_num]:
		obj = obj[lp_num]["fields"]['number']['cells']
	else: 
		return points
		
	prj_matrix = proj_matrix(frame, moto)
	
	for k in range(0, signes_num):
		point_4 = to_points_transform(obj[k], prj_matrix)
		for j  in range(0, 4):
			points[k][j] = point_4[j]		

	return points
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def get_binary_matrix(points_4, y_img, x_img):
	
	matrix = np.zeros((y_img, x_img))
	p = fig.Path([points_4[0], points_4[1], points_4[3], points_4[2]])
	
	#print(p)
	
	min_x = min(points_4[0][0], points_4[1][0], points_4[2][0], points_4[3][0])
	max_x = max(points_4[0][0], points_4[1][0], points_4[2][0], points_4[3][0])
	min_y = min(points_4[0][1], points_4[1][1], points_4[2][1], points_4[3][1])
	max_y = max(points_4[0][1], points_4[1][1], points_4[2][1], points_4[3][1])
	
	for i in range(min_x - 1, max_x + 1):
		for j in range(min_y - 1, max_y + 1):
			point = np.array([i, j])
			if(p.contains_points([(i, j)]) or np.array_equal(point, points_4[0]) or np.array_equal(point, points_4[1]) or np.array_equal(point, points_4[2]) or np.array_equal(point, points_4[3])):
				matrix[y_img - 1 - j][i] = 1
	
				
	return matrix
 	
