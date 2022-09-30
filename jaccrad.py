from pathlib import Path
import os
import sighthound as Si
import dataset_class as Dat
from sklearn.metrics import jaccard_score
import json
import numpy as np
import openalp_request as Op
import marina_seg as Ma

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track02' )
PATH_TO_DATA2 = Path('..', 'dataset2', 'UFPR-ALPR dataset', 'testing', 'track0135' )
SIGNS_NUM = 7
IMG_FORMAT  = '.png'
MARINA_RES_PATH = Path('..', '..', 'svn', 'trunk', 'launch', 'result') 
MARINA_RES_PATH_LP = Path('..', '..', 'svn', 'trunk', 'launch', 'result_for_lp')

def jaccard_res(points, data, index, alg):

	pred = Si.get_bin_matrix(ponts_4, data, index)
	true = data.get_bin_matrix(index)

	similarity = jaccard_score(pred, true, average="micro")

	#print(index + 1, "similarity =", similarity)
	return similarity
	
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
	
def sign_average(data, rectangle, number, how_calc):
	#print(rectangle)
	#res = 0
	res1 = 0
	for  sign_index in range(0, number):
		#res = res + jaccard_res(rectangle, data, sign_index)
		res1 = res1 + jaccard_rectangle(rectangle, data, sign_index)
	
	#res = res / SIGNS_NUM
	res1 = res1 / SIGNS_NUM
	#print("average =", res, res1)
	return res1

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
	
														#how_calc - 'my_alg', 'skl_met'
def calculate_IoU(name, dset, dpath, only_lp, algorithm, how_calc = 'my_alg', cut = 'lp', typ = 'all'):		#only_lp == 0 -> all picture, only_lp == 1 -> only license plate
														#cut - 'lp' or 'car'	#typ - 'all', 'car', 'motorcycle' 
	rectangle_lp = 1
	rectangle = 1
	iou = 1
	iou_lp = 1
	
	data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dpath, dset)
	data.read_txt()
	
	lp_pos = data.get_lp_position()
	
	match typ:
		case "car":
			if(data.typ != "car"):
				if(only_lp == 2):
					return -1, -1
				else:
					return -1
		case "motorcycle":
			if(data.typ != "motorcycle"):
				if(only_lp == 2):
					return -1, -1
				else:
					return -1
		
		
	if(only_lp == 0 or only_lp == 2):

		match algorithm:
			case "sighthound":
				result = Si.sighthound(dset, dpath, name, IMG_FORMAT, 0)
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
		
		else:
			#print("Detection Results = " + result )
			
			match algorithm:
				case "sighthound":
					rectangles = Si.read_sigh_res(result, SIGNS_NUM, 0, 0, lp_pos[0], lp_pos[1])
					if(data.typ == "motorcycle"):
						rectangles = br_motobike_sort(rectangles, SIGNS_NUM)
						#print(rectangle)
				
				case "openalpr":
					points = Op.read_openalpr_res(result, SIGNS_NUM)
					rectangles = Op.points_to_rectangle(points, SIGNS_NUM, 0, 0)
				
				case "marina":
					if(how_calc == "skl_met"):
						rectangles = Ma.get_points(result, SIGNS_NUM)
					else:
						rectangles = Ma.read_marina_res(result, SIGNS_NUM, lp_pos[0], lp_pos[1])
					#print(rectangles)
					#to do if rejected or something like that
		
			iou = sign_average(data, rectangles, SIGNS_NUM, how_calc)
	
	if(only_lp == 1 or only_lp == 2):
		cut_img, lp_X, lp_Y = data.cut_img(cut)
		
		
		match algorithm:
			case "sighthound":
				result_lp = Si.sighthound(dset + '_' + cut, dpath, name, IMG_FORMAT, cut_img)
				
				if(len(result_lp['objects']) == 0 and only_lp == 2):
					iou_lp = -1
					
			case "openalpr":
				result_lp = Op.save_openalpr_res(dpath, name, IMG_FORMAT, cut_img, cut)
				
				if(result_lp == 0 and only_lp == 2):
					iou_lp = -1
					
			case "marina":
				match dset:
					case "UFPR":
						mar_res_path_dset = Path(MARINA_RES_PATH_LP, "brazilian_ufpr-alpr_testing")
					case "SSIG":
						mar_res_path_dset = Path(MARINA_RES_PATH_LP, "brazilian_ssig-plate_testing")
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
		
		
		if(iou_lp == 1):
			match algorithm:
			
				case "sighthound":
					rectangle_lp = Si.read_sigh_res(result_lp, SIGNS_NUM, lp_X, lp_Y, lp_pos[0] - lp_X, lp_pos[1] - lp_Y)
					if(data.typ == "motorcycle"):
						rectangle_lp = br_motobike_sort(rectangle_lp, SIGNS_NUM)
					
				case "openalpr":
					points_lp = Op.read_openalpr_res(result_lp, SIGNS_NUM)
					rectangle_lp = Op.points_to_rectangle(points_lp, SIGNS_NUM, lp_X, lp_Y)
				
				case "marina":
					if(how_calc == "skl_met"):
						rectangle_lp = Ma.get_points(result, SIGNS_NUM)
					else:
						rectangle_lp = Ma.read_marina_res(result_lp, SIGNS_NUM, lp_pos[0] - lp_X, lp_pos[1] - lp_Y)
					#print(rectangle_lp)
		
			iou_lp = sign_average(data, rectangle_lp, SIGNS_NUM, how_calc)
		
	match only_lp:
		case 2:
			return iou, iou_lp
		case 1:
			return iou_lp
		case 0:
			return iou
	
#strange_list - list of names when iou_lp < iou (только для номера < для целой картинки)
def dataset_IoU_sight(path, dset, only_lp, algorithm, remote_list = None, how_calc = 'my_alg', cut = 'lp', typ = 'all', strange_list = None):		#dset - SSIG or UFPR		#algorithm - openalpr or sighthound
	res = 0
	res_lp = 0
	num_lp = 0
	num = 0
	trow_out = 0
	new_remote_list = []
	for dirs,folder,files in os.walk(path):
		for i in range(0, len(files)):
			iou = 0
			iou_lp = 0
			p = Path(files[i])
			if(p.suffix == ".txt"):
				name = str(p.stem)
				print(name)
				if(Path(dirs, name + IMG_FORMAT).exists()):
				
					if(remote_list is not None):
						if name in remote_list:
							iou = -1
							iou_lp = -1
					
					if(iou != -1):
						match only_lp:
							case 0:
								iou = calculate_IoU(name, dset, dirs, only_lp, algorithm, cut, typ)
								print(name, "similarity =", iou)
					
							case 1:
								iou = calculate_IoU(name, dset, dirs, only_lp, algorithm, cut, typ)
								print(name, "lp similarity =", iou)
						
							case 2:
								iou, iou_lp = calculate_IoU(name, dset, dirs, only_lp, algorithm, cut, typ)
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
						
	print("trown out =", trow_out, "percent =", trow_out/(num + trow_out)*100)
	
	if(remote_list is not None):
		remote_list.extend(new_remote_list)
	
	if(num != 0):
		res = res / num
		
					
	if(only_lp == 2):
		if(num_lp != 0):
			res_lp = res_lp / num_lp
		print("result =", res, "\tlp =", res_lp)
		return res, res_lp
	
	else:
		
		print("result =", res)
		return res
	
def main():
	print("in process...")
	
	list1 = []
	
	#dataset_IoU_sight("../dataset1/SSIG-SegPlate/testing/Track06", "SSIG", 0, "sighthound", list1)
	#dataset_IoU_sight("../dataset2", "UFPR", 2, "sighthound", list1, "lp", "car")
	dataset_IoU_sight("../dataset1/SSIG-SegPlate/testing/Track06", "SSIG", 0, "marina", list1, 'my_alg')
	#dataset_IoU_sight("../dataset1/SSIG-SegPlate", "SSIG", 0, "openalpr", list1)
	#dataset_IoU_sight("../dataset2/UFPR-ALPR dataset/testing/track0135", "UFPR", 0, "sighthound", list1, "lp", "all")
	#dataset_IoU_sight("../dataset1", "SSIG", 0, "sighthound", list1)

if __name__ == "__main__":
	main()
	
