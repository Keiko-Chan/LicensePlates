import cv2 as cv
from pathlib import Path
import numpy as np
import base64
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
class Dataset:

	X = np.zeros(7, int)
	Y = np.zeros(7, int)
	x = np.zeros(7, int)
	y = np.zeros(7, int)
	
	
	def __init__(self, name_txt, name_img, path, dset):
		self.name_txt = name_txt
		self.name_img = name_img
		self.path = path
		self.dset = dset
		self.typ = "car"
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------		
	def read_txt(self):
		f = open(str(Path(self.path, self.name_txt)), 'r')
		lines = f.readlines()
		
		start = 0
		end = 0
		
		if(self.dset == "SSIG"):
			start = 3
			end = 10
		
		if(self.dset == "UFPR"):
			start = 8
			end = 15
			typ_l = 2 
		
		for i in range(start, end):
			#print(lines[i])
			ind = 0
			st = ''
			
			dots = lines[i].find(":")
			slen = len(lines[i])
			
			for k in lines[i][dots:slen]:
				if k == ' ':
					if ind == 1:		
						self.X[i - start] = int(st)
					if ind == 2:
						self.Y[i - start] = int(st)
					if ind == 3:
						self.x[i - start] = int(st)
	
					ind = ind + 1
					st = ''
					
				if k.isdigit:
					st = st + k
					
			self.y[i - start] = int(st)
			#print(self.y[i - start])
			
		if(self.dset == "UFPR"):
			dots = lines[typ_l].find(":")
			slen = len(lines[typ_l])
			
			self.typ = lines[typ_l][dots + 2:slen - 1]
					
			#print(self.X, self.Y, self.x, self.y)
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------			
	def get_lp_number(self):
		f = open(str(Path(self.path, self.name_txt)), 'r')
		lines = f.readlines()
		
		if(self.dset == "SSIG"):
			num_line = 0
		if(self.dset == "UFPR"):
			num_line = 6
		if(self.dset != "UFPR") and (self.dset != "SSIG"):
			print("error: don`t know this dset")
			return -1
			
		dots = lines[num_line].find(":")
		
		lp_num = lines[num_line][dots + 2 : len(lines[num_line])]
		print(lp_num)
		return lp_num
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------		
	def get_img_size(self):
		img = cv.imread(str(Path(self.path, self.name_img)), cv.IMREAD_GRAYSCALE)
		dimensions = img.shape
		#print(dimensions)
		return dimensions[0], dimensions[1]
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------	
	def get_bin_matrix(self, indx):								#check that index is possible
		y_img, x_img = self.get_img_size()	
		matrix = np.zeros((y_img, x_img))
		
		for i in range(0, self.x[indx]):
			for j in range(0, self.y[indx]):
				matrix[y_img - 1 - self.Y[indx] - j][self.X[indx] + i] = 1	#may be error here
		
		#print(matrix)
		return matrix
#------------------------------------------------------------------------------------------------------------------------
#obg = 0 - license plate, obg = 1 - car
#------------------------------------------------------------------------------------------------------------------------		
	def get_lp_position(self, cut = 'lp'):								
		f = open(str(Path(self.path, self.name_txt)), 'r')
		lines = f.readlines()
		
		if(self.dset == "SSIG"):
			num_line = 1
		if(self.dset == "UFPR"):
			if(cut == 'car'):
				num_line = 1
			if(cut == 'lp' or type(cut) == int):
				num_line = 7
			
		if(self.dset != "SSIG" and self.dset != "UFPR"):
			print("error: dont know this dset")
			return -1
			
		dots = lines[num_line].find(":")	
		ind = 0
		st = ''
		slen = len(lines[num_line])
		
		for k in lines[num_line][dots:slen]:
			if k == ' ' or k == '\n':
				if ind == 1:		
					lp_X = int(st)
				if ind == 2:
					lp_Y = int(st)
				if ind == 3:
					lp_x = int(st)
				if ind == 4:
					lp_y = int(st)
	
				ind = ind + 1
				st = ''
					
			if k.isdigit:
				st = st + k
								
		
		if(type(cut) == int):								#frame
			X_max, Y_max = self.get_img_size()
			xpr = cut % 1000 
			ypr = cut // 1000
			lp_X = lp_X - int(xpr * lp_x / 100)
			lp_Y = lp_Y - int(ypr * lp_y / 100)
			lp_y = lp_y + int(ypr * lp_y / 100)
			lp_x = lp_x + int(xpr * lp_x / 100)
			
			if(lp_X < 0):
				lp_X = 0
				
			if(lp_Y < 0):
				lp_Y = 0
				
			if(lp_x + lp_X >= X_max - 1):
				lp_x = X_max - lp_x - 1
				
			if(lp_y + lp_Y >= Y_max - 1):
				lp_y = Y_max - lp_y - 1
					
					
		#print(lp_X, lp_Y, lp_x, lp_y)
		
		return lp_X, lp_Y, lp_x, lp_y
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------		
	def cut_img(self, cut):
	
		lp_X, lp_Y, lp_x, lp_y = self.get_lp_position(cut)		
		
		img = cv.imread(str(Path(self.path, self.name_img)))
		
		lp_img = img[lp_Y : lp_Y + lp_y, lp_X : lp_x + lp_X]
		
		#cv.imshow('sample image1',lp_img)
		#cv.imshow('sample image2',img)
		#cv.waitKey(0)
		#cv.destroyAllWindows() 
		
		success, encoded_lp = cv.imencode('.png', lp_img)
		lp_bytes = encoded_lp.tobytes()
		lp_img = base64.b64encode(lp_bytes).decode()
		
		return lp_img, lp_X, lp_Y
		
