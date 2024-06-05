from .utils import *

root_dir = get_dir("hust")

fault_dict = {
    "N": 0,
    "I": 1,
    "B": 2,
    "O": 3
}


def add_hust(database: RawDataset):
    file_list = os.listdir(root_dir)
    with tqdm(total=len(file_list)) as pbar:
        for file in file_list:
            if file.endswith(".mat"):
                fault_list = []
                file_id = file.split(".")[0]
                for file_char in file_id:
                    if file_char in fault_dict:
                        fault_list.append(fault_dict[file_char])
                all_data = sio.loadmat(os.path.join(root_dir, file))
                rpm = all_data["fs"][0][0] * 60
                ch_data = all_data["data"].reshape(-1)
                info = DataInfo("HUST", 0, rpm, 51200)
                label = DataLabel(fault_list, 2)
                database.add_data(info, label, ch_data)
            pbar.update(1)
            pbar.set_postfix_str(file)
