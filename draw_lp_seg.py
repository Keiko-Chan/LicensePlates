import cv2 as cv
import openalp_request as Op
import sighthound as Si
import dataset_class as Dat

SIGNS_NUM = 7
IMG_FORMAT  = '.png'

def draw_line(img, x1, y1, x2, y2):
	line_thickness = 1
	cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), thickness=line_thickness)
	
def draw_rectangle(img, X, Y, x, y):
	draw_line(img, X, Y, X + x, Y)
	draw_line(img, X, Y, X, Y + y)
	draw_line(img, X + x, Y, X + x, Y + y)
	draw_line(img, X, Y + y, X + x, Y + y)

def draw_segmentation(name, rectangles, sq_count):
	img = cv.imread(name, cv.IMREAD_COLOR)
	
	#cv.imshow('image',img)
	#cv.waitKey(0)
	#cv.destroyAllWindows()
	
	for i in range(0, sq_count):
		draw_rectangle(img, rectangles[0][i], rectangles[1][i], rectangles[2][i], rectangles[3][i])
	
	return img

def main():	
	name = "Track6[11]" #"track0135[22]"
	name_png = "Track6[11].png" #"track0135[22].png"
	dpath = "../dataset1/SSIG-SegPlate/testing/Track06" #"../dataset2/UFPR-ALPR dataset/testing/track0135"
	dset = "SSIG" #"UFPR"

	data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dpath, dset)
	lp_pos = data.get_lp_position()

	result = Si.sighthound(dset, dpath, name, IMG_FORMAT, 0)
	rectangles = Si.read_sigh_res(result, 6, 0, 0, lp_pos[0], lp_pos[1])
	
	print(rectangles)
	
	#cut_img, lp_X, lp_Y = data.cut_img("lp")
	#result_lp = Si.sighthound(dset + '_lp', dpath, name, IMG_FORMAT, cut_img)
	#rectangles = Si.read_sigh_res(result_lp, SIGNS_NUM, lp_X, lp_Y, lp_pos[0] - lp_X, lp_pos[1] - lp_Y)
	#print(rectangles)
	
	img = draw_segmentation(dpath + '/' + name_png, rectangles, 6)
	
	
	cv.imshow('image',img)
	cv.waitKey(0)
	cv.destroyAllWindows()
	
if __name__ == "__main__":
	main()
