from .utils import *

root_dir = get_dir("dirg")

freq = 51200

fault_dict = {
    "C0A": (0, 0),
    "C1A": (1, 3),
    "C2A": (1, 2),
    "C3A": (1, 1),
    "C4A": (2, 3),
    "C5A": (2, 2),
    "C6A": (2, 1),
}


def add_dirg(database: RawDataset):
    with tqdm(total=len(os.listdir(root_dir))) as pbar:
        for file in os.listdir(root_dir):
            if file.endswith(".mat"):
                rpm = int(file.split("_")[1])*60
                file_type = file.split("\\")[-1].split("_")[0]
                fault, severity = fault_dict[file_type]
                all_data = sio.loadmat(os.path.join(root_dir, file))
                for key in all_data.keys():
                    if "__" not in key:
                        data = np.array(all_data[key], dtype=np.float32)
                        chs = data.shape[1]
                        for ch_id in range(chs):
                            ch_data = data[:, ch_id]
                            info = DataInfo("DIRG", ch_id, rpm, freq)
                            label = DataLabel(fault, severity)
                            database.add_data(info, label, ch_data)
            pbar.update(1)
            pbar.set_postfix_str(file)
