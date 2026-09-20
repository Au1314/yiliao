<template>
  <div class="home">
    <dv-loading v-if="loading">Loading...</dv-loading>
    <dv-border-box-10 v-else>
      <div class="naca">
          <div class="index-header" style="margin-top: 5px">
            <div>
              <dv-decoration-10
                style="width: 450px; height: 1px; margin-bottom: 45px"
              />
              <dv-decoration-8
                style="width: 180px; height: 50px"
                :color="['#568aea', '#000000']"
              />
              <div
                style="
                  width: 150px;
                  color: #eeecec;
                  font-size: 18px;
                  padding: 0 15px;
                  font-weight: bold;
                "
              >
                可视化化平台
              </div>
              <dv-decoration-8
                :reverse="true"
                style="width: 180px; height: 50px"
                :color="['#568aea', '#000000']"
              />
              <dv-decoration-10
                style="
                  width: 450px;
                  height: 1px;
                  transform: rotateY(180deg);
                  margin-bottom: 45px;
                "
              />
            </div>
            <dv-decoration-5
              style="width: 10%; height: 20px"
              :color="['#568aea', '#000000']"
            />
          </div>

          <div class="index-content">
            <div class="left">
              <div class="left-1" style="">
                <dv-border-box-12
                  ><div style="padding: 5px">
                    <div class="title" style="margin-top: 5px">
                      各年龄段患病占比
                    </div>

                    <div
                      ref="firstMain"
                      style="width: 100%; height: 120px"
                    ></div></div
                ></dv-border-box-12>
                <dv-border-box-8
                  ><div style="padding: 5px; padding-bottom: 30px">
                    <div class="title" style="margin-top: 1px">
                      疾病类型分布
                    </div>
                    <dv-capsule-chart
                      :config="config1"
                      style="width: 80%; height: 110px"
                    /></div
                ></dv-border-box-8>

                <dv-border-box-3
                  ><div style="padding: 15px">
                    <div class="title" style="margin-top: 5px">病例列表</div>
                    <!-- <div ref="timeZhou" style="width: 100%; height: 350px"></div> -->
                    <div class="row_list" style="">
                      <ul
                        class="cases_list"
                        style="width: 100%; height: 159px; overflow: auto"
                      >
                        <li style="font-size: 15px">
                          <div>编号</div>
                          <div>求诊类型</div>
                          <div>性别</div>
                          <div>年龄</div>
                          <div>身高</div>
                          <div>体重</div>
                          <div>患病时长</div>
                        </li>
                        <li v-for="cases in casesData">
                          <div>{{ cases[0] }}</div>
                          <div>{{ cases[1] }}</div>
                          <div>{{ cases[2] }}</div>
                          <div>{{ cases[3] }}</div>
                          <div>{{ cases[10] }}</div>
                          <div>{{ cases[11] }}</div>
                          <div>{{ cases[12] }}</div>
                        </li>
                      </ul>
                    </div>
                  </div></dv-border-box-3
                >
              </div>
            </div>
            <div class="cents">
              <div class="filter-bar">
                <span v-if="filterType" class="filter-label">
                  当前筛选：<em>{{ filterType }}</em>
                  <span class="filter-reset" @click="resetFilter">× 重置</span>
                </span>
                <span v-else class="filter-hint">
                  点击右侧关键词云图中的疾病名称，可联动筛选下方图表
                </span>
              </div>
              <div class="above">
                <div class="aboveOne">
                  <div style="padding: 15px">
                    <div class="title">疾病数据信息</div>
                    <div
                      style="
                        display: flex;
                        flex-direction: column;
                        width: 100%;
                        height: 120px;
                        color: #eeecec;
                      "
                    >
                      <div style="display: flex; flex: 1">
                        <dv-decoration-11
                          style="height: 60px; text-align: center"
                          ><div style="flex: 1">
                            数据数量:{{ centerData.maxNum }}
                          </div></dv-decoration-11
                        >
                        <dv-decoration-11
                          style="height: 60px; text-align: center"
                          ><div style="flex: 1">
                            最多疾病类型:{{ centerData.maxType }}
                          </div></dv-decoration-11
                        >
                        <dv-decoration-11
                          style="height: 60px; text-align: center"
                          ><div style="flex: 1">
                            求诊最多科室:{{ centerData.maxDep }}
                          </div></dv-decoration-11
                        >
                      </div>
                      <div style="display: flex; flex: 1">
                        <dv-decoration-11
                          style="height: 60px; text-align: center"
                          ><div style="flex: 1">
                            最大患者年龄:{{ centerData.maxAge }}
                          </div></dv-decoration-11
                        >
                        <dv-decoration-11
                          style="height: 60px; text-align: center"
                          ><div style="flex: 1">
                            最小患者年龄:{{ centerData.minAge }}
                          </div></dv-decoration-11
                        >
                        <dv-decoration-11
                          style="height: 60px; text-align: center"
                          ><div style="flex: 1">
                            热门医院:{{ centerData.maxHos }}
                          </div></dv-decoration-11
                        >
                      </div>
                    </div>
                  </div>
                  <div style="padding: 15px">
                    <div class="title" style="margin-top: -30px">
                      男女性别患病对比
                    </div>
                    <div class="content">
                      <dv-active-ring-chart
                        :config="config3"
                        style="width: 150px; height: 100px"
                      />
                      <dv-water-level-pond
                        :config="config4"
                        style="width: 100px; height: 90px"
                      />
                      <dv-active-ring-chart
                        :config="config3"
                        style="width: 150px; height: 100px"
                      />
                    </div>
                  </div>
                </div>
                <div class="aboveTwo">
                  <dv-border-box-9 :color="['#568aea']">
                    <div style="padding: 15px">
                      <div class="title" style="margin-top: 5px">
                        医院科室环形图
                      </div>
                      <div
                        id="secondMian"
                        style="width: 100%; height: 110px"
                      ></div></div
                  ></dv-border-box-9>
                  <dv-border-box-1
                    ><div style="padding: 5px">
                      <div class="title" style="margin-top: 5px">
                        疾病关键词云图
                      </div>
                      <div
                        ref="thirdMain"
                        style="width: 400px; height: 90px"
                      ></div></div
                  ></dv-border-box-1>
                </div>
              </div>
              <div class="below">
                <dv-border-box-13 class="below-item">
                  <div style="padding: 7px">
                    <div class="title" style="margin-top: 5px">
                      患病身高体重平均数图
                    </div>
                    <div
                      ref="lastMain"
                      style="width: 100%; height: 200px; margin-top: 25px"
                    ></div>
                  </div>
                </dv-border-box-13>
                <dv-border-box-13 class="below-item">
                  <div style="padding: 7px">
                    <div class="title" style="margin-top: 5px">
                      患病时长分布
                    </div>
                    <div
                      ref="illDurationMain"
                      style="width: 100%; height: 200px; margin-top: 25px"
                    ></div>
                  </div>
                </dv-border-box-13>
                <dv-border-box-13 class="below-item">
                  <div style="padding: 7px">
                    <div class="title" style="margin-top: 5px">
                      过敏史分布
                    </div>
                    <div
                      ref="allergyMain"
                      style="width: 100%; height: 200px; margin-top: 25px"
                    ></div>
                  </div>
                </dv-border-box-13>
              </div>
            </div>
          </div>
        </div>
      </dv-border-box-10>
  </div>
</template>

<script>
export default {
  name: "Index",
  data() {
    return {
      loading: true,
      pieIndex: 0,
      pieTimer: null,
      pieData: [],
      casesData: [],
      centerData: {
        maxNum: "",
        maxType: "",
        maxDep: "",
        maxHos: "",
        maxAge: "",
        minAge: "",
      },
      wordData:"",
      circleData: "",
      lastData:{

      },
      illDurationData: [],
      allergyData: [],
      filterType: "",
      config1: {},
      config2: {
        lineWidth: 20,
        radius: "50%",
        activeRadius: "60%",
        activeTimeGap: 2000,
        digitalFlopStyle: {
          fontSize: 13,
        },
        data: [{ name: "demo", value: 1 }],
      },
      config3: {
        lineWidth: 20,
        radius: "50%",
        activeRadius: "60%",
        activeTimeGap: 2000,
        digitalFlopStyle: {
          fontSize: 13,
        },
        data: [],
      },
      config4: {
        data: [],
        shape: "roundRect",
      },
    };
  },
  methods: {
    initPie() {
      const chartDom = this.$refs.firstMain;
      this._pieChart = this.$echarts.init(chartDom);
      this._pieChart.setOption({
        tooltip: {
          trigger: "item",
          formatter: "{a} <br/>{b}:{c} ({d}%)",
        },
        toolbox: {
          show: true,
        },
        calculable: true,
        legend: {
          orient: "vertical",
          icon: "circle",
          left: 0,
          x: "center",
          data: this.pieData.map((item) => item.name),
          textStyle: {
            color: "#fff",
          },
        },
        series: [
          {
            name: "年龄占比",
            type: "pie",
            radius: [20, 50],
            roseType: "area",
            center: ["50%", "55%"],
            label: {
              show: true,
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                label: {
                  show: true,
                  fontWeight: "bold",
                },
              },
            },
            data: this.pieData,
          },
        ],
      });
    },
    highlightPie() {
      if (!this._pieChart || !this.pieData.length) return;
      this._pieChart.dispatchAction({
        type: "downplay",
        seriesIndex: 0,
        dataIndex: this.pieIndex,
      });
      this.pieIndex = (this.pieIndex + 1) % this.pieData.length;
      this._pieChart.dispatchAction({
        type: "highlight",
        seriesIndex: 0,
        dataIndex: this.pieIndex,
      });
    },
   getSeriesData(data = this.circleData){
    const series = [];
    (data || []).forEach((item,index)=>{
      if(index<5){
         series.push({
          name: item.name,
          type: "pie",
          clockWise: false,
          hoverAnimation: false,
          radius: [73 - index * 15 + "%", 68 - index * 15 + "%"],
          center: ["50%", "50%"],
          label: {
            show: false,
          },
          data: [
            {
              value: item.value,
              name: item.name,
            },
            {
              value: 3,
              itemStyle: {
                color: "rgba(0,0,0,0)",
                borderWidth: 0,
              },
              tooltip: {
                show: false,
              },
              hoverAnimation: false,
            },
          ],
        });

       
      }
      });
  
    return series;
   },
   randomColor(){
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgb(${r},${g},${b})`
   },
    initWord() {
      const chartDom = this.$refs.thirdMain;
      this._wordChart = this.$echarts.init(chartDom);
      this._wordChart.setOption({
        series: {
          type: "wordCloud",
          sizeRange: [20, 40],
          gridSize: 0,
          rotationRange: [0, 0],
          layoutAnimation: true,
          textStyle: {
            color: () => this.randomColor(),
          },
          emphasis: {
            textStyle: {
              fontWeight: "bold",
              color: "#fff",
            },
          },
          data: this.wordData,
        },
      });
      this._wordChart.on("click", (params) => {
        this.applyFilter(params.name);
      });
    },
    initCircle() {
      const chartDom = document.getElementById("secondMian");
      this._circleChart = this.$echarts.init(chartDom);
      this._circleChart.setOption({
        legend: {
          show: true,
          icon: "circle",
          top: "8%",
          left: "10%",
          data: this.circleData.map((item) => item.name),
          width: -5,
          itemWidth: 10,
          itemHeight: 10,
          itemGap: 6,
          textStyle: {
            fontSize: 12,
            lineHeight: 5,
            color: "#ffffff",
          },
        },
        tooltip: {
          show: true,
          trigger: "item",
          formatter: "{b}<br>{c}({d}%)",
        },
        yAxis: [
          {
            type: "category",
            inverse: true,
            axisLine: {
              show: false,
            },
          },
        ],
        xAxis: [
          {
            show: true,
          },
        ],
        series: this.getSeriesData(),
      });
    },
    initLast() {
      const chartDom = this.$refs.lastMain;
      this._lastChart = this.$echarts.init(chartDom);
      this._lastChart.setOption({
        tooltip: {
          trigger: "axis",
          backgroundColor: "rgba(255,255,255,0.1)",
          axisPointer: {
            type: "shadow",
            label: {
              show: true,
              backgroundColor: "#7B7DDC",
            },
          },
        },
        dataZoom: [
          {
            type: "slider",
            start: 0,
            end: 80,
            show: false,
          },
        ],
        legend: {
          data: ["身高", "体重"],
          textStyle: {
            color: "#B4B4B4",
          },
          top: "0%",
        },
        grid: {
          x: "8%",
          width: "85%",
          height: "87%",
          y: "4%",
        },
        xAxis: {
          data: this.lastData.xData,
          axisLine: {
            lineStyle: {
              color: "#B4B4B4",
            },
          },
          axisLabel: {
            show: true,
            interval: 0,
          },
          axisTick: {
            show: false,
          },
        },
        yAxis: [
          {
            splitLine: { show: false },
            axisLine: {
              lineStyle: {
                color: "#B4B4B4",
              },
            },
            axisLabel: {
              formatter: "{value} ",
            },
          },
          {
            splitLine: { show: false },
            axisLine: {
              lineStyle: {
                color: "#B4B4B4",
              },
            },
            axisLabel: {
              formatter: "{value} ",
            },
          },
        ],
        series: [
          {
            name: "身高",
            type: "line",
            smooth: true,
            showAllSymbol: true,
            symbol: "emptyCircle",
            symbolSize: 8,
            yAxisIndex: 1,
            itemStyle: {
              normal: {
                barBorderRadius: 5,
                color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: "#5C4033" },
                  { offset: 1, color: "#FAEBD7" },
                ]),
              },
            },
            data: this.lastData.y1Data,
          },
          {
            name: "体重",
            type: "bar",
            barWidth: "60%",
            itemStyle: {
              normal: {
                barBorderRadius: 5,
                color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: "#082e53" },
                  { offset: 1, color: "white" },
                ]),
              },
            },
            data: this.lastData.y2Data,
          },
        ],
      });
    },
    initIllDuration() {
      const chartDom = this.$refs.illDurationMain;
      this._illDurationChart = this.$echarts.init(chartDom);
      this._illDurationChart.setOption({
        tooltip: { trigger: "axis" },
        grid: { left: "12%", right: "5%", top: "15%", bottom: "10%" },
        xAxis: {
          type: "category",
          data: this.illDurationData.map((i) => i.name),
          axisLine: { lineStyle: { color: "#B4B4B4" } },
          axisTick: { show: false },
          axisLabel: { color: "#fff" },
        },
        yAxis: {
          type: "value",
          axisLine: { lineStyle: { color: "#B4B4B4" } },
          splitLine: { lineStyle: { color: "rgba(255,255,255,0.1)" } },
          axisLabel: { color: "#fff" },
        },
        series: [
          {
            type: "bar",
            barWidth: "50%",
            data: this.illDurationData.map((i) => i.value),
            itemStyle: {
              borderRadius: [4, 4, 0, 0],
              color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "#568aea" },
                { offset: 1, color: "#082e53" },
              ]),
            },
            label: { show: true, position: "top", color: "#fff" },
          },
        ],
      });
    },
    initAllergy() {
      const chartDom = this.$refs.allergyMain;
      this._allergyChart = this.$echarts.init(chartDom);
      this._allergyChart.setOption({
        tooltip: { trigger: "axis" },
        grid: { left: "12%", right: "5%", top: "15%", bottom: "10%" },
        xAxis: {
          type: "category",
          data: this.allergyData.map((i) => i.name),
          axisLine: { lineStyle: { color: "#B4B4B4" } },
          axisTick: { show: false },
          axisLabel: { color: "#fff", interval: 0 },
        },
        yAxis: {
          type: "value",
          axisLine: { lineStyle: { color: "#B4B4B4" } },
          splitLine: { lineStyle: { color: "rgba(255,255,255,0.1)" } },
          axisLabel: { color: "#fff" },
        },
        series: [
          {
            type: "bar",
            barWidth: "50%",
            data: this.allergyData.map((i) => i.value),
            itemStyle: {
              borderRadius: [4, 4, 0, 0],
              color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "#3f96a5" },
                { offset: 1, color: "#082e53" },
              ]),
            },
            label: { show: true, position: "top", color: "#fff" },
          },
        ],
      });
    },
    classifyDuration(v) {
      v = String(v).trim();
      if (v === "" || v === "无") return "无";
      if (v.indexOf("半年") >= 0) return v.indexOf("大于") >= 0 ? "大于半年" : "半年内";
      if (v.indexOf("大于") >= 0 || v.indexOf("年") >= 0) return "大于半年";
      if (v.indexOf("月") >= 0) return "一月内";
      if (["周", "天", "日", "小时"].some((k) => v.indexOf(k) >= 0)) return "一周内";
      return null;
    },
    computeAgeData(cases) {
      const buckets = {
        "0-10岁": 0, "10-20岁": 0, "20-30岁": 0, "30-40岁": 0,
        "40-50岁": 0, "50-60岁": 0, "60岁以上": 0,
      };
      cases.forEach((c) => {
        const age = parseInt(c[3]);
        if (age < 10) buckets["0-10岁"]++;
        else if (age < 20) buckets["10-20岁"]++;
        else if (age < 30) buckets["20-30岁"]++;
        else if (age < 40) buckets["30-40岁"]++;
        else if (age < 50) buckets["40-50岁"]++;
        else if (age < 60) buckets["50-60岁"]++;
        else buckets["60岁以上"]++;
      });
      return Object.keys(buckets).map((k) => ({ name: k, value: buckets[k] }));
    },
    computeGenderData(cases) {
      let boy = 0, girl = 0;
      const boyDic = {}, girlDic = {};
      cases.forEach((c) => {
        if (c[2] === "男") { boy++; boyDic[c[1]] = (boyDic[c[1]] || 0) + 1; }
        else if (c[2] === "女") { girl++; girlDic[c[1]] = (girlDic[c[1]] || 0) + 1; }
      });
      const boyRatio = Math.round((boy / cases.length) * 100);
      const girlRatio = Math.round((girl / cases.length) * 100);
      return {
        boyList: Object.keys(boyDic).map((k) => ({ name: k, value: boyDic[k] })),
        girlList: Object.keys(girlDic).map((k) => ({ name: k, value: girlDic[k] })),
        ratioData: [girlRatio, boyRatio],
      };
    },
    computeDeptData(cases) {
      const dic = {};
      cases.forEach((c) => { dic[c[8]] = (dic[c[8]] || 0) + 1; });
      return Object.keys(dic).map((k) => ({ name: k, value: dic[k] }))
        .sort((a, b) => b.value - a.value);
    },
    computeDurationData(cases) {
      const order = ["一周内", "一月内", "半年内", "大于半年", "无"];
      const dic = {};
      order.forEach((k) => (dic[k] = 0));
      cases.forEach((c) => {
        const k = this.classifyDuration(c[12]);
        if (k) dic[k]++;
      });
      return order.map((k) => ({ name: k, value: dic[k] }));
    },
    computeAllergyData(cases) {
      const dic = {};
      cases.forEach((c) => {
        const v = String(c[13]).trim();
        let key;
        if (["", "无", "暂无信息", "否认", "忘记了"].indexOf(v) >= 0) key = "无过敏史";
        else if (v.indexOf("青霉素") >= 0 && v.indexOf("头孢") >= 0) key = "青霉素+头孢类";
        else if (v.indexOf("青霉素") >= 0) key = "青霉素类";
        else if (v.indexOf("头孢") >= 0) key = "头孢类";
        else key = "其他";
        dic[key] = (dic[key] || 0) + 1;
      });
      return Object.keys(dic).map((k) => ({ name: k, value: dic[k] }))
        .sort((a, b) => b.value - a.value);
    },
    applyFilter(type) {
      this.filterType = type;
      const cases = type ? this.casesData.filter((c) => c[1] === type) : this.casesData;
      if (!cases.length) return;

      const ageData = this.computeAgeData(cases);
      this._pieChart.setOption({
        legend: { data: ageData.map((i) => i.name) },
        series: [{ data: ageData }],
      });

      const g = this.computeGenderData(cases);
      this.config3 = Object.assign({}, this.config3, { data: g.girlList });
      this.config4 = Object.assign({}, this.config4, { data: g.ratioData });

      const deptData = this.computeDeptData(cases);
      this._circleChart.setOption({
        legend: { data: deptData.map((i) => i.name) },
        series: this.getSeriesData(deptData),
      });

      this._illDurationChart.setOption({
        series: [{ data: this.computeDurationData(cases).map((i) => i.value) }],
      });
      this._allergyChart.setOption({
        series: [{ data: this.computeAllergyData(cases).map((i) => i.value) }],
      });
    },
    resetFilter() {
      this.applyFilter("");
    },
  },
  async mounted() {
    const res = await this.$http.get("/getHomeData");
    this.pieData = res.data.pieData;
    this.config1 = { data: res.data.configOne, showValue: true };
    this.casesData = res.data.casesData;
    this.centerData.maxNum = res.data.maxNum;
    this.centerData.maxType = res.data.maxType;
    this.centerData.maxDep = res.data.maxDep;
    this.centerData.maxHos = res.data.maxHos;
    this.centerData.maxAge = res.data.maxAge;
    this.centerData.minAge = res.data.minAge;
    this.circleData = res.data.circleData;
    this.wordData = res.data.wordData;
    this.lastData = res.data.lastData;
    this.illDurationData = res.data.illDurationData;
    this.allergyData = res.data.allergyData;
    this.config2.data = res.data.boyList;
    this.config3.data = res.data.girlList;
    this.config4.data = res.data.ratioData;
    this.loading = false;

    this.$nextTick(() => {
      this.initPie();
      this.initWord();
      this.initCircle();
      this.initLast();
      this.initIllDuration();
      this.initAllergy();
      this.pieTimer = setInterval(this.highlightPie, 3000);
    });
  },
  beforeDestroy() {
    if (this.pieTimer) clearInterval(this.pieTimer);
    [this._pieChart, this._wordChart, this._circleChart, this._lastChart, this._illDurationChart, this._allergyChart].forEach((chart) => {
      if (chart) chart.dispose();
    });
  },
};
</script>

<style lang="less" scoped>
.loading {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}
.cent-1-content {
  padding: 20px;
  display: flex;
}
.right-content {
  margin-left: 30px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
}
.right-content div {
  display: flex;
  font-size: 15px;
  align-items: center;
}
.cents {
  display: flex;
  flex-direction: column;
}
.above {
  display: flex;
}
.below {
  display: flex;
}
.below-item {
  flex: 1;
}
.filter-bar {
  height: 26px;
  line-height: 26px;
  text-align: center;
  font-size: 13px;
}
.filter-hint {
  color: #8a8a8a;
}
.filter-label {
  color: #eeecec;
}
.filter-label em {
  color: #568aea;
  font-style: normal;
  font-weight: bold;
  margin: 0 4px;
}
.filter-reset {
  margin-left: 10px;
  cursor: pointer;
  color: #ff6b6b;
  border: 1px solid #ff6b6b;
  border-radius: 3px;
  padding: 0 6px;
}
.filter-reset:hover {
  background: rgba(255, 107, 107, 0.15);
}
.aboveOne {
  display: flex;
  flex-direction: column;
}
.aboveTwo {
  display: flex;
  flex-direction: column;
}
.cent {
  width: 850px;
  height: 300px;
}

.cent-1 {
  margin: 10px;
  color: aliceblue;
  width: 500px;
  height: 220px;
  /* background-color: rgb(26, 26, 133); */
}

.left {
  display: flex;
  flex-direction: column;
}

.left-1 {
  margin: 15px;
  color: aliceblue;
  width: 550px;
  display: flex;
  flex-direction: column;
}
.left-2 {
  margin: 15px;
  color: aliceblue;
  width: 530px;
  display: flex;
  flex-direction: column;
}

.naca {
  // padding: 35px 15px 0 15px;
  box-sizing: border-box;
  width: 100%;
  // height: 40rem;
  display: flex;
  flex-direction: column;
}
.naca .index-header {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.naca .index-header div {
  display: flex;
  justify-content: center;
  align-items: center;
}
.naca .index-content {
  display: flex;
  justify-content: center;
  align-items: center;
}
.bg {
  width: 100%;
  height: 45rem;
  background-color: black;
  position: relative;
}
.title {
  color: #3f96a5;
  font-size: 18px;
  margin-top: -20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-weight: bold;
}
.content {
  display: flex;
  align-items: center;
}
.content-word {
  width: 140px;
  height: 130px;
  background: #11193e;
  border-radius: 40px;
  border: 1px solid #3d3d3d;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.content-word-item {
  margin-left: 19px;
  margin-bottom: 10px;
  img {
    width: 20px;
    height: 20px;
  }
}
.content-word-item-title {
  font-size: 18px;
}
.content-word-item-content {
  margin-top: 5px;

  display: flex;
  align-items: center;
}
.row_list {
  list-style: none;
}
.cases_list::-webkit-scrollbar {
  display: none;
}

.cases_list li {
  display: grid;
  -ms-grid-columns: 30px 110px 60px 60px 60px 50px 100px;
  grid-template-columns: 30px 110px 60px 60px 60px 50px 100px;
  cursor: pointer;
  margin-left: 23px;
  text-align: center;
  line-height: 30px;
  color: rgb(238, 236, 236);
}
.list_time {
  height: 30px;
  overflow: auto;
}
.list_time::-webkit-scrollbar {
  display: none;
}
</style>