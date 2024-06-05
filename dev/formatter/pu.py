import json
from .utils import *

root_dir = get_dir("pu")
file_info_file = os.path.join(root_dir, "fault.json")
file_info = json.load(open(file_info_file, "r"))

freq = 64000

all_file_num = get_file_num(root_dir)


def add_pu(database: RawDataset):
    with tqdm(total=all_file_num) as pbar:
        for sub_dir in os.listdir(root_dir):
            if sub_dir == "fault.json":
                pbar.update(1)
                continue
            fault, severity = file_info[sub_dir]
            label = DataLabel(fault, severity)
            for file in os.listdir(os.path.join(root_dir, sub_dir)):
                if file.endswith(".mat"):
                    rpm = int(file.split("_")[0][1:]) * 100
                    all_data = sio.loadmat(os.path.join(root_dir, sub_dir, file))
                    for key in all_data.keys():
                        if not key.endswith("__"):
                            data = all_data[key]["Y"][0][0][0][6][2][0]
                            data = data.flatten()
                            info = DataInfo("PU", 0, rpm, freq)
                            database.add_data(info, label, data)
                pbar.update(1)
                pbar.set_postfix_str(file)
