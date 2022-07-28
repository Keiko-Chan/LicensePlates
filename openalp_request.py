import json
from openalpr import Alpr
from pathlib import Path

PATH_TO_DATA1 = Path('..', 'dataset1', 'SSIG-SegPlate', 'testing', 'Track23' )

alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data/")
if not alpr.is_loaded():
    print("Error loading OpenALPR")
    sys.exit(1)
results = alpr.recognize_file(Path(PATH_TO_DATA1, "Track23[01].png"))
print(json.dumps(results, indent=4))
alpr.unload()
