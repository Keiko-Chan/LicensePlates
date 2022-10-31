import cv2 as cv
import openalp_request as Op
import sighthound as Si
import dataset_class as Dat
from pathlib import Path
import marina_seg as Ma

SIGNS_NUM = 7
NEEDED_SIGNS_NUM = 7
IMG_FORMAT  = '.png'
MARINA_RES_PATH = Path('..', '..', 'svn', 'trunk', 'launch', 'result') 
MARINA_RES_PATH_LP = Path('..', '..', 'svn', 'trunk', 'launch', 'result_for_lp_flag')

def draw_line(img, x1, y1, x2, y2):
	line_thickness = 1
	cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), thickness=line_thickness)
	
def draw_rectangle(img, X, Y, x, y):
	draw_line(img, X, Y, X + x, Y)
	draw_line(img, X, Y, X, Y + y)
	draw_line(img, X + x, Y, X + x, Y + y)
	draw_line(img, X, Y + y, X + x, Y + y)
	
	return img

def draw_querty(img, point_4):
	draw_line(img, point_4[0][0], point_4[0][1], point_4[1][0], point_4[1][1])
	draw_line(img, point_4[1][0], point_4[1][1], point_4[3][0], point_4[3][1])
	draw_line(img, point_4[3][0], point_4[3][1], point_4[2][0], point_4[2][1])
	draw_line(img, point_4[2][0], point_4[2][1], point_4[0][0], point_4[0][1])

def draw_segmentation(name, rectangles, sq_count, rect):
	img = cv.imread(name, cv.IMREAD_COLOR)
	
	#cv.imshow('image',img)
	#cv.waitKey(0)
	#cv.destroyAllWindows()
	
	for i in range(0, sq_count):
		if(rect == 1):
			draw_rectangle(img, rectangles[0][i], rectangles[1][i], rectangles[2][i], rectangles[3][i])
		else:
			draw_querty(img, rectangles[i])
	
	return img

def marina_draw(name, dset, dpath, lp_pos, name_png, moto, lp = 0):
	if(lp == 0):
		mar_res_path_dset = Path(MARINA_RES_PATH, "brazilian_ufpr-alpr_testing")
	else:
		mar_res_path_dset = Path(MARINA_RES_PATH_LP, "brazilian_ufpr-alpr_testing")
		
	result = Ma.get_marina_res(dset, name, IMG_FORMAT, mar_res_path_dset)
	rectangles = Ma.get_points(result, SIGNS_NUM, moto)	
	print(rectangles)
	img = draw_segmentation(dpath + '/' + name_png, rectangles, NEEDED_SIGNS_NUM, 0)
	
	return img
	
def sighthound_draw(name, dset, dpath, lp_pos, name_png):
	result = Si.sighthound(dset, dpath, name, IMG_FORMAT, 0)
	rectangles = Si.read_sigh_res(result, NEEDED_SIGNS_NUM, 0, 0, lp_pos[0], lp_pos[1])
	img = draw_segmentation(dpath + '/' + name_png, rectangles, NEEDED_SIGNS_NUM, 1)
	
	return img

def data_draw(data, dset, dpath, lp_pos, name_png):
	img = cv.imread(dpath + '/' + name_png, cv.IMREAD_COLOR)
	
	print(data.X, data.Y, data.x, data.y)
	
	for i in range(0, NEEDED_SIGNS_NUM):
		img = draw_rectangle(img, data.X[i], data.Y[i], data.x[i], data.y[i])
	return img

def main():	
	name = "track0148[08]" #"Track6[11]" 
	name_png = name + ".png" #"Track6[11].png"
	dpath = "../dataset2/UFPR-ALPR dataset/testing/track0148" #"../dataset1/SSIG-SegPlate/testing/Track06" 
	dset = "UFPR" #"SSIG" 

	data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dpath, dset)
	lp_pos = data.get_lp_position()
	data.read_txt()

	img = marina_draw(name, dset, dpath, lp_pos, name_png, data.typ, 1)
	#img = data_draw(data, dset, dpath, lp_pos, name_png)
	
	#print(rectangles)
	
	#cut_img, lp_X, lp_Y = data.cut_img("lp")
	#result_lp = Si.sighthound(dset + '_lp', dpath, name, IMG_FORMAT, cut_img)
	#rectangles = Si.read_sigh_res(result_lp, SIGNS_NUM, lp_X, lp_Y, lp_pos[0] - lp_X, lp_pos[1] - lp_Y)
	#print(rectangles)
	
	cv.imshow('image',img)
	cv.waitKey(0)
	cv.destroyAllWindows()
	
if __name__ == "__main__":
	main()
