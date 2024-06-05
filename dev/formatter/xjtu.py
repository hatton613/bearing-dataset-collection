from .utils import *

root_dir = get_dir("xjtu")

freq = 25600

rpm_dict = {
    "35Hz12kN": 2100,
    "37.5Hz11kN": 2250,
    "40Hz10kN": 2400,
}

fault_dict = {
    "Bearing1_1": 3,
    "Bearing1_2": 3,
    "Bearing1_3": 3,
    "Bearing1_4": 2,
    "Bearing1_5": [1, 3],
    "Bearing2_1": 1,
    "Bearing2_2": 3,
    "Bearing2_3": 2,
    "Bearing2_4": 3,
    "Bearing2_5": 3,
    "Bearing3_1": 3,
    "Bearing3_2": [1, 2, 3],
    "Bearing3_3": 1,
    "Bearing3_4": 1,
    "Bearing3_5": 3,
}


class ref_std:
    def __init__(self, ref_dir):
        ref_data = np.loadtxt(os.path.join(ref_dir, "1.csv"), delimiter=",", skiprows=1)
        self.std = np.std(ref_data)

    def get_severity(self, data):
        data_std = np.std(data)
        severity = 0
        if data_std > 4 * self.std:
            severity = 3
        elif data_std > 2.5 * self.std:
            severity = 2
        elif data_std > 1.5 * self.std:
            severity = 1
        return severity


def add_xjtu(database: RawDataset):
    file_mum = get_file_num(root_dir)
    with tqdm(total=file_mum) as pbar:
        for freq_dir, rpm in rpm_dict.items():
            sub_dir = os.path.join(root_dir, freq_dir)
            for test_dir in os.listdir(sub_dir):
                fault = fault_dict[test_dir]
                data_dir = os.path.join(sub_dir, test_dir)
                ref = ref_std(data_dir)
                for file in os.listdir(data_dir):
                    data = np.loadtxt(os.path.join(data_dir, file), delimiter=",", skiprows=1)
                    severity = ref.get_severity(data)
                    for channel in range(2):
                        data_info = DataInfo("XJTU", channel, rpm, freq)
                        data_label = DataLabel(fault, severity)
                        database.add_data(data_info, data_label, data[:, channel])
                    pbar.update(1)
                    pbar.set_postfix_str(file)
