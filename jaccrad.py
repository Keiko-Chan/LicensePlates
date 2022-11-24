from pathlib import Path
import os
import sighthound as Si
import dataset_class as Dat
from sklearn.metrics import jaccard_score
import json
import numpy as np
import openalp_request as Op
import marina_seg as Ma
import pandas as pd
import collections
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track02' )
PATH_TO_DATA2 = Path('..', 'dataset2', 'UFPR-ALPR dataset', 'testing', 'track0135' )
SIGNS_NUM = 7
IMG_FORMAT  = '.png'
MARINA_RES_PATH = Path('..', '..', 'svn', 'trunk', 'launch', 'result')
MARINA_RES_PATH_CAR = Path('..', '..', 'svn', 'trunk', 'launch', 'result_cars') 
MARINA_RES_PATH_LP_0 = Path('..', '..', 'svn', 'trunk', 'launch', 'result_for_lp')
MARINA_RES_PATH_LP_1 = Path('..', '..', 'svn', 'trunk', 'launch', 'result_for_lp_flag')
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def check_result(algorithm, dset, name, cut, flag = 0):
	
	match flag:
		case 0:
			res_path = Path('results', str(cut) + '_' + algorithm + '_' + dset + ".json")
		case _:
			res_path = Path('results', str(cut) + '_flag' + str(flag) + '_' + algorithm + '_' + dset + ".json")
	
	if(res_path.exists() == False):
		return -2
	
	with open(str(res_path)) as f:
		file_content = f.read()
		my_dict = json.loads(file_content)
	
	if name in my_dict:
		return my_dict[name]
	
	else: 
		return -2
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------		
def sort_result(algorithm, dset, cut, flag = 0):
	match flag:
		case 0:
			res_path = Path('results', str(cut) + '_' + algorithm + '_' + dset + ".json")
		case _:
			res_path = Path('results', str(cut) + '_flag' + str(flag) + '_' + algorithm + '_' + dset + ".json")
			
	sort_dict = None
	
	if(res_path.exists() == False):
		return -1
		
	with open(str(res_path)) as f:
		file_content = f.read()
		my_dict = json.loads(file_content)
	
	for key in sorted(my_dict.keys()):
			if(sort_dict == None):
				sort_dict = {key: my_dict[key]}
			else:
				sort_dict.update({key: my_dict[key]})
				
	with open(str(res_path), 'w') as f:
		json.dump(sort_dict, f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=2)
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def save_result(iou, algorithm, dset, name, cut, flag = 0):

	res_path = Path('results')
	
	if(res_path.exists() == False):
		res_path.mkdir()
		
	match flag:
		case 0:
			res_path = Path(res_path, str(cut) + '_' + algorithm + '_' + dset + ".json")	
		case _:
			res_path = Path(res_path, str(cut) + '_flag' + str(flag) + '_' + algorithm + '_' + dset + ".json")
	
	if(res_path.exists() == True):
		with open(str(res_path)) as f:
			file_content = f.read()
			my_dict = json.loads(file_content)	
		
		new_track = {name: iou}
		my_dict.update(new_track)
	
	else:
		my_dict = {name: iou}
	
	
	with open(str(res_path), 'w') as f:
		json.dump(my_dict, f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=2)
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def jaccard_res(points, data, index, algorithm, cut = "lp"):
	
	match algorithm:
		case "sighthound":
			if(points[0][index] == 0 and points[1][index] == 0 and points[2][index] == 0 and points[3][index] == 0):
				return 0
			pred = Si.get_bin_matrix(points, data, index, cut)	
			
		case "openalpr":
			pred = Op.get_bin_matrix(points, data, index, cut)
		
		case "marina":
			if(points[index][0][0] == 0 and points[index][0][1] == 0 and points[index][1][0] == 0 and points[index][1][1] == 0):
				return 0
		
			pred = Ma.get_binary_matrix(points[index], data, cut)	

	true = data.get_bin_matrix(index)
	similarity = jaccard_score(pred, true, average="micro")

	#print(index + 1, "similarity =", similarity)
	return similarity
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------	
def jaccard_rectangle(rect, data, indx): 	#min max
	if(rect[3][indx] == 0 or rect[2][indx] == 0):
		return 0
		
	if(rect[0][indx] < data.X[indx]):
		X1 = rect[0][indx]
		x1 = rect[2][indx]
		X2 = data.X[indx]
		x2 = data.x[indx]
	else:
		X2 = rect[0][indx]
		x2 = rect[2][indx]
		X1 = data.X[indx]
		x1 = data.x[indx]
	
	if(rect[1][indx] < data.Y[indx]):
		Y1 = rect[1][indx]
		y1 = rect[3][indx]
		Y2 = data.Y[indx]
		y2 = data.y[indx]
	else:
		Y2 = rect[1][indx]
		y2 = rect[3][indx]
		Y1 = data.Y[indx]
		y1 = data.y[indx]
	
	#print(X1, x1, X2)
		
	if(X1 + x1 < X2):
		return 0
	
	if(Y1 + y1 < Y2):
		return 0
	
	if(X2 + x2 <= X1 + x1):
		a = x2	
	else:
		a = x1 - X2 + X1
		
	if(Y2 + y2 <= Y1 + y1):
		b = y2
	else:
		b = y1 - Y2 + Y1
	
	res = a * b / (rect[3][indx] * rect[2][indx] + data.y[indx] * data.x[indx] - a * b)
	
	#print(indx + 1, "similarity1 =", res)
	
	#if(res < 0.6):
		#print("here something")

	return res
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------	
def sign_average(data, rectangles, number, algorithm, how_calc = "my_alg", cut = 0):
	#print(rectangle)
	#res = 0
	res = 0
	for  sign_index in range(0, number):
		if(how_calc == "skl_met"):
			res = res + jaccard_res(rectangles, data, sign_index, algorithm, cut)
		else:
			res = res + jaccard_rectangle(rectangles, data, sign_index)
	
	res = res / SIGNS_NUM
	#print("average =", res, res1)
	return res
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def br_motobike_sort(rectangles, signes_num):
	sort_rectangles = np.zeros((4, signes_num), int)
	st = 1
	en = 1
	
	for i in range(0, 4):
		sort_rectangles[i][0] = rectangles[i][0]
	
	for i in range(1, signes_num):
		if(abs(sort_rectangles[1][st - 1] - rectangles[1][i]) > abs(sort_rectangles[0][st - 1] - rectangles[0][i])):
			for k in range(0, 4):
				sort_rectangles[k][signes_num - en] = rectangles[k][i]
			en = en + 1
		else:
			for k in range(0, 4):
				sort_rectangles[k][st] = rectangles[k][i]
			st = st + 1
	if(sort_rectangles[1][0] > sort_rectangles[1][signes_num - 1]):
		sorted_rectangles = np.zeros((4, signes_num), int)
		
		for i in range(0, 3):
			for k in range(0, 4):
				sorted_rectangles[k][i] = sort_rectangles[k][4 + i]

		for i in range(3, signes_num):
			for k in range(0, 4):
				sorted_rectangles[k][i] = sort_rectangles[k][i - 3]
		
		return sorted_rectangles
		
	return sort_rectangles
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def count_smth(rectangle, data, koef):
	hight = rectangle[0][1][1] - rectangle[0][0][1]
	
	if(rectangle[0][1][1] == 0 and rectangle[0][1][0] == 0 and rectangle[0][0][1] == 0 and rectangle[0][0][0] == 0):
		return 0
	
	if(hight < koef * data.y[0]):
		return 1
	
	return 0
#------------------------------------------------------------------------------------------------------------------------
#how_calc - 'my_alg', 'skl_met'
#only_lp == 0 -> all picture, only_lp == 1 -> only license plate
#cut - 'lp' or 'car'
#typ - 'all', 'car', 'motorcycle' 
#------------------------------------------------------------------------------------------------------------------------														
def calculate_IoU(counter, name, dset, dpath, only_lp, algorithm, cut = 'lp', typ = 'all', flag = 0):		
														
	rectangle_lp = 1
	rectangle = 1
	iou = None
	iou_lp = None
	how_calc = "my_alg"
	
	data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dpath, dset)
	data.read_txt()
	
	lp_pos = data.get_lp_position()
	
	if(type(cut) != str and type(cut) != int):
		if(only_lp == 2):
			return -1, -1
		else:
			return -1, counter
	
	match typ:
		case "car":
			if(data.typ != "car"):
				if(only_lp == 2):
					return -1, -1
				else:
					return -1, counter
		case "motorcycle":
			if(data.typ != "motorcycle"):
				if(only_lp == 2):
					return -1, -1
				else:
					return -1, counter
		
		
	if(only_lp == 0 or only_lp == 2):

		match algorithm:
			case "sighthound":
				result = Si.sighthound(dset, dpath, name, IMG_FORMAT, 0, 0)
			case "openalpr":
				result = Op.save_openalpr_res(dpath, name, IMG_FORMAT, 0)
			case "marina":
				match dset:
					case "UFPR":
						mar_res_path_dset = Path(MARINA_RES_PATH, "brazilian_ufpr-alpr_testing")
					case "SSIG":
						mar_res_path_dset = Path(MARINA_RES_PATH, "brazilian_ssig-plate_testing")
					case _:
						return -2
						
				result = Ma.get_marina_res(dset, name, IMG_FORMAT, mar_res_path_dset)
			case _:
				print("don`t know this algorithm", algorithm)
				if(only_lp == 2):
					return -2, -2
				else:
					return -2
	
		#print(result)
	
		if result == -1 or result == 0:
			iou = result
			
			
		if iou == None:
			saved_iou = check_result(algorithm, dset, name, "image", flag)
			if(saved_iou != -2):
				iou = saved_iou	

		if iou == None:	
			match algorithm:
				case "sighthound":
					rectangles = Si.read_sigh_res(result, SIGNS_NUM, 0, 0, lp_pos[0], lp_pos[1])
					#how_calc = "skl_met"
					if(data.typ == "motorcycle"):
						rectangles = br_motobike_sort(rectangles, SIGNS_NUM)
						#print(rectangle)
				
				case "openalpr":
					points = Op.read_openalpr_res(result, SIGNS_NUM)
					rectangles = Op.points_to_rectangle(points, SIGNS_NUM, 0, 0)
				
				case "marina":
					rectangles = Ma.get_points(result, SIGNS_NUM, data.typ)
					how_calc = "skl_met"
					#rectangles = Ma.read_marina_res(result, SIGNS_NUM, data.typ, lp_pos[2], lp_pos[3], lp_pos[0], lp_pos[1])
					#print(rectangles)
					#to do if rejected or something like that
					
			
			iou = sign_average(data, rectangles, SIGNS_NUM, algorithm, how_calc)
			save_result(iou, algorithm, dset, name, "image", flag)
			
	
	if(only_lp == 1 or only_lp == 2):
		#cut_img, lp_X, lp_Y = data.cut_img(cut)
		lp_X, lp_Y, lp_x, lp_y = data.get_lp_position(cut)
		
		match algorithm:
			case "sighthound":
				result_lp = Si.sighthound(dset + '_' + str(cut), dpath, name, IMG_FORMAT, data, cut)
				
				if(len(result_lp['objects']) == 0 and only_lp == 2):
					iou_lp = -1
					
			case "openalpr":
				result_lp = Op.save_openalpr_res(dpath, name, IMG_FORMAT, data, cut)
				
				if(result_lp == 0 and only_lp == 2):
					iou_lp = -1
					
			case "marina":
				match dset:
					case "UFPR":
						if(cut == "car"): 
							mar_res_path_dset = Path(MARINA_RES_PATH_CAR, "brazilian_ufpr-alpr_testing")
							
						else:							
							match flag:							
								case 1:
									mar_res_path_dset = Path(MARINA_RES_PATH_LP_1, "brazilian_ufpr-alpr_testing")
								case _:
									mar_res_path_dset = Path(MARINA_RES_PATH_LP_0, "brazilian_ufpr-alpr_testing")
					case "SSIG":
						if(cut == "car"): 
							iou_lp = -1
						
						else:
							match flag:
								case 1:
									mar_res_path_dset = Path(MARINA_RES_PATH_LP_1, "brazilian_ssig-plate_testing")
								case _:
									mar_res_path_dset = Path(MARINA_RES_PATH_LP_0, "brazilian_ssig-plate_testing")
					case _:
						return -2
				
				result_lp = Ma.get_marina_res(dset, name, IMG_FORMAT, mar_res_path_dset)
				
				if(result_lp != -1 and Ma.founded(result_lp) == False and only_lp == 2):
					iou_lp = -1
				
			case _:
				print("don`t know this algorithm", algorithm)
				if(only_lp == 2):
					return -2, -2
				else:
					return -2
		
		if (result_lp == -1 or result_lp == 0) and iou_lp != -1:
			iou_lp = result_lp
		
		if(iou_lp == None):
			saved_iou = check_result(algorithm, dset, name, cut, flag)
			if(saved_iou != -2):
				iou_lp = saved_iou	
		
		if(iou_lp == None):
			match algorithm:
			
				case "sighthound":
					rectangle_lp = Si.read_sigh_res(result_lp, SIGNS_NUM, lp_X, lp_Y, lp_pos[0] - lp_X, lp_pos[1] - lp_Y)
					if(data.typ == "motorcycle"):
						rectangle_lp = br_motobike_sort(rectangle_lp, SIGNS_NUM)
					
				case "openalpr":
					points_lp = Op.read_openalpr_res(result_lp, SIGNS_NUM)
					rectangle_lp = Op.points_to_rectangle(points_lp, SIGNS_NUM, lp_X, lp_Y)
				
				case "marina":
					rectangle_lp = Ma.get_points(result_lp, SIGNS_NUM, data.typ)
					how_calc = "skl_met"
					
			#counter = counter + count_smth(rectangle_lp, data, 0.7)
			iou_lp = sign_average(data, rectangle_lp, SIGNS_NUM, algorithm, how_calc, cut)
			save_result(iou_lp, algorithm, dset, name, cut, flag)
		
	match only_lp:
		case 2:
			return iou, iou_lp
		case 1:
			return iou_lp, counter
		case 0:
			return iou, counter
#------------------------------------------------------------------------------------------------------------------------
#strange_list - list of names when iou_lp < iou (только для номера < для целой картинки)
#dset - SSIG or UFPR
#algorithm - openalpr or sighthound
#------------------------------------------------------------------------------------------------------------------------
def dataset_IoU_sight(path, dset, only_lp, algorithm, remote_list = None, cut = 'lp', typ = 'all', strange_list = None, flag = 0):		
	res = 0
	res_lp = 0
	num_lp = 0
	num = 0
	trow_out = 0
	counter = 0
	new_remote_list = []
	for dirs,folder,files in os.walk(path):
		for i in range(0, len(files)):
			iou = 0
			iou_lp = 0
			p = Path(files[i])
			if(p.suffix == ".txt"):
				name = str(p.stem)
				#print(name)
				if(Path(dirs, name + IMG_FORMAT).exists()):
				
					if(remote_list is not None):
						if name in remote_list:
							iou = -1
							iou_lp = -1
					
					if(iou != -1):
						match only_lp:
							case 0:
								iou, counter = calculate_IoU(counter, name, dset, dirs, only_lp, algorithm, cut, typ, flag)
								print(name, "similarity =", iou)
					
							case 1:
								iou, counter = calculate_IoU(counter, name, dset, dirs, only_lp, algorithm, cut, typ, flag)
								print(name, "lp similarity =", iou, counter)
						
							case 2:
								iou, iou_lp = calculate_IoU(counter, name, dset, dirs, only_lp, algorithm, cut, typ, flag)
								print(name, "similarity =", iou, "\nlp similarity =", iou_lp)
						
								if(strange_list is not None):
									if(type(strange_list) == list and iou_lp != -1 and iou > iou_lp):
										strange_list.append(name)
							case _:
								print("only_lp can`t be", only_lp)
								return -1
					
					if iou != -1:
						num = num + 1
						res = res + iou
					else:
						#num = num + 1
						if(only_lp != 2):
							trow_out = trow_out + 1
							new_remote_list.append(name)
							
					
					if iou_lp != -1 and only_lp == 2:
						num_lp = num_lp + 1
						res_lp = res_lp + iou_lp
					else:
						if(only_lp == 2):
							trow_out = trow_out + 1
							new_remote_list.append(name)
						
					if iou != -1 and iou_lp == -1 and only_lp == 2:
						num = num - 1
						res = res - iou
			
	if(only_lp == 0):			
		sort_result(algorithm, dset, "image")
	else:
		sort_result(algorithm, dset, cut, flag)
		
	print("amount of images =", num)
	
	if(num + trow_out == 0):
		num = 1
	print("trown out =", trow_out, "percent =", trow_out/(num + trow_out)*100)
	
	if(remote_list is not None):
		remote_list.extend(new_remote_list)
	
	if(num != 0):
		res = res / num
		
	print("counter =", counter)
					
	if(only_lp == 2):
		if(num_lp != 0):
			res_lp = res_lp / num_lp
		print("result =", res, "\tlp =", res_lp)
		return res, res_lp
	
	else:
		
		print("result =", res)
		return res
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def main():
	print("in process...")

	list1 = []
	#'skl_met' /UFPR-ALPR dataset/testing/track0138"
	#dataset_IoU_sight("../dataset2", "UFPR", 2, "marina", list1, typ = "car")
	dataset_IoU_sight("../dataset2", "UFPR", 1, "sighthound", list1, cut = 10010)	
	#dataset_IoU_sight("../dataset2", "UFPR", 2, "openalpr", list1, cut = "lp", typ = "car")	
	#dataset_IoU_sight("../dataset2/UFPR-ALPR dataset", "UFPR", 1, "marina", list1, typ = "car", cut = "car")
	#dataset_IoU_sight("../dataset2/UFPR-ALPR dataset/testing/track0111", "UFPR", 1, "openalpr", list1, cut = "car")
	#dataset_IoU_sight("../dataset2", "UFPR", 1, "marina", list1, typ="motorcycle", flag = 1)
	#dataset_IoU_sight("../dataset2/UFPR-ALPR dataset/testing/track0135", "UFPR", 0, "sighthound", list1, "lp", "motorcycle")

if __name__ == "__main__":
	main()
	
