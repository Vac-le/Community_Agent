<template>
  <view class="container">
    <!-- 用户信息区域 -->
    <view class="user-section">
      <view class="user-profile">
        <image class="avatar" :src="userInfo.avatar" mode="aspectFill"></image>
        <view class="user-detail">
          <text class="username">{{userInfo.name || '用户'}}</text>
          <view class="user-tags">
            <text class="tag">ID {{userInfo.id}}</text>
            <text class="tag-dot"></text>
            <text class="tag">{{userInfo.age}}岁</text>
          </view>
        </view>
      </view>
      
      <!-- 订单数据统计 -->
      <view class="stats-row">
        <view class="stat-item" @tap="myOrders">
          <text class="stat-num">{{orderStats.allCount || 0}}</text>
          <text class="stat-text">全部</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item" @tap="myOrders">
          <text class="stat-num">{{orderStats.waitCount || 0}}</text>
          <text class="stat-text">待服务</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item" @tap="myOrders">
          <text class="stat-num">{{orderStats.completeCount || 0}}</text>
          <text class="stat-text">已完成</text>
        </view>
      </view>
    </view>

    <!-- 天气预报 -->
    <view class="weather-section" v-if="todayWeather">
      <view class="weather-header">
        <view class="location-info">
          <text class="location-icon">📍</text>
          <text class="city-name">{{cityInfo.cityName}}</text>
        </view>
      </view>
      
      <!-- 今日天气 -->
      <view class="today-weather">
        <view class="weather-main">
          <view class="temp-area">
            <text class="temp-now">{{todayWeather.tempDay}}°</text>
            <text class="temp-range">{{todayWeather.tempNight}}° ~ {{todayWeather.tempDay}}°</text>
          </view>
        <view class="weather-desc">
          <text class="condition-text">{{todayWeather.conditionDay}}</text>
          <text class="humidity-text" v-if="todayWeather.humidity">湿度 {{todayWeather.humidity}}%</text>
        </view>
      </view>
      
      <view class="weather-details">
        <view class="detail-item" v-if="todayWeather.windDirDay">
          <text class="detail-icon">💨</text>
          <text class="detail-text">{{todayWeather.windDirDay}} {{todayWeather.windLevelDay}}级</text>
        </view>
        <view class="detail-item" v-if="todayWeather.pop">
          <text class="detail-icon">💧</text>
          <text class="detail-text">降水 {{todayWeather.pop}}%</text>
        </view>
        <view class="detail-item" v-if="todayWeather.uvi">
          <text class="detail-icon">☀️</text>
          <text class="detail-text">紫外线 {{todayWeather.uvi}}</text>
        </view>
        <!-- 如果缺少这些字段，显示基本的风速信息 -->
        <view class="detail-item" v-if="!todayWeather.pop && todayWeather.windSpeedDay">
          <text class="detail-icon">💨</text>
          <text class="detail-text">风速 {{todayWeather.windSpeedDay}}m/s</text>
        </view>
      </view>
      </view>
      
      <!-- 未来天气 -->
      <scroll-view scroll-x class="forecast-scroll" v-if="forecastList.length > 0">
        <view class="forecast-list">
          <view class="forecast-item" v-for="(item, index) in forecastList" :key="index">
            <text class="forecast-date">{{formatDate(item.predictDate || item.date)}}</text>
            <text class="forecast-icon">{{getWeatherIcon(item.conditionIdDay)}}</text>
            <text class="forecast-condition">{{item.conditionDay}}</text>
            <text class="forecast-temp">{{item.tempNight}}°~{{item.tempDay}}°</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 功能菜单列表 - 从后端动态获取 -->
    <view class="menu-section" v-if="menus.length > 0">
      <view class="menu-list">
        <view class="menu-item" v-for="(menu, index) in menus" :key="index" :data-index="index" @tap="handleMenuClick">
          <text class="menu-text">{{menu.name}}</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <!-- 服务热线 -->
    <view class="menu-section">
      <view class="hotline-item" @tap="callHotline">
        <view class="hotline-left">
          <text class="hotline-label">社区服务热线</text>
          <text class="hotline-number">400-123-4567</text>
        </view>
        <text class="call-text">拨打</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <text class="logout-btn" @tap="logout">退出登录</text>
    </view>
    
    <view class="bottom-space"></view>
    <!-- 客服热线 -->
  </view>
</template>

<script>
  export default {
    data() {
      return {
        menus:[],
		userInfo: {
		  name: "",
		  gender: '',
		  age: "",
		  phone: '',
		  address: '',
		  childrenName: '',
		  childrenPhone: '',
		  avatar: '/static/logo.png'
		},
		// 订单统计数据
		orderStats: {
		  allCount: 0,
		  waitCount: 0,
		  completeCount: 0
		},
		// 天气数据
		cityInfo: {
		  cityName: '西安市'
		},
		todayWeather: null,
		forecastList: []
      }
    },
    onLoad() {
      // 页面加载时的逻辑
	  this.getInfo();
	  this.getOrderStats();
	  this.loadWeather();
    },
    onShow() {
      // 页面显示时的逻辑
	  this.getInfo();
	  this.getOrderStats();
	  this.getUserMenus();
    },
    methods: {
		async getInfo(){
			const res = await this.$myRequest({
				  	url:'user/userInfoCtl/userInfo',
				  		method: 'GET',
			});
			console.log(res.data);
			this.userInfo = res.data.data;
			this.userInfo.avatar = res.data.data.img;
		},
		async getUserMenus(){
			const res = await this.$myRequest({
				  	url:'user/userInfoCtl/menus',
				  	method: 'GET',
			});
			console.log(res.data);
			this.menus = res.data.data;
		},
	// 处理菜单点击事件
	handleMenuClick(e) {
		// 从事件对象获取索引
		const index = e.currentTarget.dataset.index;
		if (index === undefined || index === null) {
			console.error('无法获取菜单索引');
			return;
		}
		
		// 从数组中获取菜单对象
		const menu = this.menus[index];
		if (!menu) {
			console.error('菜单对象为空, index:', index);
			return;
		}
		console.log('点击的菜单:', menu);
		
		const targetUrl = menu.url;
		if (targetUrl) {
			uni.navigateTo({ 
				url: targetUrl,
				fail: (err) => {
					console.error('页面跳转失败:', err);
					uni.showToast({
						title: '页面暂未开放',
						icon: 'none'
					});
				}
			});
		} else {
			uni.showToast({
				title: '功能开发中',
				icon: 'none'
			});
		}
	},
		// 获取订单统计数据
		async getOrderStats(){
			try {
				const res = await this.$myRequest({
					url:'user/userInfoCtl/orderStats',
					method: 'GET',
				});
				console.log('订单统计数据:', res.data);
				if(res.data.code === 200) {
					this.orderStats = res.data.data;
				}
			} catch (error) {
				console.error('获取订单统计失败:', error);
				uni.showToast({
					title: '获取订单统计失败',
					icon: 'none'
				});
			}
		},
		  // 其他方法
		  logout() {
			uni.showModal({
			  title: '退出登录',
			  content: '确定要退出登录吗？',
			  success: (res) => {
				uni.clearStorageSync();//清除缓存
				if (res.confirm) {
				  uni.navigateTo({ url: '/pages/login/login' });
				}
			  }
			});
		  },
		  callHotline() {
			uni.makePhoneCall({ phoneNumber: '4001234567' });
		  },
		  
		  // 加载天气数据
		  async loadWeather() {
			try {
		  const res = await this.$myRequest({
			url: '/api/weatherCtl/weather?cityId='+uni.getStorageSync('cityId'),
			method: 'POST'
		  });
		  
		  if (res.data.code == 200) {
			let weatherData = res.data.data;
			
			// 如果weatherData是字符串，先JSON.parse
			if (typeof weatherData === 'string') {
			  try {
				weatherData = JSON.parse(weatherData);
			  } catch (e) {
				console.error('JSON解析失败:', e);
				return;
			  }
			}
			
			// 判断是否是嵌套结构（weatherData本身又是完整的API响应）
			if (weatherData && typeof weatherData === 'object' && weatherData.code !== undefined) {
			  if (weatherData.code == 0 && weatherData.data) {
				weatherData = weatherData.data;
			  }
			}
			
			// 设置城市信息
			if (weatherData && weatherData.city) {
			  this.cityInfo = {
				cityName: weatherData.city.name ,
				provinceName: weatherData.city.pname 
			  };
			}
			
			// 今日天气和未来天气
			if (weatherData && weatherData.forecast && Array.isArray(weatherData.forecast) && weatherData.forecast.length > 0) {
			  this.todayWeather = weatherData.forecast[0];
			  this.forecastList = weatherData.forecast.slice(1, 7);
			  this.$forceUpdate();
			}
		  }
		} catch (error) {
		  console.error('获取天气失败:', error);
		  uni.showToast({
			title: '天气服务异常',
			icon: 'none'
		  });
		}
		  },
		  
		  // 格式化日期
		  formatDate(dateStr) {
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
			return `${month}/${day}`;
		  },
		  
		  // 获取天气图标
		  getWeatherIcon(conditionId) {
			const iconMap = {
			  '0': '☀️',   // 晴
			  '1': '☁️',   // 多云
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
			return iconMap[conditionId] || '☁️';
		  }
	}
  }
</script>

<style>
  /* 2024潮流设计 - 社区便民小程序用户中心 */
  .container {
    min-height: 100vh;
    background: #F0F4FF;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    padding-bottom: 40rpx;
  }
  
  /* 用户信息区域 - 渐变卡片 */
  .user-section {
    background: linear-gradient(135deg, #8FB4F9 0%, #75A3F8 50%, #6292F0 100%);
    padding: 48rpx 36rpx;
    margin: 0 24rpx 20rpx 24rpx;
    border-radius: 32rpx;
    box-shadow: 0 16rpx 48rpx rgba(98, 146, 240, 0.28);
  }
  
  .user-profile {
    display: flex;
    align-items: center;
    margin-bottom: 40rpx;
  }
  
  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    margin-right: 28rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.6);
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
  }
  
  .user-detail {
    flex: 1;
  }
  
  .username {
    font-size: 36rpx;
    font-weight: 700;
    color: #FFFFFF;
    display: block;
    margin-bottom: 12rpx;
    letter-spacing: 0.5rpx;
    text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  }
  
  .user-tags {
    display: flex;
    align-items: center;
  }
  
  .tag {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.95);
    background: rgba(255, 255, 255, 0.25);
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    border: 1rpx solid rgba(255, 255, 255, 0.3);
  }
  
  .tag-dot {
    margin: 0 12rpx;
    color: rgba(255, 255, 255, 0.6);
  }
  
  /* 订单统计 - 现代化设计 */
  .stats-row {
    display: flex;
    padding-top: 36rpx;
    margin-top: 32rpx;
    border-top: 2rpx solid rgba(255, 255, 255, 0.3);
  }
  
  .stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: all 0.3s ease;
  }
  
  .stat-item:active {
    transform: translateY(-4rpx);
  }
  
  .stat-num {
    font-size: 48rpx;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 10rpx;
    letter-spacing: -1rpx;
    text-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.15);
  }
  
  .stat-text {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
  }
  
  .stat-divider {
    width: 2rpx;
    height: 60rpx;
    background: rgba(255, 255, 255, 0.3);
    align-self: center;
  }
  

  /* 天气预报 - 纯色卡片 */
  .weather-section {
    background: #FFFFFF;
    margin: 0 24rpx 20rpx 24rpx;
    padding: 40rpx 36rpx;
    border-radius: 32rpx;
    box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
  }

  .weather-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
  }

  .location-info {
    display: flex;
    align-items: center;
  }

  .location-icon {
    font-size: 32rpx;
    margin-right: 10rpx;
  }

  .city-name {
    font-size: 30rpx;
    font-weight: 600;
    color: #1A1A1A;
  }

  .refresh-btn {
    width: 56rpx;
    height: 56rpx;
    background: #F5F5F5;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .refresh-btn:active {
    background: #E8E8E8;
  }

  .refresh-icon {
    font-size: 28rpx;
  }

  .today-weather {
    margin-bottom: 30rpx;
  }

  .weather-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
  }

  .temp-area {
    display: flex;
    flex-direction: column;
  }

  .temp-now {
    font-size: 96rpx;
    font-weight: 200;
    line-height: 1;
    margin-bottom: 12rpx;
    color: #1A1A1A;
    letter-spacing: -3rpx;
  }

  .temp-range {
    font-size: 26rpx;
    color: #8E8E93;
    font-weight: 500;
  }

  .weather-desc {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .condition-text {
    font-size: 36rpx;
    font-weight: 600;
    margin-bottom: 10rpx;
    color: #1A1A1A;
  }

  .humidity-text {
    font-size: 26rpx;
    color: #8E8E93;
    font-weight: 500;
  }

  .weather-details {
    display: flex;
    justify-content: space-around;
    padding: 28rpx 0;
    margin-top: 24rpx;
    border-top: 2rpx solid #F0F0F0;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10rpx;
    background: transparent;
    padding: 20rpx 24rpx;
    border-radius: 20rpx;
  }

  .detail-icon {
    font-size: 32rpx;
  }

  .detail-text {
    font-size: 24rpx;
    color: #1A1A1A;
    font-weight: 500;
  }

  .forecast-scroll {
    white-space: nowrap;
    margin-top: 20rpx;
  }

  .forecast-list {
    display: inline-flex;
    gap: 16rpx;
  }

  .forecast-item {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    background: #E8F0FE;
    padding: 24rpx 28rpx;
    border-radius: 24rpx;
    min-width: 130rpx;
    gap: 10rpx;
    margin-right: 16rpx;
    box-shadow: 0 4rpx 16rpx rgba(91, 143, 249, 0.08);
    transition: all 0.3s ease;
  }
  
  .forecast-item:last-child {
    margin-right: 0;
  }
  
  .forecast-item:active {
    transform: translateY(-4rpx);
    box-shadow: 0 8rpx 24rpx rgba(91, 143, 249, 0.15);
    background: #D6E4FF;
  }

  .forecast-date {
    font-size: 24rpx;
    color: #1A1A1A;
    font-weight: 600;
  }

  .forecast-icon {
    font-size: 48rpx;
    margin: 10rpx 0;
  }

  .forecast-condition {
    font-size: 26rpx;
    color: #1A1A1A;
    font-weight: 500;
  }

  .forecast-temp {
    font-size: 22rpx;
    color: #8E8E93;
    font-weight: 500;
  }

  /* 菜单列表 - 现代化卡片 */
  .menu-section {
    background: #FFFFFF;
    margin: 0 24rpx 20rpx 24rpx;
    border-radius: 32rpx;
    box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
    overflow: hidden;
  }
  
  .menu-list {
    display: block;
  }
  
  .menu-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32rpx 36rpx;
    border-bottom: 2rpx solid #F0F0F0;
    transition: all 0.3s ease;
  }
  
  .menu-item:last-child {
    border-bottom: none;
  }
  
  .menu-item:active {
    background-color: #F8F8F8;
    transform: translateX(8rpx);
  }
  
  .menu-text {
    font-size: 30rpx;
    color: #1A1A1A;
    font-weight: 500;
  }
  
  .menu-arrow {
    font-size: 36rpx;
    color: #C7C7CC;
    font-weight: 300;
  }
  
  /* 服务热线 - 现代化设计 */
  .hotline-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32rpx 36rpx;
    transition: all 0.3s ease;
  }
  
  .hotline-item:active {
    background-color: #F8F8F8;
  }
  
  .hotline-left {
    flex: 1;
  }
  
  .hotline-label {
    font-size: 30rpx;
    color: #1A1A1A;
    display: block;
    margin-bottom: 8rpx;
    font-weight: 500;
  }
  
  .hotline-number {
    font-size: 26rpx;
    color: #8E8E93;
    font-family: 'SF Mono', 'Courier New', monospace;
    font-weight: 600;
  }
  
  .call-text {
    font-size: 28rpx;
    color: #FFFFFF;
    padding: 12rpx 28rpx;
    background: #75A3F8;
    border-radius: 20rpx;
    font-weight: 600;
  }
  
  /* 退出登录 - 现代化按钮 */
  .logout-section {
    background: #FFFFFF;
    margin: 0 24rpx 20rpx 24rpx;
    border-radius: 32rpx;
    box-shadow: 0 8rpx 32rpx rgba(255, 59, 48, 0.15);
    overflow: hidden;
  }
  
  .logout-btn {
    display: block;
    text-align: center;
    font-size: 30rpx;
    color: #FF3B30;
    padding: 32rpx 0;
    transition: all 0.3s ease;
    font-weight: 600;
    letter-spacing: 1rpx;
  }
  
  .logout-btn:active {
    background-color: #FFF2F0;
    transform: scale(0.98);
  }
  
  .bottom-space {
    height: 40rpx;
  }

  /* ========== 全局统一主题覆盖（我的页） ========== */
  .container {
    background: linear-gradient(180deg, #edf3ff 0%, #f7f9ff 26%, #f6f8fd 100%) !important;
  }

  .user-section {
    background: linear-gradient(135deg, #8ea9f1 0%, #7fa0ef 55%, #88d2df 100%) !important;
    border: none !important;
    box-shadow: 0 14rpx 36rpx rgba(116, 154, 234, 0.22) !important;
    margin-top: 24rpx;
  }

  .weather-section,
  .menu-section,
  .logout-section {
    background: #ffffff !important;
    border: 1rpx solid #edf1fb !important;
    box-shadow: 0 10rpx 26rpx rgba(173, 189, 220, 0.12) !important;
  }

  .username,
  .stat-num {
    color: #ffffff !important;
  }

  .city-name,
  .temp-now,
  .menu-text,
  .hotline-label {
    color: #33476f !important;
  }

  .menu-arrow,
  .hotline-number,
  .temp-range,
  .detail-text,
  .forecast-temp,
  .forecast-condition {
    color: #8b9abc !important;
  }

  .detail-item,
  .forecast-item {
    background: #f7f9ff !important;
    box-shadow: none !important;
  }

  .call-text {
    color: #ffffff !important;
    background: linear-gradient(135deg, #8cb5ff 0%, #73bde3 100%) !important;
    box-shadow: none !important;
  }

  .logout-btn {
    color: #eb7d65 !important;
  }
</style>
