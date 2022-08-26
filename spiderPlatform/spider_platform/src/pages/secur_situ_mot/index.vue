<template>
  <div class="new-page" :style="`min-height: ${pageMinHeight}px`">
    <el-row>
      <el-col :span="12">
        <el-card class="box-card">
          <div id="emotion" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <div id="keywords" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import {METHOD, request} from '@/utils/request';
import {SEC_MONITOR} from '@/services/api';
import * as echarts from 'echarts';

export default {
  name: "index",
  data() {
    return {
      emotionDom: null,
      emotionChart: null,
      emotionOption: null,
      keywordsDom: null,
      keywordsChart: null,
      keywordsOption: null
    }
  },
  mounted() {
    this.emotionDom = document.getElementById('emotion');
    this.emotionChart = echarts.init(this.emotionDom);
    this.keywordsDom = document.getElementById('keywords');
    this.keywordsChart = echarts.init(this.keywordsDom);

    this.emotionOption = {
      title: {
        text: '情感走势'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: []
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      toolbox: {
        feature: {
          saveAsImage: {}
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: true,
        data: []
      },
      yAxis: {
        type: 'value'
      },
      series: []
    };
    this.emotionOption && this.emotionChart.setOption(this.emotionOption);

    this.keywordsOption = {
      title: {
        text: '关键词走势'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: []
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      toolbox: {
        feature: {
          saveAsImage: {}
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: true,
        data: []
      },
      yAxis: {
        type: 'value'
      },
      series: []
    };
    this.keywordsOption && this.keywordsChart.setOption(this.keywordsOption);

    const that = this;
    request(SEC_MONITOR, METHOD.POST, {
      "project_name": "default",
      "mode": "day"
    }).then(function (data) {
      let emotionData = [];
      let emotionLegend = [];
      let emotions = data["emotion"];
      for (let key in emotions) {
        emotionLegend.push(key);
        emotionData.push(
            {
              name: key,
              type: 'line',
              smooth: true,
              data: emotions[key]
            },
        );
        that.emotionOption.legend.data = emotionLegend;
        that.emotionOption.series = emotionData;
      }

      let keywordData = [];
      let keywordLegend = [];
      let keywords = data["keywords"];
      for (let key in keywords) {
        keywordLegend.push(key);
        keywordData.push(
            {
              name: key,
              type: 'line',
              smooth: true,
              data: keywords[key]
            },
        );
        that.keywordsOption.legend.data = keywordLegend;
        that.keywordsOption.series = keywordData;
      }
    });
  }
}
</script>

<style scoped>
.box-card {
  min-height: 700px;
}

.chart {
  width: 765px;
  height: 658px;
}
</style>
