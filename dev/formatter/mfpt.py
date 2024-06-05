from .utils import *

root_dir = get_dir("mfpt")


fault_dict = {
    "1 - Three Baseline Conditions": 0,
    "2 - Three Outer Race Fault Conditions": 3,
    "3 - Seven More Outer Race Fault Conditions": 3,
    "4 - Seven Inner Race Fault Conditions": 1,
}

severity = 2


def add_mfpt(database: RawDataset):
    for sub_dir in fault_dict.keys():
        file_list = os.listdir(os.path.join(root_dir, sub_dir))
        with tqdm(total=len(file_list)) as pbar:
            for file in file_list:
                if file.endswith(".mat"):
                    all_data = sio.loadmat(os.path.join(root_dir, sub_dir, file))
                    fault = fault_dict[sub_dir]
                    freq = int(all_data["bearing"]["sr"][0][0][0][0])
                    data = all_data["bearing"]["gs"][0][0].flatten()
                    rpm = int(all_data["bearing"]["rate"][0][0][0][0] * 60)
                    info = DataInfo("MFPT", 0, rpm, freq)
                    label = DataLabel(fault, severity)
                    database.add_data(info, label, data)
                pbar.update(1)
                pbar.set_postfix_str(f'{sub_dir}:{file}')
