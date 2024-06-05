import json

from .utils import *

root_dir = get_dir("cwru")
file_info_json = os.path.join(root_dir, "CWRU.json")
file_info: dict = json.load(open(file_info_json, "r", encoding="utf-8"))


def get_file_info(file_name: str):
    file_id = file_name.split(".")[0]
    file_class: int = file_info[file_id][0]
    freq_list = [48000, 12000, 48000, 12000]
    freq = freq_list[file_class]
    fault: int = file_info[file_id][2]
    severity: int = file_info[file_id][3]
    if severity == 4:
        severity = 3
    return freq, fault, severity


def get_rpm(data: dict):
    for key in data.keys():
        if key.endswith("RPM"):
            return int(data[key])
    return 1725


def add_cwru(database: RawDataset):
    file_dir = os.path.join(root_dir, "data")
    with tqdm(total=len(os.listdir(file_dir))) as pbar:
        for file in os.listdir(file_dir):
            if file.endswith(".mat"):
                freq, fault, severity = get_file_info(file)
                all_data = sio.loadmat(os.path.join(file_dir, file))
                ch_id = 0
                rpm = get_rpm(all_data)
                for key in all_data.keys():
                    if key.endswith("_time"):
                        data = all_data[key].reshape(-1)
                        data = np.array(data)
                        info = DataInfo("CWRU", ch_id, rpm, freq)
                        label = DataLabel(fault, severity)
                        database.add_data(info, label, data)
                        ch_id += 1
            pbar.update(1)
            pbar.set_postfix_str(file)
