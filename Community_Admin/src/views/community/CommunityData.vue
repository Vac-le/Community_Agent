<template>
  <div class="community-data-container">
    <!-- 天气预报区域 -->
    <div class="weather-section">
      <!-- 页面标题 -->
      <div class="page-header">
        <h2 class="page-title">社区天气概览</h2>
        <el-button 
          type="primary" 
          icon="el-icon-refresh" 
          size="small" 
          @click="loadWeather"
          :loading="weatherLoading">
          刷新天气
        </el-button>
      </div>

      <!-- 今日天气卡片 -->
      <el-card class="today-weather-card" v-if="todayWeather" shadow="hover">
        <div class="weather-header">
          <div class="location-info">
            <i class="el-icon-location"></i>
            <span class="city-name">{{ cityInfo.cityName }}</span>
            <span class="province-name">{{ cityInfo.provinceName }}</span>
          </div>
          <div class="update-time">
            <i class="el-icon-time"></i>
            <span>{{ currentTime }}</span>
          </div>
        </div>

        <div class="today-weather-content">
          <div class="weather-main">
            <div class="temp-area">
              <span class="weather-icon">{{ getWeatherIcon(todayWeather.conditionIdDay) }}</span>
              <span class="temp-now">{{ todayWeather.tempDay }}°</span>
            </div>
            <div class="weather-info">
              <div class="condition-text">{{ todayWeather.conditionDay }}</div>
              <div class="temp-range">{{ todayWeather.tempNight }}° ~ {{ todayWeather.tempDay }}°</div>
            </div>
          </div>

          <div class="weather-details">
            <div class="detail-item" v-if="todayWeather.windDirDay">
              <i class="el-icon-wind-power"></i>
              <span>{{ todayWeather.windDirDay }} {{ todayWeather.windLevelDay }}级</span>
            </div>
            <div class="detail-item" v-if="todayWeather.humidity">
              <i class="el-icon-help"></i>
              <span>湿度 {{ todayWeather.humidity }}%</span>
            </div>
            <div class="detail-item" v-if="todayWeather.pop">
              <i class="el-icon-drizzle"></i>
              <span>降水 {{ todayWeather.pop }}%</span>
            </div>
            <div class="detail-item" v-if="todayWeather.uvi">
              <i class="el-icon-sunny"></i>
              <span>紫外线 {{ todayWeather.uvi }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 加载状态 -->
      <el-card v-if="weatherLoading" class="loading-card">
        <div class="loading-content">
          <i class="el-icon-loading"></i>
          <span>加载天气数据中...</span>
        </div>
      </el-card>

      <!-- 未来半个月天气预报 -->
      <el-card class="forecast-card" v-if="forecastList.length > 0" shadow="hover">
        <div slot="header" class="forecast-header">
          <span class="forecast-title">
            <i class="el-icon-date"></i>
            未来半个月天气预报
          </span>
          <el-tag size="small" type="info">{{ forecastList.length }}天</el-tag>
        </div>

        <div class="forecast-grid">
          <div 
            class="forecast-item" 
            v-for="(item, index) in forecastList" 
            :key="index">
            <div class="forecast-date">{{ formatDate(item.predictDate || item.date) }}</div>
            <div class="forecast-icon">{{ getWeatherIcon(item.conditionIdDay) }}</div>
            <div class="forecast-condition">{{ item.conditionDay }}</div>
            <div class="forecast-temp">
              <span class="temp-high">{{ item.tempDay }}°</span>
              <span class="temp-divider">/</span>
              <span class="temp-low">{{ item.tempNight }}°</span>
            </div>
            <div class="forecast-wind" v-if="item.windDirDay">
              <i class="el-icon-wind-power"></i>
              <span>{{ item.windLevelDay }}级</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 无数据提示 -->
      <el-card v-if="!todayWeather && !weatherLoading" class="no-data-card">
        <el-empty description="暂无天气数据">
          <el-button type="primary" @click="loadWeather">加载天气</el-button>
        </el-empty>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      weatherLoading: false,
      cityInfo: {
        cityName: '',
        provinceName: ''
      },
      todayWeather: null,
      forecastList: [],
      currentTime: ''
    };
  },
  mounted() {
    this.loadWeather();
    this.updateCurrentTime();
  },
  methods: {
    // 更新当前时间
    updateCurrentTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      this.currentTime = `${year}-${month}-${day} ${hours}:${minutes}`;
    },

    // 加载天气数据
    async loadWeather() {
      this.weatherLoading = true;
      try {
        const resp = await this.$http.post(`/api/weatherCtl/weather`);
        
        if (resp.data.code == 200) {
          let weatherData = resp.data.data;
          
          // 如果weatherData是字符串，先JSON.parse
          if (typeof weatherData === 'string') {
            try {
              weatherData = JSON.parse(weatherData);
            } catch (e) {
              console.error('JSON解析失败:', e);
              this.$message.error('天气数据格式错误');
              return;
            }
          }
          
          // 判断是否是嵌套结构
          if (weatherData && typeof weatherData === 'object' && weatherData.code !== undefined) {
            if (weatherData.code == 0 && weatherData.data) {
              weatherData = weatherData.data;
            }
          }
          
          // 设置城市信息
          if (weatherData && weatherData.city) {
            this.cityInfo = {
              cityName: weatherData.city.name || '未知城市',
              provinceName: weatherData.city.pname || ''
            };
          }
          
          // 今日天气和未来天气（获取15天）
          if (weatherData && weatherData.forecast && Array.isArray(weatherData.forecast) && weatherData.forecast.length > 0) {
            this.todayWeather = weatherData.forecast[0];
            // 获取未来15天（排除今天）
            this.forecastList = weatherData.forecast.slice(1, 16);
          }
          
          this.$message.success('天气数据加载成功');
        } else {
          this.$message.error(resp.data.msg || '获取天气失败');
        }
      } catch (error) {
        console.error('获取天气失败:', error);
        this.$message.error('天气服务异常，请稍后重试');
      } finally {
        this.weatherLoading = false;
      }
    },
    
    // 格式化日期
    formatDate(dateStr) {
      if (!dateStr) return '';
      
      const date = new Date(dateStr);
      const today = new Date();
      const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);
      
      if (date.toDateString() === tomorrow.toDateString()) {
        return '明天';
      }
      
      const afterTomorrow = new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000);
      if (date.toDateString() === afterTomorrow.toDateString()) {
        return '后天';
      }
      
      const month = date.getMonth() + 1;
      const day = date.getDate();
      const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
      const weekDay = weekDays[date.getDay()];
      
      return `${month}月${day}日 ${weekDay}`;
    },
    
    // 获取天气图标
    getWeatherIcon(conditionId) {
      const iconMap = {
        '0': '☀️',   // 晴
        '1': '🌤️',   // 多云
        '2': '☁️',   // 阴
        '3': '🌧️',   // 阵雨
        '4': '⛈️',   // 雷阵雨
        '5': '🌨️',   // 雨夹雪
        '6': '🌨️',   // 雨雪
        '7': '🌧️',   // 小雨
        '8': '🌧️',   // 中雨
        '9': '🌧️',   // 大雨
        '10': '🌧️',  // 暴雨
        '11': '🌧️',  // 大暴雨
        '12': '🌧️',  // 特大暴雨
        '13': '❄️',  // 阵雪
        '14': '❄️',  // 小雪
        '15': '❄️',  // 中雪
        '16': '❄️',  // 大雪
        '17': '❄️',  // 暴雪
        '18': '🌫️',  // 雾
        '31': '☁️'   // 多云
      };
      return iconMap[String(conditionId)] || '☁️';
    }
  }
};
</script>

<style scoped>
.community-data-container {
  min-height: 100vh;
  background: transparent;
  padding: 20px;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}

/* 天气区域 */
.weather-section {
  max-width: 1400px;
  margin: 0 auto;
}

/* 今日天气卡片 */
.today-weather-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 20px;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.location-info i {
  color: #409eff;
  font-size: 20px;
}

.city-name {
  font-size: 20px;
  font-weight: 600;
  color: #f1f5f9;
}

.province-name {
  font-size: 14px;
  color: #94a3b8;
  margin-left: 4px;
}

.update-time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 14px;
}

.update-time i {
  font-size: 16px;
}

.today-weather-content {
  padding: 10px 0;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-bottom: 30px;
}

.temp-area {
  display: flex;
  align-items: center;
  gap: 20px;
}

.weather-icon {
  font-size: 80px;
  line-height: 1;
}

.temp-now {
  font-size: 72px;
  font-weight: 300;
  color: #f1f5f9;
  line-height: 1;
}

.weather-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.condition-text {
  font-size: 28px;
  font-weight: 600;
  color: #f1f5f9;
}

.temp-range {
  font-size: 18px;
  color: #94a3b8;
}

.weather-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
  background: rgba(255,255,255,0.04);
  border-radius: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #94a3b8;
}

.detail-item i {
  font-size: 20px;
  color: #409eff;
}

/* 未来天气预报卡片 */
.forecast-card {
  border-radius: 12px;
  overflow: hidden;
}

.forecast-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forecast-title {
  font-size: 18px;
  font-weight: 600;
  color: #f1f5f9;
  display: flex;
  align-items: center;
  gap: 8px;
}

.forecast-title i {
  color: #409eff;
}

.forecast-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.forecast-item {
  background: rgba(255,255,255,0.05);
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.forecast-item:hover {
  background: rgba(59,130,246,0.12);
  border-color: #60a5fa;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(59,130,246,0.2);
}

.forecast-date {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 600;
  margin-bottom: 12px;
}

.forecast-icon {
  font-size: 48px;
  margin: 12px 0;
}

.forecast-condition {
  font-size: 15px;
  color: #e2e8f0;
  font-weight: 600;
  margin: 10px 0;
}

.forecast-temp {
  font-size: 16px;
  margin: 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.temp-high {
  color: #f56c6c;
  font-weight: 600;
}

.temp-divider {
  color: #64748b;
}

.temp-low {
  color: #409eff;
  font-weight: 600;
}

.forecast-wind {
  font-size: 13px;
  color: #64748b;
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.forecast-wind i {
  font-size: 14px;
}

/* 加载状态 */
.loading-card {
  border-radius: 12px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: 16px;
  color: #64748b;
  font-size: 16px;
}

.loading-content i {
  font-size: 36px;
}

/* 无数据状态 */
.no-data-card {
  border-radius: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .weather-main {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .weather-info {
    align-items: center;
  }
  
  .forecast-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }
  
  .weather-details {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
