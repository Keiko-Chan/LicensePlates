from pathlib import Path
import os
import sighthound as Si
import dataset_class as Dat
from sklearn.metrics import jaccard_score
import json
import numpy as np

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track23' )
PATH_TO_DATA2 = Path('..', 'dataset2', 'UFPR-ALPR dataset', 'testing', 'track0091' )
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

	return res
	
def sign_average(data, rectangle, number):
	#res = 0
	res1 = 0
	for  sign_index in range(0, number):
		#res = res + jaccard_res(rectangle, data, sign_index)
		res1 = res1 + jaccard_rectangle(rectangle, data, sign_index)
	
	#res = res / SIGNS_NUM
	res1 = res1 / SIGNS_NUM
	#print("average =", res, res1)
	return res1
	
def calculate_IoU_sight(name, dset, dpath, only_lp):					#only_lp == 0 -> all picture, only_lp == 1 -> only license plate

	result = Si.sighthound(dset, dpath, name, IMG_FORMAT, 0)
	
	if result == -1:
		return -1
	
	#print("Detection Results = " + result )
	rectangle = Si.read_sigh_res(result, SIGNS_NUM, 0, 0)
	
	data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dpath, dset)
	data.read_txt()	
	
	if(only_lp == 1):
		lp_img, lp_X, lp_Y = data.lp_img()
		result_lp = Si.sighthound(dset + "_lp", dpath, name, IMG_FORMAT, lp_img)
		rectangle_lp = Si.read_sigh_res(result_lp, SIGNS_NUM, lp_X, lp_Y)
		return sign_average(data, rectangle_lp, SIGNS_NUM)
		
	return sign_average(data, rectangle, SIGNS_NUM)
	
	
def dataset_IoU_sight(path, dset, only_lp):		#dset - SSIG or UFPR
	res = 0
	num = 0
	for dirs,folder,files in os.walk(path):
		for i in range(0, len(files)):
			p = Path(files[i])
			if(p.suffix == ".txt"):
				name = str(p.stem)
				print(name)
				if(Path(dirs, name + IMG_FORMAT).exists()):
					
					iou = calculate_IoU_sight(name, dset, dirs, only_lp)
					print(iou)
					
					if iou != -1:
						num = num + 1
						res = res + iou
					
	res = res / num
	print(res)
	return res
	
def main():
	print("in process...")
	
	print(calculate_IoU_sight("Track23[01]", "SSIG", PATH_TO_DATA1, 0))
	#print(calculate_IoU_sight("track0091[01]", "UFPR", PATH_TO_DATA2, 1))
	
	#dataset_IoU_sight("../dataset1", "SSIG", 0)
	#dataset_IoU_sight("../dataset2", "UFPR", 1)

if __name__ == "__main__":
	main()
	
