import os
import yaml
import sqlite3
import numpy as np
from tqdm import tqdm
import scipy.io as sio
from random import randint


class DataInfo:
    def __init__(self, dataset: str, channel: int, rpm: int, freq: int):
        self.dataset = dataset
        self.channel = channel
        self.rpm = rpm
        self.freq = freq


class DataLabel:
    def __init__(self, fault: int | list[int], severity: int):
        fault_list = [0, 0, 0, 0]
        if isinstance(fault, list):
            for f in fault:
                fault_list[f] = severity
        else:
            fault_list[fault] = severity
        if severity == 0:
            fault_list[0] = 1
        if sum(fault_list) == 0:
            fault_list[0] = 1
        self.fault = fault_list


def get_dir(dataset: str):
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)['open_dataset'][dataset]


def get_file_num(path):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                count += 1
    return count


def check_raw_db_file():
    with open('config.yaml', 'r', encoding="utf-8") as f:
        file_path = yaml.load(f, Loader=yaml.FullLoader)['dataset']['raw_path']
    if not os.path.exists(file_path):
        open(file_path, 'w').close()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE data (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset TEXT,
            channel INTEGER,
            rpm INTEGER,
            freq INTEGER,
            FN INTEGER,
            FI INTEGER,
            FB INTEGER,
            FO INTEGER,
            data BLOB
        )''')
        conn.commit()
    else:
        conn = sqlite3.connect(file_path)
    return conn


def get_fault_id(norm: int, inner: int, ball: int, outer: int):
    if norm:
        return 0
    else:
        fault_num = 0
        if inner:
            fault_num += 1
        if ball:
            fault_num += 1
        if outer:
            fault_num += 1
        if fault_num > 1:
            return 10
        else:
            if inner:
                return inner
            elif ball:
                return ball + 3
            else:
                return outer + 6


def get_stats_dict():
    with open('config.yaml', 'r', encoding="utf-8") as f:
        dataset_names = yaml.load(f, Loader=yaml.FullLoader)['open_dataset'].keys()
    tmp_data = []
    for _ in range(11):
        tmp_data.append(0)
    res_dict = {}
    for dataset_name in dataset_names:
        res_dict[dataset_name.upper()] = tmp_data[:]
    return res_dict


class RawDataset:
    def __init__(self):
        self.conn = check_raw_db_file()

    def close(self):
        self.conn.close()

    def add_data(self, info: DataInfo, label: DataLabel, data: np.ndarray):
        cursor = self.conn.cursor()
        data = np.float32(data).tobytes()
        cursor.execute('INSERT INTO data (dataset, channel, rpm, freq, FN, FI, FB, FO, data) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (
                           info.dataset, info.channel, info.rpm, info.freq, label.fault[0],
                           label.fault[1], label.fault[2], label.fault[3], data))
        self.conn.commit()

    def clear_data(self, dataset: str):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM data WHERE dataset = ?', (dataset,))
        self.conn.commit()

    def get_data_num(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM data')
        num = cursor.fetchone()[0]
        return num

    def get_data(self, _id: int):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM data WHERE _id = ?', (_id,))
        data = cursor.fetchone()
        data = np.frombuffer(data[-1], dtype=np.float32)
        return data

    def get_sample(self, _id: int):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM data WHERE _id = ?', (_id,))
        data = cursor.fetchone()
        info = DataInfo(data[1], data[2], data[3], data[4])
        data = np.frombuffer(data[-1], dtype=np.float32)
        return info, data

    def stats(self):
        record_num = self.get_data_num()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM data')
        stats_dict_num = get_stats_dict()
        stats_dict_time = get_stats_dict()
        with tqdm(total=record_num) as tbar:
            for i in range(record_num):
                row = cursor.fetchone()
                data = np.frombuffer(row[-1], dtype=np.float32)
                data_point_num = len(data)
                freq = row[4]
                data_time = data_point_num / freq
                fault_id = get_fault_id(row[5], row[6], row[7], row[8])
                stats_dict_num[row[1]][fault_id] += 1
                stats_dict_time[row[1]][fault_id] += data_time
                tbar.update(1)
        return stats_dict_num, stats_dict_time


def check_split_db_file():
    with open('config.yaml', 'r', encoding="utf-8") as f:
        file_path = yaml.load(f, Loader=yaml.FullLoader)['dataset']['split_path']
    if not os.path.exists(file_path):
        open(file_path, 'w').close()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE data (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            rand_id INTEGER KEY,
            dataset TEXT,
            channel INTEGER,
            FN INTEGER,
            FI INTEGER,
            FB INTEGER,
            FO INTEGER,
            rpm INTEGER,
            freq INTEGER,
            avg REAL,
            std REAL,
            vib BLOB,
            spec BLOB
        )''')
        conn.commit()
    else:
        conn = sqlite3.connect(file_path)
    return conn


def split_raw_dataset():
    conn = check_split_db_file()
    cur = conn.cursor()
    raw_dataset = RawDataset()
    raw_conn = raw_dataset.conn
    raw_cur = raw_conn.cursor()

    raw_record_num = raw_dataset.get_data_num()
    raw_cur.execute('SELECT * FROM data')
    with tqdm(total=raw_record_num) as tbar:
        for _ in range(raw_record_num):
            raw_row = raw_cur.fetchone()
            raw_vib = np.frombuffer(raw_row[-1], dtype=np.float32)
            raw_data_point_num = len(raw_vib)

            dataset = raw_row[1]
            channel = raw_row[2]
            rpm = raw_row[3]
            freq = raw_row[4]

            fn = raw_row[5]
            fi = raw_row[6]
            fb = raw_row[7]
            fo = raw_row[8]

            split_num = raw_data_point_num // freq
            for i in range(split_num):
                split_data = raw_vib[i * freq: (i + 1) * freq]
                std = split_data.std()
                avg = split_data.mean()
                split_data = (split_data - avg) / std

                spec = np.fft.fft(split_data, norm='ortho')
                spec = np.abs(spec[:freq//2])
                spec = spec.astype(np.float32)

                rand_id = randint(0, int(1e7-1))
                cur.execute('INSERT INTO data (rand_id, dataset, channel, FN, FI, FB, FO, rpm, freq, avg, std, vib, '
                            'spec) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (rand_id, dataset, channel, fn, fi, fb, fo, rpm, freq, float(avg), float(std), split_data.tobytes(), spec.tobytes(),))

            tbar.update(1)
            conn.commit()

    conn.close()
    raw_conn.close()
