interface DataRecord {
  id: number
  dataset: string
  channel: string
  fn: number
  fi: number
  fb: number
  fo: number
  rpm: number
  freq: number
}

interface DatasetInfo {
  [key: string]: number
}

interface FilterOption {
  [key: string]: string
}

interface ChartData {
  id: number
  name: string
  type: string
  symbol: string
  data: number[][]
  [key: string]: any
}