from pathlib import Path
import base64
import os
import sighthound as Si
import dataset_class as Dat
from sklearn.metrics import jaccard_score
from scipy.spatial.distance import jaccard
import json
import numpy as np

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track23' )
PATH_TO_DATA2 = Path('..', 'dataset2', 'UFPR-ALPR dataset', 'testing', 'track0091' )
SIGNS_NUM = 7

def jaccard_res(pred, true, index):
	similarity = jaccard_score(pred, true, average="micro")
	#distance = jaccard(pred, true)
	#print(index + 1, "similarity =", similarity)
	return similarity
	
def sign_average(data, points, number):
	res = 0
	for  sign_index in range(0, number):
		true = data.get_bin_matrix(sign_index)
		pred = Si.get_bin_matrix(points, data, sign_index)
		res = res + jaccard_res(pred, true, sign_index)
	
	res = res / SIGNS_NUM
	print("average =", res)
	return res
	
def calculate_IoU_sight(name, dset, dpath):	

	p_path = Path('sightound_points_' + dset)

	if(p_path.exists() == False):
		p_path.mkdir()
	
	p_path = Path(p_path, name + '.json')
		
	if(p_path.exists() == False):
			
		image_data = base64.b64encode(open(Path(dpath, name + ".png"), "rb").read()).decode()
		result = str(Si.sighthound(image_data))
		#print("Detection Results = " + result )
		points = Si.read_sigh_res(result, SIGNS_NUM)
			
		with open(str(p_path), 'w') as f:
			json.dump(points.tolist(), f)
	else:
		
		with open(str(p_path)) as f:
			file_content = f.read()
			p_list = json.loads(file_content)
			points = np.array(p_list)
	
	
	data = Dat.Dataset(name + ".txt", name + ".png", dpath)
	data.read_txt(dset)	
		
	return sign_average(data, points, SIGNS_NUM)
	
	
def dataset_IoU_sight(path, dset):
	res = 0
	num = 0
	for dirs,folder,files in os.walk(path):
		for i in range(0, len(files)):
			p = Path(files[i])
			if(p.suffix == ".txt"):
				name = str(p.stem)
				#print(name)
				if(Path(dirs, name + ".png").exists() or Path(dirs, name + ".jpg").exists()):
					num = num + 1
					res = res + calculate_IoU_sight(name, dset, dirs)
					
	res = res / num
	print(res)
	return res
	
def main():
	print("in process...")
	
	calculate_IoU_sight("Track23[01]", "SSIG", PATH_TO_DATA1)
	calculate_IoU_sight("track0091[01]", "UFPR", PATH_TO_DATA2)
	
	#dataset_IoU_sight("../dataset1", "SSIG")

if __name__ == "__main__":
	main()
	
