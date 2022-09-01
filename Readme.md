# How to use it #
---
## changes in sighthound.py ##

In this line you can see X-Access-Token:
		HEADERS = {"Content-type": "application/json", "X-Access-Token": "Your token"}
You need to register on the sighthound site and enter your token here "Your token".

---
## using ##

Use this function from jaccard.py
		dataset_IoU_sight(path, dset, only_lp, algorithm, remote_list = None,strange_list = None)
* path - path to dataset
* dset - "SSIG" (SSIG-SegPlate) or "UFPR" (UFPR-ALPR) 'authenticator' of data set, depends on the form of txt file.
* only_lp - 0 (whole image), 1 (only license plate picture, cut from image), 2 (1 and 0, where the pictures, in which the lp was not found in case '1', were removed from the dataset)
* algorithm - sighthound or openalpr
* remote_list - list of names of numbers to be removed and which were removed
* strange_list - list of names of lp, which iou for whole image was more than for only lp. Work only with only_lp = 2

---
## if you have another dataset ##

Need changes in dataset_class.py.
* in function get_lp_position(self), 'num_line' - line with lp position (like that: 'position_plate: 1390 782 145 49') 
		if(self.dset == "SSIG"):
			num_line = 1
		if(self.dset == "UFPR"):
			num_line = 7
* in function read_txt(self), 'start' - line wich start positions of signs ('end' its end..) (like that: 'char6: 1511 799 16 24')
		if(self.dset == "SSIG"):
			start = 3
			end = 10
		
		if(self.dset == "UFPR"):
			start = 8
			end = 15
Need change the country of lp in openalpr_request.py
Need change of count of signs in jaccard.py:
		SIGNS_NUM = 7
		
---
## changes in openalpr ##

I changed main.cpp file, to save opeanlpr results about license plate (most probable and first from them) segmentation. You can see it below.
Pay attention to this line:
		const std::string MY_PATH = "/home/ekatrina/prog/License plates/LicensePlates/openalpr_res" ;
It`s the path to folder openalpr_res which will appear in the folder with the program, this path in main.cpp must be changed manually.

If you need another country license plates, change 'br' on something else. 
		subprocess.run(["alpr" , '-c' , 'br', str(Path(path, (name + img_format)))])
		subprocess.run(["alpr", '-c' , 'br', img_path])
Changes:
		const std::string MY_PATH = "/home/ekatrina/prog/License plates/LicensePlates/openalpr_res" ;

		int save_to_file(std::string name_path, std::vector<AlprChar> character_vector, std::string path)
		{
			int slash_pos = name_path.rfind("/");
	
			std::string name = name_path;
	
			if(slash_pos != -1)
			name = name_path.substr(slash_pos);
		
			int point_pos = name.rfind(".");
			std::string new_name = name.substr(0, point_pos) + ".json";
			std::string new_path = path + "/" + new_name;
	
			std::ofstream f1;	
			f1.open(new_path);
			f1 << "{\"characters\":[";
	
			int vect_size = character_vector.size();
	
			for(int i = 0; i < vect_size; i++)
			{
				f1 << "{\"points\":[";
				for(int k = 0; k < 4; k++)
				{
					f1 << "{\"x\":\"" << character_vector[i].corners[k].x << "\",";
					f1 << "\"y\":\"" << character_vector[i].corners[k].y << "\"}";
				
					if(k != 3)
						f1 << ",";
				}
				f1 << "]}";
		
				if(i != vect_size - 1)
					f1 << ",";
			}
			f1 << "]}";
	
			f1.close();
	
			return 0;
		}

		int save_fail_file(std::string name_path, std::string path, std::string error)
		{
			int slash_pos = name_path.rfind("/");
	
			std::string name = name_path;
	
			if(slash_pos != -1)
				name = name_path.substr(slash_pos);
		
			int point_pos = name.rfind(".");
			std::string new_name = name.substr(0, point_pos) + ".json";
			std::string new_path = path + "/" + new_name;
		
			std::ofstream f1;	
			f1.open(new_path);
	
			f1 << "{\"error\":\"";
			f1 << error;
			f1 << "\"}";
	
			f1.close();
	
			return 0;
		}
I used this functions in function detectandshow
		if(results.plates.size() > 0)
		{
			std::vector<AlprChar> character_vector = results.plates[0].bestPlate.character_details;
      
			//std::cout << character_vector[0].corners[0].x << " " << character_vector[0].corners[1].x << " " << character_vector[0].corners[2].x << " " << character_vector[0].corners[3].x << std::endl;
              
			save_to_file(my_filename, character_vector, MY_PATH);
		}
	
  
		if(results.plates.size() < 1)
			save_fail_file(my_filename, MY_PATH, "nothing founded");
