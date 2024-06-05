import yaml
import sqlite3
from tqdm import tqdm
import numpy as np


def collect_open_dataset_info():
    with open('config.yaml', 'r', encoding='utf-8') as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)
        dataset_path = cfg['dataset']['path']
    dataset_info = {}
    with sqlite3.connect(dataset_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT count(*) FROM data')
        total_num = cur.fetchone()[0]

        cur.execute('SELECT dataset, channel FROM data')
        with tqdm(total=total_num) as pbar:
            for _ in range(total_num):
                row = cur.fetchone()
                if row[0] not in dataset_info:
                    dataset_info[row[0]] = row[1] + 1
                else:
                    if dataset_info[row[0]] < row[1] + 1:
                        dataset_info[row[0]] = row[1] + 1
                pbar.update(1)
    print(dataset_info)
    cfg['open_dataset'] = dataset_info
    with open('config.yaml', 'w', encoding='utf-8') as config_file:
        yaml.dump(cfg, config_file, allow_unicode=True)


def get_dataset_info():
    with open('config.yaml', 'r', encoding='utf-8') as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)['open_dataset']


def sqlite_filter_formater(filter_str: str, key_name: str):
    if filter_str == 'any':
        return ''
    else:
        return f'{key_name} = {filter_str}'


def sqlite_fault_filter(fault_type: str, severity: str):
    severity_list = ['normal', 'slight', 'moderate', 'severe']
    fault_dict = {
        'inner': 'FI',
        'ball': 'FB',
        'outer': 'FO'
    }
    if fault_type == 'any':
        if severity == 'any':
            return ''
        elif severity == 'normal':
            return 'FN = 1'
        else:
            severity_id = severity_list.index(severity)
            return f'(FI = {severity_id} OR FB = {severity_id} OR FO = {severity_id})'
    elif fault_type == 'normal':
        return 'FN = 1'
    else:
        if severity == 'any':
            return f'{fault_dict[fault_type]} > 0'
        else:
            severity_id = severity_list.index(severity)
            return f'{fault_dict[fault_type]} = {severity_id}'


def get_data_list(dataset: str, channel: str, fault_type: str, severity: str):
    if fault_type not in ['any', 'normal', 'inner', 'ball', 'outer']:
        raise KeyError('no such fault type')
    if severity not in ['any', 'normal', 'slight', 'moderate', 'severe']:
        raise KeyError('no such severity')
    dataset_filter = sqlite_filter_formater(f'"{dataset}"', 'dataset')
    channel_filter = sqlite_filter_formater(channel, 'channel')
    fault_filter = sqlite_fault_filter(fault_type, severity)

    filter_list = [s for s in [dataset_filter, channel_filter, fault_filter] if s]
    if filter_list:
        filter_str = 'WHERE ' + ' AND '.join(filter_list)
    else:
        filter_str = ''

    with open('config.yaml', 'r', encoding='utf-8') as config_file:
        dataset_path = yaml.load(config_file, Loader=yaml.FullLoader)['dataset']['path']
    with sqlite3.connect(dataset_path) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT _id, dataset, channel, FN, FI, FB, FO, rpm, freq FROM data {filter_str}')
        filtered_data = cur.fetchall()
        res = []
        for row in filtered_data:
            res.append({
                'id': row[0],
                'dataset': row[1],
                'channel': row[2],
                'fn': row[3],
                'fi': row[4],
                'fb': row[5],
                'fo': row[6],
                'rpm': row[7],
                'freq': row[8]
            })
        return res


def get_data(record_id: int, data_type: str):
    with open('config.yaml', 'r', encoding='utf-8') as config_file:
        dataset_path = yaml.load(config_file, Loader=yaml.FullLoader)['dataset']['path']
    with sqlite3.connect(dataset_path) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT {data_type} FROM data WHERE _id = {record_id}')
        res = cur.fetchone()[0]
        res = np.frombuffer(res, dtype=np.float32).tolist()
        return res
