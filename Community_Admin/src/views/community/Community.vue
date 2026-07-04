<template>
  <div class="community-container">
    <div class="screen-hero">
      <div class="hero-copy">
        <div class="hero-topbar">
          <div class="hero-brand">
            <p class="hero-kicker">SMART COMMUNITY COMMAND CENTER</p>
            <h1>社区运营数据大屏</h1>
          </div>
          <div class="hero-clock-panel">
            <div class="clock-time">{{ currentTime }}</div>
            <div class="clock-date">{{ currentDate }}</div>
          </div>
        </div>
        <p class="hero-desc">
          聚合用户、订单与服务状态，全景呈现社区后台核心运营数据，帮助管理员快速感知业务波动与处理重点。
        </p>
        <div class="hero-actions">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            <span>实时监测中</span>
          </div>
          <div class="hero-chip">指挥中心视图</div>
          <div class="hero-chip ghost">核心链路已接入</div>
          <div class="hero-chip sync-chip">
            <span class="sync-dot"></span>
            <span>最近刷新 {{ lastRefreshTime || '--:--:--' }}</span>
          </div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="visual-corner corner-left"></div>
        <div class="visual-corner corner-right"></div>
        <div class="hero-orbit">
          <div class="orbit-core">
            <span>{{ displaySummary.orderTotal }}</span>
            <p>累计工单</p>
          </div>
          <div class="orbit-ring ring-a"></div>
          <div class="orbit-ring ring-b"></div>
        </div>
        <div class="hero-stats-board">
          <div class="board-row">
            <span>活跃处理</span>
            <strong>{{ displaySummary.activeOrders }}</strong>
          </div>
          <div class="board-row">
            <span>已完成履约</span>
            <strong>{{ displaySummary.finishedOrders }}</strong>
          </div>
          <div class="board-row">
            <span>服务覆盖用户</span>
            <strong>{{ displaySummary.userTotal }}</strong>
          </div>
        </div>
      </div>
    </div>

    <div class="overview-grid">
      <div class="overview-card accent-blue">
        <div class="overview-topline">
          <span class="overview-index">01</span>
          <span class="overview-trend up">+12%</span>
        </div>
        <div class="overview-label">用户总量</div>
        <div class="overview-value">{{ displaySummary.userTotal }}</div>
        <div class="overview-meta">包含普通用户与配送人员</div>
      </div>
      <div class="overview-card accent-emerald">
        <div class="overview-topline">
          <span class="overview-index">02</span>
          <span class="overview-trend up">+8%</span>
        </div>
        <div class="overview-label">订单总量</div>
        <div class="overview-value">{{ displaySummary.orderTotal }}</div>
        <div class="overview-meta">餐饮 / 代购 / 家政累计订单</div>
      </div>
      <div class="overview-card accent-amber">
        <div class="overview-topline">
          <span class="overview-index">03</span>
          <span class="overview-trend warn">处理中</span>
        </div>
        <div class="overview-label">进行中订单</div>
        <div class="overview-value">{{ displaySummary.activeOrders }}</div>
        <div class="overview-meta">未完成订单动态追踪</div>
      </div>
      <div class="overview-card accent-violet">
        <div class="overview-topline">
          <span class="overview-index">04</span>
          <span class="overview-trend ok">稳定</span>
        </div>
        <div class="overview-label">已完成订单</div>
        <div class="overview-value">{{ displaySummary.finishedOrders }}</div>
        <div class="overview-meta">社区服务履约完成情况</div>
      </div>
    </div>

    <el-card class="panel-card trend-panel" shadow="never">
      <div slot="header" class="panel-header">
        <div class="panel-heading">
          <span class="panel-scan-dot"></span>
          <div>
            <p class="panel-eyebrow">TREND ANALYSIS</p>
            <span>订单趋势分析</span>
          </div>
        </div>
        <div class="panel-tag">近周期业务波动</div>
      </div>
      <div id="chart3" class="chart-content trend-chart"></div>
    </el-card>

    <div class="charts-row">
      <el-card class="panel-card mini-panel" shadow="never">
        <div slot="header" class="panel-header">
          <div class="panel-heading">
          <span class="panel-scan-dot"></span>
          <div>
            <p class="panel-eyebrow">USER ANALYSIS</p>
            <span>用户类型统计</span>
          </div>
        </div>
          <div class="panel-tag">结构分布</div>
        </div>
        <div id="chart1" class="chart-content"></div>
      </el-card>

      <el-card class="panel-card mini-panel" shadow="never">
        <div slot="header" class="panel-header">
          <div class="panel-heading">
          <span class="panel-scan-dot"></span>
          <div>
            <p class="panel-eyebrow">ORDER MIX</p>
            <span>订单类型分布</span>
          </div>
        </div>
          <div class="panel-tag">业务占比</div>
        </div>
        <div id="chart2" class="chart-content"></div>
      </el-card>

      <el-card class="panel-card mini-panel" shadow="never">
        <div slot="header" class="panel-header">
          <div class="panel-heading">
          <span class="panel-scan-dot"></span>
          <div>
            <p class="panel-eyebrow">STATUS MONITOR</p>
            <span>订单状态分布</span>
          </div>
        </div>
          <div class="panel-tag">履约状态</div>
        </div>
        <div id="chart4" class="chart-content"></div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      chart1Instance: null,
      chart2Instance: null,
      chart3Instance: null,
      chart4Instance: null,
      resizeHandler: null,
      clockTimer: null,
      currentTime: '',
      currentDate: '',
      lastRefreshTime: '',
      displaySummary: {
        userTotal: 0,
        orderTotal: 0,
        activeOrders: 0,
        finishedOrders: 0
      },
      summary: {
        userTotal: 0,
        orderTotal: 0,
        activeOrders: 0,
        finishedOrders: 0
      }
    };
  },
  methods: {
    formatClockTime(date) {
      const pad = (value) => String(value).padStart(2, '0');
      return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    },
    animateMetric(key, target) {
      const start = Number(this.displaySummary[key] || 0);
      const end = Number(target || 0);
      const duration = 800;
      const startTime = Date.now();
      const step = () => {
        const progress = Math.min((Date.now() - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        this.$set(this.displaySummary, key, Math.round(start + (end - start) * eased));
        if (progress < 1) {
          requestAnimationFrame(step);
        }
      };
      requestAnimationFrame(step);
    },
    updateRefreshTime() {
      this.lastRefreshTime = this.formatClockTime(new Date());
    },
    updateClock() {
      const now = new Date();
      const weekMap = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
      const pad = (value) => String(value).padStart(2, '0');
      this.currentTime = this.formatClockTime(now);
      this.currentDate = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${weekMap[now.getDay()]}`;
    },
    getAxisStyle() {
      return {
        axisLine: {
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.28)'
          }
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#9fb3c8',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.10)',
            type: 'dashed'
          }
        }
      };
    },
    getToolbox() {
      return {
        show: true,
        right: 0,
        iconStyle: {
          borderColor: '#7dd3fc'
        },
        emphasis: {
          iconStyle: {
            borderColor: '#f8fafc'
          }
        },
        feature: {
          dataView: { show: true, readOnly: true },
          magicType: { show: true, type: ['line', 'bar'] },
          restore: { show: true },
          saveAsImage: { show: true }
        }
      };
    },
    updateSummaryUsers(values) {
      const total = Array.isArray(values)
        ? values.reduce((sum, item) => sum + Number(item || 0), 0)
        : 0;
      this.summary.userTotal = total;
      this.animateMetric('userTotal', total);
      this.updateRefreshTime();
    },
    updateSummaryOrders(values) {
      const total = Array.isArray(values)
        ? values.reduce((sum, item) => sum + Number(item || 0), 0)
        : 0;
      this.summary.orderTotal = total;
      this.animateMetric('orderTotal', total);
      this.updateRefreshTime();
    },
    updateSummaryStatus(items) {
      let active = 0;
      let finished = 0;
      (items || []).forEach((item) => {
        const name = item.name || '';
        const value = Number(item.value || 0);
        if (name.indexOf('完成') !== -1 || name.indexOf('送达') !== -1) {
          finished += value;
        } else {
          active += value;
        }
      });
      this.summary.activeOrders = active;
      this.summary.finishedOrders = finished;
      this.animateMetric('activeOrders', active);
      this.animateMetric('finishedOrders', finished);
      this.updateRefreshTime();
    },

    // 用户配送统计
    userCount() {
      this.$http.get('api/communityCtl/UserSendCount').then((resp) => {
        if (resp.data.code == 200) {
          this.updateSummaryUsers(resp.data.data.y);
          this.$nextTick(() => {
            if (this.chart1Instance) {
              this.chart1Instance.dispose();
            }

            const chartDom = document.getElementById('chart1');
            if (!chartDom) return;

            this.chart1Instance = this.echarts.init(chartDom);
            const option = {
              backgroundColor: 'transparent',
              tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(15, 23, 42, 0.92)',
                borderColor: 'rgba(125, 211, 252, 0.35)',
                textStyle: {
                  color: '#e5eef8'
                },
                axisPointer: {
                  type: 'shadow'
                }
              },
              grid: {
                left: '4%',
                right: '4%',
                bottom: '2%',
                top: '12%',
                containLabel: true
              },
              toolbox: this.getToolbox(),
              xAxis: {
                type: 'category',
                data: resp.data.data.x,
                axisLine: this.getAxisStyle().axisLine,
                axisTick: this.getAxisStyle().axisTick,
                axisLabel: this.getAxisStyle().axisLabel
              },
              yAxis: {
                type: 'value',
                axisLine: this.getAxisStyle().axisLine,
                axisTick: this.getAxisStyle().axisTick,
                axisLabel: this.getAxisStyle().axisLabel,
                splitLine: this.getAxisStyle().splitLine
              },
              series: [
                {
                  name: '数量',
                  type: 'bar',
                  barWidth: 26,
                  data: resp.data.data.y,
                  itemStyle: {
                    borderRadius: [10, 10, 2, 2],
                    color: new this.echarts.graphic.LinearGradient(0, 0, 0, 1, [
                      { offset: 0, color: '#67e8f9' },
                      { offset: 1, color: '#2563eb' }
                    ])
                  },
                  label: {
                    show: true,
                    position: 'top',
                    color: '#dbeafe'
                  }
                }
              ]
            };
            this.chart1Instance.setOption(option);
          });
        }
      }).catch((error) => {
        console.error('获取用户配送统计失败:', error);
      });
    },

    // 订单类型分布
    orderCount() {
      this.$http.get('api/communityCtl/orderCount').then((resp) => {
        if (resp.data.code == 200) {
          this.updateSummaryOrders(resp.data.data.y);
          this.$nextTick(() => {
            if (this.chart2Instance) {
              this.chart2Instance.dispose();
            }

            const chartDom = document.getElementById('chart2');
            if (!chartDom) return;

            this.chart2Instance = this.echarts.init(chartDom);
            const option = {
              backgroundColor: 'transparent',
              tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(15, 23, 42, 0.92)',
                borderColor: 'rgba(52, 211, 153, 0.35)',
                textStyle: {
                  color: '#e5eef8'
                },
                axisPointer: {
                  type: 'shadow'
                }
              },
              grid: {
                left: '4%',
                right: '4%',
                bottom: '2%',
                top: '12%',
                containLabel: true
              },
              toolbox: this.getToolbox(),
              xAxis: {
                type: 'category',
                data: resp.data.data.x,
                axisLine: this.getAxisStyle().axisLine,
                axisTick: this.getAxisStyle().axisTick,
                axisLabel: this.getAxisStyle().axisLabel
              },
              yAxis: {
                type: 'value',
                axisLine: this.getAxisStyle().axisLine,
                axisTick: this.getAxisStyle().axisTick,
                axisLabel: this.getAxisStyle().axisLabel,
                splitLine: this.getAxisStyle().splitLine
              },
              series: [
                {
                  name: '数量',
                  type: 'bar',
                  barWidth: 26,
                  data: resp.data.data.y,
                  itemStyle: {
                    borderRadius: [10, 10, 2, 2],
                    color: new this.echarts.graphic.LinearGradient(0, 0, 0, 1, [
                      { offset: 0, color: '#6ee7b7' },
                      { offset: 1, color: '#0f766e' }
                    ])
                  },
                  label: {
                    show: true,
                    position: 'top',
                    color: '#d1fae5'
                  }
                }
              ]
            };
            this.chart2Instance.setOption(option);
          });
        }
      }).catch((error) => {
        console.error('获取订单统计失败:', error);
      });
    },

    // 订单状态分布
    orderStatusCount() {
      this.$http.get('api/communityCtl/orderStatusCount').then((resp) => {
        if (resp.data.code == 200) {
          this.updateSummaryStatus(resp.data.data);
          this.$nextTick(() => {
            if (this.chart4Instance) {
              this.chart4Instance.dispose();
            }

            const chartDom = document.getElementById('chart4');
            if (!chartDom) return;

            this.chart4Instance = this.echarts.init(chartDom);
            const option = {
              backgroundColor: 'transparent',
              tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)',
                backgroundColor: 'rgba(15, 23, 42, 0.92)',
                borderColor: 'rgba(250, 204, 21, 0.35)',
                textStyle: {
                  color: '#f8fafc'
                }
              },
              legend: {
                orient: 'horizontal',
                left: 'center',
                bottom: '2%',
                textStyle: {
                  color: '#b8c7d9',
                  fontSize: 12
                },
                itemGap: 18
              },
              series: [
                {
                  name: '订单状态',
                  type: 'pie',
                  radius: ['46%', '68%'],
                  center: ['50%', '42%'],
                  data: resp.data.data,
                  avoidLabelOverlap: true,
                  itemStyle: {
                    borderColor: '#08111f',
                    borderWidth: 4
                  },
                  label: {
                    show: true,
                    color: '#e2e8f0',
                    formatter: '{b}\n{d}%'
                  },
                  labelLine: {
                    lineStyle: {
                      color: 'rgba(148, 163, 184, 0.45)'
                    }
                  },
                  emphasis: {
                    scale: true,
                    scaleSize: 8,
                    itemStyle: {
                      shadowBlur: 18,
                      shadowColor: 'rgba(0,0,0,0.35)'
                    }
                  }
                }
              ],
              color: ['#38bdf8', '#f59e0b', '#22c55e', '#f87171']
            };
            this.chart4Instance.setOption(option);
          });
        }
      }).catch((error) => {
        console.error('获取订单状态统计失败:', error);
      });
    },

    // 订单趋势分析
    orderTrend() {
      this.$http.get('api/communityCtl/orderTrend').then((resp) => {
        if (resp && resp.data && resp.data.code == 200) {
          this.$nextTick(() => {
            if (this.chart3Instance) {
              this.chart3Instance.dispose();
            }

            const chartDom = document.getElementById('chart3');
            if (!chartDom) return;

            chartDom.style.width = '100%';
            chartDom.style.height = '420px';
            this.chart3Instance = this.echarts.init(chartDom);

            const data = resp.data.data || {};
            const dates = data.dates || [];
            const eat = data.eat || [];
            const purchase = data.purchase || [];
            const home = data.home || [];

            const option = {
              backgroundColor: 'transparent',
              tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                borderColor: 'rgba(96, 165, 250, 0.35)',
                textStyle: {
                  color: '#f8fafc'
                },
                axisPointer: {
                  type: 'line',
                  lineStyle: {
                    color: 'rgba(148, 163, 184, 0.35)'
                  }
                }
              },
              legend: {
                data: ['餐饮订单', '代购订单', '家政订单'],
                top: '0%',
                textStyle: {
                  color: '#cbd5e1'
                }
              },
              grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '14%',
                containLabel: true
              },
              toolbox: this.getToolbox(),
              xAxis: {
                type: 'category',
                data: dates,
                boundaryGap: false,
                axisLine: this.getAxisStyle().axisLine,
                axisTick: this.getAxisStyle().axisTick,
                axisLabel: this.getAxisStyle().axisLabel
              },
              yAxis: {
                type: 'value',
                axisLine: this.getAxisStyle().axisLine,
                axisTick: this.getAxisStyle().axisTick,
                axisLabel: this.getAxisStyle().axisLabel,
                splitLine: this.getAxisStyle().splitLine
              },
              series: [
                {
                  name: '餐饮订单',
                  type: 'line',
                  smooth: true,
                  symbol: 'circle',
                  symbolSize: 7,
                  data: eat,
                  itemStyle: { color: '#fb7185' },
                  lineStyle: { width: 3, color: '#fb7185' },
                  areaStyle: {
                    color: {
                      type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                      colorStops: [
                        { offset: 0, color: 'rgba(251, 113, 133, 0.34)' },
                        { offset: 1, color: 'rgba(251, 113, 133, 0.03)' }
                      ]
                    }
                  }
                },
                {
                  name: '代购订单',
                  type: 'line',
                  smooth: true,
                  symbol: 'circle',
                  symbolSize: 7,
                  data: purchase,
                  itemStyle: { color: '#60a5fa' },
                  lineStyle: { width: 3, color: '#60a5fa' },
                  areaStyle: {
                    color: {
                      type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                      colorStops: [
                        { offset: 0, color: 'rgba(96, 165, 250, 0.34)' },
                        { offset: 1, color: 'rgba(96, 165, 250, 0.03)' }
                      ]
                    }
                  }
                },
                {
                  name: '家政订单',
                  type: 'line',
                  smooth: true,
                  symbol: 'circle',
                  symbolSize: 7,
                  data: home,
                  itemStyle: { color: '#34d399' },
                  lineStyle: { width: 3, color: '#34d399' },
                  areaStyle: {
                    color: {
                      type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                      colorStops: [
                        { offset: 0, color: 'rgba(52, 211, 153, 0.34)' },
                        { offset: 1, color: 'rgba(52, 211, 153, 0.03)' }
                      ]
                    }
                  }
                }
              ]
            };

            this.chart3Instance.setOption(option);
            this.$nextTick(() => {
              if (this.chart3Instance) this.chart3Instance.resize();
            });
          });
        }
      }).catch((error) => {
        console.error('获取订单趋势失败:', error);
      });
    },

    handleResize() {
      if (this.chart1Instance) this.chart1Instance.resize();
      if (this.chart2Instance) this.chart2Instance.resize();
      if (this.chart3Instance) this.chart3Instance.resize();
      if (this.chart4Instance) this.chart4Instance.resize();
    }
  },
  mounted() {
    this.updateClock();
    this.updateRefreshTime();
    this.clockTimer = setInterval(this.updateClock, 1000);
    this.userCount();
    this.orderCount();
    this.orderStatusCount();
    this.orderTrend();

    this.resizeHandler = this.handleResize;
    window.addEventListener('resize', this.resizeHandler);
  },
  beforeDestroy() {
    if (this.chart1Instance) this.chart1Instance.dispose();
    if (this.chart2Instance) this.chart2Instance.dispose();
    if (this.chart3Instance) this.chart3Instance.dispose();
    if (this.chart4Instance) this.chart4Instance.dispose();
    if (this.clockTimer) clearInterval(this.clockTimer);

    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
    }
  }
};
</script>

<style scoped>
.community-container {
  position: relative;
  height: 100%;
  width: 100%;
  padding: 24px 28px;
  color: #e5eef8;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

.community-container::before,
.community-container::after {
  content: '';
  position: fixed;
  z-index: 0;
  pointer-events: none;
  filter: blur(70px);
  opacity: 0.45;
}

.community-container::before {
  top: 80px;
  left: 2%;
  width: 260px;
  height: 260px;
  background: rgba(56, 189, 248, 0.18);
}

.community-container::after {
  top: 180px;
  right: 5%;
  width: 300px;
  height: 300px;
  background: rgba(139, 92, 246, 0.15);
}

.screen-hero,
.overview-grid,
.panel-card {
  position: relative;
  z-index: 1;
}

.screen-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  margin-bottom: 22px;
  padding: 40px 30px;
  border-radius: 28px;
  background:
    linear-gradient(120deg, rgba(10,18,34,0.96) 0%, rgba(10,26,43,0.90) 42%, rgba(18,34,59,0.82) 100%);
  border: 1px solid rgba(56, 189, 248, 0.15);
  box-shadow: 0 24px 60px rgba(2, 8, 23, 0.45);
  overflow: hidden;
  text-align: center;
}

.screen-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 12% 16%, rgba(56,189,248,0.18), transparent 24%),
    radial-gradient(circle at 85% 22%, rgba(139,92,246,0.18), transparent 22%),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: auto, auto, 28px 28px, 28px 28px;
  opacity: 0.8;
  pointer-events: none;
}

.screen-hero::after {
  content: '';
  position: absolute;
  inset: auto 0 0 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(56,189,248,0.8), transparent);
  opacity: 0.9;
}

.hero-copy,
.hero-visual {
  position: relative;
  z-index: 1;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  align-items: center;
}

.hero-topbar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  margin-bottom: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  width: 100%;
}

.hero-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-align: center;
}

.hero-kicker {
  margin: 0 !important;
  font-size: 12px;
  letter-spacing: 0.34em;
  color: #7dd3fc;
  opacity: 0.8;
}

.hero-brand h1 {
  margin: 0 !important;
  font-size: 48px !important;
  line-height: 1.1;
  background: linear-gradient(to bottom, #fff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-clock-panel {
  min-width: 180px;
  padding: 10px 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(7,17,31,0.86), rgba(15,23,42,0.64));
  border: 1px solid rgba(125,211,252,0.16);
  text-align: right;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
}

.clock-time {
  font-size: 28px;
  line-height: 1;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #f8fbff;
}

.clock-date {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(191,204,222,0.76);
}

.hero-kicker {
  margin: 0 0 10px;
  font-size: 12px;
  letter-spacing: 0.34em;
  color: #7dd3fc;
}

.hero-copy h1 {
  margin: 0;
  font-size: 38px;
  line-height: 1.12;
  font-weight: 800;
  color: #f8fbff;
  text-shadow: 0 0 24px rgba(56,189,248,0.10);
}

.hero-desc {
  max-width: 800px;
  margin: 20px auto 0;
  color: rgba(218, 232, 245, 0.85);
  line-height: 1.8;
  font-size: 16px;
  text-align: center;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 28px;
}

.hero-badge {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.58);
  border: 1px solid rgba(125, 211, 252, 0.22);
  color: #dff8ff;
  font-size: 13px;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.16);
  color: #bae6fd;
  font-size: 12px;
}

.hero-chip.ghost {
  background: rgba(255,255,255,0.04);
  border-color: rgba(255,255,255,0.08);
  color: rgba(226,237,248,0.78);
}

.sync-chip {
  background: rgba(34,197,94,0.10);
  border-color: rgba(34,197,94,0.18);
  color: #dcfce7;
}

.sync-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 12px rgba(34,197,94,0.8);
  animation: pulseSync 1.8s ease-in-out infinite;
}

.badge-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.8);
}

.hero-visual {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 60px;
  width: 100%;
  max-width: 1000px;
}

.visual-corner {
  position: absolute;
  width: 46px;
  height: 46px;
  border-top: 2px solid rgba(125,211,252,0.68);
  top: 4px;
}

.visual-corner::after {
  content: '';
  position: absolute;
  top: -2px;
  width: 2px;
  height: 46px;
  background: rgba(125,211,252,0.68);
}

.corner-left {
  left: 4px;
}

.corner-left::after {
  left: -2px;
}

.corner-right {
  right: 4px;
}

.corner-right::after {
  right: -2px;
}

.hero-orbit {
  position: relative;
  height: 220px;
  border-radius: 28px;
  background: radial-gradient(circle at center, rgba(59,130,246,0.14), rgba(8,15,30,0.08) 55%, transparent 70%);
  overflow: hidden;
}

.orbit-core {
  position: absolute;
  inset: 50% auto auto 50%;
  transform: translate(-50%, -50%);
  width: 132px;
  height: 132px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: radial-gradient(circle at 30% 30%, rgba(125,211,252,0.24), rgba(15,23,42,0.96));
  border: 1px solid rgba(125,211,252,0.18);
  box-shadow: 0 0 36px rgba(56,189,248,0.20), inset 0 0 24px rgba(255,255,255,0.04);
}

.orbit-core span {
  font-size: 34px;
  line-height: 1;
  font-weight: 800;
  color: #f8fbff;
}

.orbit-core p {
  margin: 8px 0 0;
  font-size: 12px;
  color: rgba(226,237,248,0.72);
}

.orbit-ring {
  position: absolute;
  inset: 50% auto auto 50%;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(125,211,252,0.12);
}

.ring-a {
  width: 190px;
  height: 190px;
}

.ring-b {
  width: 248px;
  height: 248px;
  border-style: dashed;
  animation: orbitSpin 16s linear infinite;
}

.hero-stats-board {
  padding: 20px 30px;
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(56, 189, 248, 0.15);
  box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
  min-width: 300px;
}

.board-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.board-row:last-child {
  border-bottom: none;
}

.board-row span {
  font-size: 13px;
  color: rgba(203,213,225,0.72);
}

.board-row strong {
  font-size: 20px;
  color: #f8fbff;
  font-weight: 700;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 22px;
}

.overview-card {
  padding: 22px 22px 18px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(11, 21, 39, 0.95), rgba(9, 16, 30, 0.88));
  box-shadow: 0 18px 40px rgba(2, 8, 23, 0.24);
  overflow: hidden;
  position: relative;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.overview-topline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
  width: 100%;
}

.overview-index {
  font-size: 11px;
  letter-spacing: 0.24em;
  color: rgba(148,163,184,0.62);
}

.overview-trend {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 11px;
  border: 1px solid transparent;
}

.overview-trend.up {
  color: #a7f3d0;
  background: rgba(16,185,129,0.12);
  border-color: rgba(16,185,129,0.18);
}

.overview-trend.warn {
  color: #fde68a;
  background: rgba(245,158,11,0.12);
  border-color: rgba(245,158,11,0.18);
}

.overview-trend.ok {
  color: #ddd6fe;
  background: rgba(139,92,246,0.12);
  border-color: rgba(139,92,246,0.18);
}

.overview-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.05), transparent 36%);
  pointer-events: none;
}

.overview-card::after {
  content: '';
  position: absolute;
  inset: auto -10% -45% auto;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  opacity: 0.2;
  filter: blur(10px);
}

.accent-blue::after {
  background: #38bdf8;
}

.accent-emerald::after {
  background: #34d399;
}

.accent-amber::after {
  background: #f59e0b;
}

.accent-violet::after {
  background: #8b5cf6;
}

.overview-label {
  font-size: 14px;
  color: #7dd3fc;
  margin-bottom: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.overview-value {
  font-size: 42px;
  line-height: 1;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 12px;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
}

.overview-meta {
  font-size: 12px;
  color: rgba(203, 213, 225, 0.72);
}

.panel-card {
  margin-bottom: 22px;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(56, 189, 248, 0.2) !important;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(10, 18, 34, 0.94)) !important;
  box-shadow: 0 20px 50px rgba(2, 8, 23, 0.48), inset 0 0 20px rgba(56, 189, 248, 0.05) !important;
  backdrop-filter: blur(20px);
}

.panel-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 24px;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255,255,255,0.05), transparent 26%, transparent 74%, rgba(56,189,248,0.08));
}

.panel-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: -20%;
  width: 40%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(125,211,252,0.9), transparent);
  box-shadow: 0 0 18px rgba(56,189,248,0.35);
}

.panel-card >>> .el-card__header {
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.66), rgba(10, 18, 34, 0.32));
  padding: 18px 24px;
}

.panel-card >>> .el-card__body {
  padding: 20px 22px 22px;
  background: transparent;
}

.panel-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  position: relative;
  width: 100%;
}

.panel-heading {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.panel-scan-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #67e8f9;
  box-shadow: 0 0 14px rgba(103,232,249,0.85);
  animation: pulseScan 2s ease-in-out infinite;
}

.panel-eyebrow {
  margin: 0 0 6px;
  font-size: 11px;
  color: #67e8f9;
  letter-spacing: 0.24em;
}

.panel-header span {
  font-size: 18px;
  font-weight: 600;
  color: #f8fafc;
}

.panel-tag {
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.10);
  border: 1px solid rgba(56, 189, 248, 0.16);
  color: #bae6fd;
  font-size: 12px;
  white-space: nowrap;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.trend-chart {
  height: 420px;
}

.chart-content {
  height: 300px;
  position: relative;
}

.chart-content::before {
  content: '';
  position: absolute;
  inset: 10px;
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: 16px;
  pointer-events: none;
}

.chart-content::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.03), transparent 24%, transparent 76%, rgba(56,189,248,0.04));
  pointer-events: none;
}

@media (max-width: 1400px) {
  .screen-hero {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    grid-template-columns: 1fr 1fr;
    display: grid;
    align-items: stretch;
  }

  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .screen-hero {
    grid-template-columns: 1fr;
    padding: 22px 20px;
  }

  .hero-copy h1 {
    font-size: 28px;
  }

  .hero-visual {
    display: flex;
  }

  .hero-orbit {
    height: 200px;
  }

  .charts-row,
  .overview-grid {
    grid-template-columns: 1fr;
  }
}

@keyframes pulseSync {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.35);
    opacity: 1;
  }
}

@keyframes pulseScan {
  0%, 100% {
    transform: scale(1);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.4);
    opacity: 1;
  }
}

@keyframes orbitSpin {
  from {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}
</style>
