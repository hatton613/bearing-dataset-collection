from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml

from query import get_dataset_info, get_data_list, get_data, collect_open_dataset_info


class GetDataListReq(BaseModel):
    dataset: str
    channel: str
    fault_type: str
    severity: str


class GetDataReq(BaseModel):
    id: int
    type: str


def start_server():
    with open('config.yaml', 'r', encoding='utf-8') as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)['server']

    app = FastAPI()
    # noinspection PyTypeChecker
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg['origins'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get('/get-info')
    def get_info_route():
        return get_dataset_info()

    @app.post('/get-data-list')
    def get_data_list_route(x: GetDataListReq):
        return get_data_list(x.dataset, x.channel, x.fault_type, x.severity)

    @app.post('/get-data')
    def get_data_list_route(x: GetDataReq):
        return get_data(x.id, x.type)

    uvicorn.run(app, host=cfg['host'], port=cfg['port'])


if __name__ == '__main__':
    collect_open_dataset_info()
    start_server()
