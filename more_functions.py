import dataset_class as Dat
from pathlib import Path
import os
import cv2 as cv
import json
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate')
PATH_TO_DATA2 = Path('..', 'dataset2', 'UFPR-ALPR dataset')
IMG_FORMAT  = '.png'
JSON_PATH = Path('..', "..", "svn", "markup", "test", "brazilian_ufpr-alpr_testing")
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
def save_cut_dset(path, dset, res_path, cut = 'lp',  remote_list = None):
	
	if(res_path.exists() == False):
		res_path.mkdir()	
	
	for dirs,folder,files in os.walk(path):
		for i in range(0, len(files)):
			p = Path(files[i])
			if(p.suffix == ".txt"):
				name = str(p.stem)
				print(name)
				if(Path(dirs, name + IMG_FORMAT).exists()):
				
					if(remote_list is not None):
						if name in remote_list:
							break
					
					data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dirs, dset)
					data.read_txt()
					
					if(dset == "SSIG" and cut == "car"):
						break
					
					lp_X, lp_Y, lp_x, lp_y = data.get_lp_position(cut)		
					img = cv.imread(str(Path(data.path, data.name_img)))		
					cut_img = img[lp_Y : lp_Y + lp_y, lp_X : lp_x + lp_X]
					
					save_path = Path(res_path, name + IMG_FORMAT)
					
					if(save_path.exists() == False):
						cv.imwrite(str(save_path), cut_img)
						

def save_json_files(path, dset, res_path, json_path, cut = 'lp'):
	if(res_path.exists() == False):
		res_path.mkdir()	
	
	for dirs,folder,files in os.walk(path):
		for i in range(0, len(files)):
			p = Path(files[i])
			if(p.suffix == ".txt"):
				name = str(p.stem)
				print(name)
				
				if(dset == "SSIG" and cut == "car"):
					break	
				
				if(not Path(dirs, name + IMG_FORMAT).exists()):
					continue
				
				json_name_path = Path(json_path, name + IMG_FORMAT + ".json")
				new_res_path = Path(res_path,  name + IMG_FORMAT + ".json")
				
				if(not json_name_path.exists()):
					continue	
					
				data = Dat.Dataset(name + ".txt", name + IMG_FORMAT, dirs, dset)
				data.read_txt()
				
				lp_X, lp_Y, lp_x, lp_y = data.get_lp_position(cut)
					
				with open(str(json_name_path)) as f:
					file_content = f.read()
					new_json = json.loads(file_content)
				
				
				for i in range(0, 4):
					new_json["plates"][0]["frame"][i][0] = new_json["plates"][0]["frame"][i][0] - lp_X
					new_json["plates"][0]["frame"][i][1] = new_json["plates"][0]["frame"][i][1] - lp_Y
					#print(new_json['plates'][0]['frame'][i][0])
					#print(new_json["plates"][0]["frame"][i][1])
				
				with open(str(new_res_path), 'w') as f:
					json.dump(new_json, f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=2)


def main():
	res_path = Path('..', 'UFPR_car_set_json')
	#save_cut_dset(PATH_TO_DATA2, "UFPR", res_path, cut = 'car')
	save_json_files(PATH_TO_DATA2, "UFPR", res_path, JSON_PATH, cut = 'car')

if __name__ == "__main__":
	main()
