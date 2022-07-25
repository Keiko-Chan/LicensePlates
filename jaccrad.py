from pathlib import Path
import base64
import sighthound as Si
import dataset_class as Dat
from sklearn.metrics import jaccard_score
from scipy.spatial.distance import jaccard

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track23' )
PATH_TO_DATA2 = Path('..', 'dataset2', 'UFPR-ALPR dataset', 'training', 'track0001' )

def jaccard_res(pred, true, index):
	similarity = jaccard_score(pred, true, average="micro")
	#distance = jaccard(pred, true)
	print(index + 1, "similarity =", similarity)
	return similarity
	
def sign_average(data, points):
	res = 0
	for  sign_index in range(0, 7):
		true = data.get_bin_matrix(sign_index)
		pred = Si.get_bin_matrix(points, data, sign_index)
		res = res + jaccard_res(pred, true, sign_index)
	
	res = res / 7
	print("average =", res)
	return res
	
def calculate_IoU(name, dset, dpath):	
	image_data = base64.b64encode(open(Path(dpath, name + ".png"), "rb").read()).decode()
	result = str(Si.sighthound(image_data))
	print("Detection Results = " + result )
	
	data = Dat.Dataset(name + ".txt", name + ".png", dpath)
	data.read_txt(dset)
	
	points = Si.sigh_res(result)
		
	sign_average(data, points)
	
def main():
	print("in process...")
	
	#calculate_IoU("Track23[01]", "SSIG", PATH_TO_DATA1)
	calculate_IoU("track0001[03]", "UFPR", PATH_TO_DATA2)

if __name__ == "__main__":
	main()
	
