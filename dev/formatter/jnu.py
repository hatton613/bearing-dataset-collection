from .utils import *

root_dir = get_dir("jnu")
sub_dirs = ["Ball", "Inner", "Outer", "Normal"]
freq = 100000


def decode_filename(file_name):
    severity = 2
    if "N" in file_name:
        fault = 0
        severity = 0
    elif "OB" in file_name:
        fault = 3
    elif "IB" in file_name:
        fault = 1
    else:
        fault = 2
    if "1500" in file_name:
        rpm = 1500
    elif "1000" in file_name:
        rpm = 1000
    else:
        rpm = 500
    return rpm, fault, severity


def add_jnu(database: RawDataset):
    all_file_num = get_file_num(root_dir)
    with tqdm(total=all_file_num) as pbar:
        pbar.update(2)
        for sub_dir in sub_dirs:
            file_list = os.listdir(os.path.join(root_dir, sub_dir))
            for file in file_list:
                rpm, fault, severity = decode_filename(file)
                file_path = os.path.join(root_dir, sub_dir, file)
                with open(file_path, "r") as f:
                    raw_data = f.readlines()
                    file_data = []
                    for line in raw_data:
                        line = line.strip()
                        line = line.strip(",")
                        line = line.split(",")
                        if len(line) != 5:
                            continue
                        line = [float(x) for x in line]
                        file_data.append(line)
                    file_data = np.array(file_data, dtype=np.float32)
                    chs = file_data.shape[1]
                    for ch_id in range(chs):
                        ch_data = file_data[:, ch_id]
                        info = DataInfo("JNU", ch_id, rpm, freq)
                        label = DataLabel(fault, severity)
                        database.add_data(info, label, ch_data)
                pbar.update(1)
                pbar.set_postfix_str(file)

