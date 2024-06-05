import axios from "axios";

const backendUrl:string = "http://localhost:24680";

export async function getDatasetInfo() {
  return axios.get(backendUrl + "/get-info").then((res) => {
    return res.data
  })
}

export async function getDataList(dataset:string, channel:string, faultType:string, severity:string) {
  return axios.post(backendUrl + "/get-data-list", {
    dataset: dataset,
    channel: channel,
    fault_type: faultType,
    severity: severity,
  }).then((res) => {
    return res.data
  })
}

export async function getData(id:number, specMode:boolean) {
  return axios.post(backendUrl + "/get-data", {
    id: id,
    type: specMode ? "spec" : "vib",
  }).then((res) => {
    return res.data
  })
}