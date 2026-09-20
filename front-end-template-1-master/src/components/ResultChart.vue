<template>
  <div ref="chart" :style="{ width: '100%', height: height + 'px' }"></div>
</template>

<script>
export default {
  name: 'ResultChart',
  props: {
    option: { type: Object, required: true },
    height: { type: Number, default: 280 }
  },
  data() {
    return { chart: null }
  },
  mounted() {
    this.render()
  },
  watch: {
    option: {
      deep: true,
      handler() { this.render() }
    }
  },
  methods: {
    render() {
      if (!this.option) return
      if (!this.chart) this.chart = this.$echarts.init(this.$refs.chart)
      this.chart.setOption(this.option, true)
    }
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
  }
}
</script>
