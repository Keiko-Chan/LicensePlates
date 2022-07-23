import cv2 as cv
from pathlib import Path
import numpy as np

class Dataset:

	X = np.zeros(7, int)
	Y = np.zeros(7, int)
	x = np.zeros(7, int)
	y = np.zeros(7, int)
	
	
	def __init__(self, name_txt, name_img, path):
		self.name_txt = name_txt
		self.name_img = name_img
		self.path = path
		
	def read_txt_SSIG(self):
		f = open(str(Path(self.path, self.name_txt)), 'r')
		lines = f.readlines()
		
		for i in range(3, 10):
			#print(lines[i])
			ind = 0
			st = ''
			
			for k in lines[i] :
				if k == ' ':
					if ind == 1:		
						self.X[i-3] = int(st)
					if ind == 2:
						self.Y[i-3] = int(st)
					if ind == 3:
						self.x[i-3] = int(st)
	
					ind = ind + 1
					st = ''
					
				if k.isdigit:
					st = st + k
					
			self.y[i-3] = int(st)
					
			#print(self.X, self.Y, self.x, self.y)
	
	def get_img_size(self):
		img = cv.imread(str(Path(self.path, self.name_img)), cv.IMREAD_GRAYSCALE)
		dimensions = img.shape
		#print(dimensions)
		return dimensions[0], dimensions[1]
	
	def get_bin_matrix(self, indx):								#check that index is possible
		y_img, x_img = self.get_img_size()	
		matrix = np.zeros((y_img, x_img))
		
		for i in range(0, self.x[indx]):
			for j in range(0, self.y[indx]):
				matrix[y_img - 1 - self.Y[indx] + j][self.X[indx] + i] = 1	#may be error hear
		
		#print(matrix)
		return matrix
		
		
