from pathlib import Path
import os
import sighthound as Si
import dataset_class as Dat
from sklearn.metrics import jaccard_score
import json
import numpy as np
import openalp_request as Op

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track02' )
PATH_TO_DATA2 = Path('..', 'dataset2', 'UFPR-ALPR dataset', 'testing', 'track0135' )
SIGNS_NUM = 7
IMG_FORMAT  = '.png'

def jaccard_res(rect, data, index):

	pred = Si.get_bin_matrix(rect, data, index)
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
	
def sign_average(data, rectangle, number):
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
	
def calculate_IoU(name, dset, dpath, only_lp, algorithm, cut = 'lp'):				#only_lp == 0 -> all picture, only_lp == 1 -> only license plate
												#cut - 'lp' or 'car'
	rectangle_lp = 1
	rectangle = 1
	iou = 1
	iou_lp = 1
	
	data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dpath, dset)
	data.read_txt()
	
	lp_pos = data.get_lp_position()

	if(only_lp == 0 or only_lp == 2):

		if(algorithm == "sighthound"):
			result = Si.sighthound(dset, dpath, name, IMG_FORMAT, 0)
		if(algorithm == "openalpr"):
			result = Op.save_openalpr_res(dpath, name, IMG_FORMAT, 0)
	
		#print(result)
	
		if result == -1 or result == 0:
			iou = result
		
		else:
			#print("Detection Results = " + result )
			
			if(algorithm == "sighthound"):
				rectangle = Si.read_sigh_res(result, SIGNS_NUM, 0, 0, lp_pos[0], lp_pos[1])
			if(algorithm == "openalpr"):
				points = Op.read_openalpr_res(result, SIGNS_NUM)
				rectangle = Op.points_to_rectangle(points, SIGNS_NUM, 0, 0)
		
			iou = sign_average(data, rectangle, SIGNS_NUM)
	
	if(only_lp == 1 or only_lp == 2):
		cut_img, lp_X, lp_Y = data.cut_img(cut)
		
		if(algorithm == "sighthound"):
			result_lp = Si.sighthound(dset + '_' + cut, dpath, name, IMG_FORMAT, cut_img)
		if(algorithm == "openalpr"):
			result_lp = Op.save_openalpr_res(dpath, name, IMG_FORMAT, cut_img, cut)
		
		if result_lp == -1 or result_lp == 0:
			iou_lp = result_lp
		
		if(algorithm == "sighthound"):
			if len(result_lp['objects']) == 0 and only_lp > 1:
				iou_lp = -1
		if(algorithm == "openalpr"):
			if(result_lp == 0 and only_lp > 1):
				iou_lp = -1
		
		if(iou_lp == 1):
			if(algorithm == "sighthound"):
				rectangle_lp = Si.read_sigh_res(result_lp, SIGNS_NUM, lp_X, lp_Y, lp_pos[0] - lp_X, lp_pos[1] - lp_Y)
			if(algorithm == "openalpr"):
				points_lp = Op.read_openalpr_res(result_lp, SIGNS_NUM)
				rectangle_lp = Op.points_to_rectangle(points_lp, SIGNS_NUM, lp_X, lp_Y)
		
			iou_lp = sign_average(data, rectangle_lp, SIGNS_NUM)
		
	if(only_lp == 2):
		return iou, iou_lp
		
	if(only_lp == 1):
		return iou_lp		
		
	if(only_lp == 0):
		return iou
	
#strange_list - list of names when iou_lp < iou (только для номера < для целой картинки)
def dataset_IoU_sight(path, dset, only_lp, algorithm, remote_list = None, cut = 'lp', strange_list = None):		#dset - SSIG or UFPR		#algorithm - openalpr or sighthound
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
				#print(name)
				if(Path(dirs, name + IMG_FORMAT).exists()):
				
					if(remote_list is not None):
						if name in remote_list:
							iou = -1
							iou_lp = -1
					
					if(only_lp == 0 and iou != -1):
						iou = calculate_IoU(name, dset, dirs, only_lp, algorithm)
						print(name, "similarity =", iou)
					
					if(only_lp == 1 and iou != -1):
						iou = calculate_IoU(name, dset, dirs, only_lp, algorithm, cut)
						print(name, "lp similarity =", iou)
						
					if(only_lp == 2 and iou_lp != -1):
						iou, iou_lp = calculate_IoU(name, dset, dirs, only_lp, algorithm, cut)
						print(name, "similarity =", iou, "\nlp similarity =", iou_lp)
						
						if(strange_list is not None):
							if(type(strange_list) == list and iou_lp != -1 and iou > iou_lp):
								strange_list.append(name)	
					
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
	
	dataset_IoU_sight("../dataset1/SSIG-SegPlate/testing/Track06", "SSIG", 0, "sighthound", list1)
	#dataset_IoU_sight("../dataset2", "UFPR", 2, "openalpr", list1, "car")
	#dataset_IoU_sight("../dataset2", "UFPR", 1, "sighthound", list1, "car")
	#dataset_IoU_sight("../dataset1", "SSIG", 1, "sighthound", list1)

if __name__ == "__main__":
	main()
	
