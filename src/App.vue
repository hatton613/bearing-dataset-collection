<script setup lang="ts">
import {reactive, type Ref, ref} from 'vue'
import {getData, getDataList, getDatasetInfo} from '@/utils'
import {getInstanceByDom, init} from "echarts";

const datasetInfo: Ref<DatasetInfo> = ref({})
const recordTable: Ref<DataRecord[]> = ref([])

const specMode: Ref<boolean> = ref(true)

const datasetSelect: Ref<string> = ref('')
const datasetOption: Ref<string[]> = ref([])

const channelSelect: Ref<string> = ref('0')
const channelOption: Ref<string[]> = ref([])

const faultTypeSelect: Ref<string> = ref('normal')
const severitySelect: Ref<string> = ref('any')

const splitLineInterval:Ref<number> = ref(0)
const splitLineCenter:Ref<number> = ref(0)

const chartLoading: Ref<boolean> = ref(false)
const dataLoading: Ref<boolean> = ref(true)
const skipNum: Ref<number> = ref(5)

let buttonText = reactive<Record<number, string>>({});

const faultTypeOption: FilterOption = {
  any: "任意",
  normal: "正常",
  inner: "内圈",
  ball: "滚珠",
  outer: "外圈"
}

const severityOption: FilterOption = {
  any: "任意",
  normal: "正常",
  slight: "轻微",
  moderate: "一般",
  severe: "严重"
}

const tagColors = {
  'normal': '#ffffff',
  'inner': ['#d4fdff', '#c5f4ff', '#a8e0ff'],
  'ball': ['#c7f9cc', '#c6fed3', '#99ffd0'],
  'outer': ['#ffdfe7', '#ffbfcf', '#ffafc3'],
}

const emptyData:ChartData[] = []

const chartOption = {
  grid: {
    top: '10%',
    left: '5%',
    right: '8%',
    bottom: '10%'
  },
  toolbox: {
    feature: {
      dataZoom: {
        yAxisIndex: 'none'
      },
      restore: {},
      saveAsImage: {},
      myFull: {
        show: true,
        title: '全屏显示',
        icon: 'path://M480,112H128V480H480V112z M480,480H128V112H480V480z M400,352L352,352L352,400L400,400z M400,424L352,424L352,400L400,400z',
        onclick: function () {
          const chartDom = document.getElementById("data-chart")
          if (!document.fullscreenElement && chartDom) {
            chartDom.requestFullscreen().catch(err => {
              alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
            });
          } else {
            document.exitFullscreen();
          }
        }
      }
    }
  },
  dataZoom: [{
    type: 'inside',
    xAxisIndex: [0],
    start: 0,
    end: 100
  }, {
    type: 'slider',
    show: true,
    xAxisIndex: [0],
    start: 0,
    end: 100,
  }],
  tooltip: {
    trigger: 'axis',
  },
  xAxis: {
    type: 'value',
    name: '频率(Hz)',
    min: 'dataMin', // 自动计算最小值
    max: 'dataMax', // 自动计算最大值
  },
  yAxis: {
    type: 'value',
    name: '幅值',
  },
  series: emptyData
}

function updateChartAxisName() {
  chartOption.xAxis.name = specMode.value ? '频率(Hz)' : '时间(s)'
}

function getChart(){
  const container = document.getElementById('data-chart')
  if (!container) return
  const existingChart = getInstanceByDom(container)
  if (existingChart) return existingChart
  return init(container)
}

function updateDataList() {
  dataLoading.value = true
  getDataList(datasetSelect.value, channelSelect.value, faultTypeSelect.value, severitySelect.value).then(data => {
    recordTable.value = data
    dataLoading.value = false
  })
}

function updateChannelOption() {
  channelOption.value =['any']
  for (let i = 0; i < datasetInfo.value[datasetSelect.value]; i++) {
    channelOption.value.push(String(i))
  }
  updateDataList()
}

function updateDatasetInfo() {
  getDatasetInfo().then((data) => {
    datasetInfo.value = data
    datasetOption.value = Object.keys(data)
    datasetOption.value.push('any')
    datasetSelect.value = datasetOption.value[0]
    updateChannelOption()
  })
}

function addChartLine(recordId: number, freq: number, name:string){
  chartLoading.value = true
  const chart = getChart()
  const seriesIndex = chartOption.series.findIndex(function(s) {
    return s.id === recordId
  })
  if (seriesIndex === -1) {
    getData(recordId, specMode.value).then((res:number[])=>{
      const seriesData = []

      if (specMode.value) {
        const freqUnit = freq / 2 / res.length
        let maxFreqValue = 0
        for (let i = 0; i < res.length; i=i+skipNum.value) {
          const value = res[i]
          const freq = i * freqUnit
          if (value > maxFreqValue) {
            maxFreqValue = value
            splitLineCenter.value = freq
            splitLineInterval.value = freq
          }
          seriesData.push([freq, value])
        }
        updateSplitLine()
        chartOption.series.push({
          id: recordId,
          name: name,
          type: 'line',
          data: seriesData,
          symbol: 'none',
          markPoint: {
            data: [
              {
                coord: [splitLineCenter.value, maxFreqValue],
                symbol: "pin",
                symbolSize: 25,
                animation: true,
                label: {
                  show: true,
                  formatter: splitLineCenter.value.toFixed(1) + 'Hz',
                },
              },
            ],
          },
        })
      } else {
        const timeUnit = 1 / res.length
        for (let i = 0; i < res.length; i=i+skipNum.value) {
          seriesData.push([timeUnit*i, res[i]])
        }
        chartOption.series.push({
          id: recordId,
          name: '',
          type: 'line',
          data: seriesData,
          symbol: 'none',
        })
      }
      chart?.setOption(chartOption)
      buttonText[recordId] = '删除'
      chartLoading.value = false
    })
  } else {
    chartOption.series.splice(seriesIndex, 1);
    buttonText[recordId] = '绘制'
    chart?.setOption(chartOption, true)
    chartLoading.value = false
  }
}

function clearChart() {
  const chart = getChart()
  chartOption.series = []
  updateChartAxisName()
  chart?.setOption(chartOption, true)
  Object.keys(buttonText).forEach(key => {
    delete buttonText[key as unknown as number];
  });
}

document.addEventListener('fullscreenchange', function() {
  const chartDom = document.getElementById("data-chart")
  if (chartDom) {
    if (document.fullscreenElement) {
      chartDom.classList.add('fullscreen');
    } else {
      chartDom.classList.remove('fullscreen');
    }
    const chartElement = getChart()
    chartElement?.resize()
  }
})

function updateSplitLine() {
  chartOption.series = chartOption.series.filter(item => item.name != "splitLine")
  const lineData = []
  let nowData = splitLineCenter.value
  while (true) {
    nowData -= splitLineInterval.value
    if (nowData <= 0) {
      break
    } else {
      lineData.push({xAxis: nowData})
    }
  }
  nowData = splitLineCenter.value
  while (true) {
    if (nowData >= 10000) {
      break
    } else {
      lineData.push({xAxis: nowData})
    }
    nowData += splitLineInterval.value
  }

  chartOption.series.push({
    id: 0,
    name: "splitLine",
    type: "line",
    symbol: "none",
    data: [[0]],
    markLine: {
      animation: false,
      data: lineData
    }
  })
  const chartElement = getChart()
  chartElement?.setOption(chartOption, true)
}

function getRecordName(record: DataRecord) {
  let name = record.dataset
  if (record.fn) {
    name += '正常'
  } else {
    if (record.fi) {
      name += ('-' + Object.values(severityOption)[record.fi + 1] + '内圈')
    }
    if (record.fb) {
      name += ('-' + Object.values(severityOption)[record.fb + 1] + '滚珠')
    }
    if (record.fo) {
      name += ('-' + Object.values(severityOption)[record.fo + 1] + '外圈')
    }
  }
  return name
}

updateDatasetInfo()
clearChart()

</script>

<template>
<div class="open-dataset-page">
  <div class="left-panel">
    <el-container v-loading="chartLoading" id="data-chart" />
    <div class="control-panel">

      <div class="data-panel">
        <div class="control-option">
          <span class="control-option-label">数据集:</span>
          <el-select v-model="datasetSelect" @change="updateChannelOption">
            <el-option
              v-for="item in datasetOption"
              :key="item"
              :label="item === 'any' ? '任意' : item "
              :value="item"
            />
          </el-select>
        </div>
        <div class="control-option">
          <span class="control-option-label">通道选择:</span>
          <el-select v-model="channelSelect" @change="updateDataList">
            <el-option
              v-for="item in channelOption"
              :key="item"
              :label="item === 'any' ? '任意' : item "
              :value="item"
            />
          </el-select>
        </div>
        <div class="control-option">
          <span class="control-option-label">故障筛选:</span>
          <el-select v-model="faultTypeSelect" @change="updateDataList">
            <el-option
              v-for="item in Object.keys(faultTypeOption)"
              :key="item"
              :label="faultTypeOption[item]"
              :value="item"
            />
          </el-select>
        </div>
        <div class="control-option">
          <span class="control-option-label">程度筛选:</span>
          <el-select v-model="severitySelect" @change="updateDataList">
            <el-option
              v-for="item in Object.keys(severityOption)"
              :key="item"
              :label="severityOption[item]"
              :value="item"
            />
          </el-select>
        </div>
      </div>

      <div class="chart-panel">

        <div class="chart-option">
          <el-switch v-model="specMode" inactive-text="时域模式" active-text="频谱模式" @change="clearChart"></el-switch>
          <el-button @click="clearChart" style="margin-left: 5.4vw">清除画布</el-button>
        </div>

        <div class="chart-option">
          <span class="freq-slider-name">
            特征频率:
          </span>
          <el-slider v-model="splitLineCenter" :min="0" :max="5000" show-input @change="updateSplitLine" class="freq-slider"/>
        </div>

        <div class="chart-option">
          <div class="freq-slider-name">
            标尺间隔:
          </div>
          <el-slider v-model="splitLineInterval" :min="0" :max="5000" show-input @change="updateSplitLine" class="freq-slider"/>
        </div>

        <div class="chart-option">
          <div class="freq-slider-name">
            下采样倍率:
          </div>
          <el-slider v-model="skipNum" :min="1" :max="10" show-input class="freq-slider"/>
        </div>

      </div>
    </div>
  </div>

  <el-table :data="recordTable" class="dataTable" v-loading="dataLoading">
    <el-table-column property="id" label="ID" align="center" />
    <el-table-column property="dataset" label="数据集" align="center" />
    <el-table-column property="channel" label="通道编号" align="center" />
    <el-table-column property="freq" label="采样频率(Hz)" align="center" />
    <el-table-column property="rpm" label="转速(rpm)" align="center" />
    <el-table-column label="标签" align="center">
      <template #default="{row}">
        <el-tag v-if="row.fn" :color="tagColors.normal" class="label-tag">正常</el-tag>
        <el-tag v-if="row.fi" :color="tagColors.inner[row.fi - 1]" class="label-tag">{{Object.values(severityOption)[row.fi + 1]}}内圈</el-tag>
        <el-tag v-if="row.fb" :color="tagColors.ball[row.fb - 1]" class="label-tag">{{Object.values(severityOption)[row.fb + 1]}}滚珠</el-tag>
        <el-tag v-if="row.fo" :color="tagColors.outer[row.fo - 1]" class="label-tag">{{Object.values(severityOption)[row.fo + 1]}}外圈</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作" align="center">
      <template #default="{row}">
        <el-button v-if="buttonText[row.id]"
                   @click="addChartLine(row.id, row.freq, getRecordName(row))"
                   :type="buttonText[row.id] === '绘制' ? 'info' : 'danger'"
                   size="small">{{buttonText[row.id]}}</el-button>
        <el-button v-else @click="addChartLine(row.id, row.freq, getRecordName(row))" size="small">绘制</el-button>
      </template>
    </el-table-column>
  </el-table>
</div>
</template>

<style scoped>

.open-dataset-page {
  display: flex;
}

.left-panel {
  width: 60vw;
}

#data-chart {
  width: 100%;
  height: 70vh;
}.fullscreen {
   width: 100%;
   height: 100%;
   background-color: white; /* 设置背景为白色 */
 }

.dataTable {
  width: 40vw;
  height: 98vh;
}

.label-tag {
  color: #000;
}

.control-panel{
  width: 100%;
  display: flex;
  justify-content: center;
}

.control-option{
  display: flex;
  width: 14vw;
  align-items: center;
  margin-top: 1vh;
}

.control-option-label {
  width: 8vw;
}

.chart-panel{
  display: flex;
  flex-direction: column;
  margin-left: 3vw;
}

.freq-slider-name {
  width: 6vw;
}


.chart-option {
  display: flex;
  width: 20vw;
  align-items: center;
  margin-top: 1vh;
}
</style>
