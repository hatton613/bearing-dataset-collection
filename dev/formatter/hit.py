from .utils import *

root_dir = get_dir("hit")
file_list = os.listdir(root_dir)

freq = 20000


def add_hit(database: RawDataset):
    with tqdm(total=len(file_list)) as pbar:
        for file in file_list:
            if file.endswith(".npy"):
                all_data = np.load(os.path.join(root_dir, file))
                for sample in all_data:
                    l_rpm = sample[6][0]
                    h_rpm = sample[6][1]
                    rpm = int(h_rpm - l_rpm)
                    fault = int(sample[7][0])
                    if fault == 2:
                        fault = 3
                    label = DataLabel(fault, 2)
                    for channel in range(4):
                        info = DataInfo("HIT", channel, rpm, freq)
                        channel_data = sample[channel+2]
                        database.add_data(info, label, channel_data)
            pbar.update(1)
            pbar.set_postfix_str(file)