from .utils import *

root_dir = get_dir("ims")
sub_dirs = ["1st_test", "2nd_test", "3rd_test"]

freq = 20000
rpm = 2000


def get_fault_label(t_name, ch_id, t_id):
    if t_name == "1st_test":
        if ch_id in [0, 1, 2, 3]:
            return 0, 0
        elif ch_id in [4, 5]:
            if t_id < 1750:
                return 1, 1
            else:
                return 1, 2
        else:
            if t_id < 1500:
                return 1, 1
            elif t_id < 2000:
                return 1, 2
            else:
                return 1, 3
    elif t_name == "2nd_test":
        if ch_id == 0:
            if t_id < 500:
                return 0, 0
            elif t_id < 700:
                return 3, 1
            elif t_id < 900:
                return 3, 2
            else:
                return 3, 3
        else:
            return 0, 0
    else:
        if t_id < 6150:
            return 0, 0
        else:
            if ch_id == 2:
                if t_id < 6250:
                    return 3, 2
                else:
                    return 3, 3
            else:
                if t_id < 6275:
                    return 3, 1
                else:
                    return 3, 2


def add_ims(database: RawDataset):
    for sub_dir in sub_dirs:
        file_list = os.listdir(os.path.join(root_dir, sub_dir))
        file_list.sort()
        with tqdm(total=len(file_list)) as pbar:
            for t_id in range(len(file_list)):
                file = file_list[t_id]
                file_path = os.path.join(root_dir, sub_dir, file)
                file_data = np.loadtxt(file_path, dtype=np.float32)
                chs = file_data.shape[1]

                for ch_id in range(chs):
                    ch_data = file_data[:, ch_id]
                    info = DataInfo("IMS", ch_id, rpm, freq)
                    fault, severity = get_fault_label(sub_dir, ch_id, t_id)
                    label = DataLabel(fault, severity)
                    database.add_data(info, label, ch_data)

                pbar.update(1)
                pbar.set_postfix_str(f'{sub_dir}:{file}')