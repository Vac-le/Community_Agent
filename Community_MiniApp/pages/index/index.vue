<template>
  <view class="container">
    <!-- 背景粒子效果 -->
    <view class="particles-bg">
      <view class="particle" v-for="(p, i) in particles" :key="i" :style="p.style"></view>
    </view>
    <!-- 轮播图 -->
    <swiper class="banner" indicator-dots circular autoplay interval="3000">
      <swiper-item>
        <image src='/static/首页图片.png' mode="aspectFill"></image>
      </swiper-item>
    <swiper-item>
        <image src='https://img95.699pic.com/photo/40245/5493.jpg_wh300.jpg' mode="aspectFill"></image>
      </swiper-item>
	<swiper-item>
	    <image src='https://imgs.699pic.com/images/501/280/316.jpg!list1x.v2' mode="aspectFill"></image>
	</swiper-item>
	</swiper>
    <!-- 快捷服务 -->
    <view class="quick-services">
      <text class="section-title">服务</text>
      <view class="service-grid">
        <view class="service-item" v-for="(m,index) in menus" :key="m.id">
          <navigator :url="m.url" open-type="navigate" class="service-navigator">
            <view class="service-icon">
              <image class="service-image" :src="m.img" mode="aspectFit" :alt="m.name"></image>
            </view>
            <text class="service-name">{{m.name}}</text>
          </navigator>
        </view>
      </view>
    </view>

    <!-- 天气预报 - 只显示今日天气 -->
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
          <view class="detail-item" v-if="!todayWeather.pop && todayWeather.windSpeedDay">
            <text class="detail-icon">💨</text>
            <text class="detail-text">风速 {{todayWeather.windSpeedDay}}m/s</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 最新活动 -->
    <view class="latest-activities">
      <text class="section-title">最新活动</text>
      <view class="activity-list">
        <view class="activity-item" v-for="(item, index) in activities" :key="item.id" @tap="showActivityDetail(item)">
          <image class="activity-image" :src="item.img" mode="aspectFill"></image>
          <view class="activity-info">
            <text class="activity-title">{{item.title}}</text>
            <text class="activity-time">{{item.oper_time}}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 社区公告 -->
    <view class="announcements">
      <text class="section-title">社区公告</text>
      <view class="announcement-list">
        <view class="announcement-item" v-for="(item, index) in announcements" :key="item.id" @tap="showNoticeDetail(item)">
          <text class="announcement-title">{{item.title}}</text>
          <text class="announcement-time">{{item.oper_time}}</text>
        </view>
      </view>
    </view>

    <!-- 活动详情弹窗 -->
    <view class="popup-mask" v-if="showActivityPopup" @tap="closeActivityPopup">
      <view class="popup-content" @tap.stop>
        <view class="popup-header">
          <text class="popup-title">{{selectedActivity.title}}</text>
          <view class="popup-close" @tap="closeActivityPopup">
            <text class="close-icon">×</text>
          </view>
        </view>
        <scroll-view scroll-y class="popup-scroll">
          <view class="popup-time">
            <text class="time-label">发布时间：</text>
            <text class="time-value">{{selectedActivity.operTime}}</text>
          </view>
          <view class="popup-image" v-if="selectedActivity.img">
            <image :src="selectedActivity.img" mode="widthFix" class="detail-image" @tap="previewImage(selectedActivity.img)"></image>
          </view>
          <view class="popup-body">
            <rich-text :nodes="processedContent" class="rich-content"></rich-text>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 公告详情弹窗 -->
    <view class="popup-mask" v-if="showNoticePopup" @tap="closeNoticePopup">
      <view class="popup-content" @tap.stop>
        <view class="popup-header">
          <text class="popup-title">{{selectedNotice.title}}</text>
          <view class="popup-close" @tap="closeNoticePopup">
            <text class="close-icon">×</text>
          </view>
        </view>
        <scroll-view scroll-y class="popup-scroll">
          <view class="popup-time">
            <text class="time-label">发布时间：</text>
            <text class="time-value">{{selectedNotice.operTime}}</text>
          </view>
          <view class="popup-body">
            <text class="notice-content">{{selectedNotice.content}}</text>
          </view>
        </scroll-view>
      </view>
    </view>

  </view>
</template>

<script>
  export default {
    data() {
      return {
        // 活动数据 - 对应activity表字段
        activities: [],
        // 公告数据 - 对应notice表字段
        announcements: [],
        // 弹窗相关数据
        showActivityPopup: false,
        showNoticePopup: false,
        selectedActivity: {},
        selectedNotice: {},
        processedContent: '',
        token: "",
        userId: "",
        menus: [],
        // 天气数据
        cityInfo: {
          cityName: '西安市'
        },
        todayWeather: null,
        // 粒子效果
        particles: []
      }
    },
    onLoad() {
      this.token = uni.getStorageSync('token');
      this.userId = uni.getStorageSync('userId');
      this.checkLoginStatus();
	  this.loadWeather();
	  this.loadActivities();
      this.initParticles();
    },
    onShow() {
      // 页面加载时的逻辑
      this.getUserMenus();
    },
    methods: {
		// 初始化粒子
		initParticles() {
			this.particles = [];
			const particleCount = 30;
			for (let i = 0; i < particleCount; i++) {
				const left = Math.random() * 100;
				const top = Math.random() * 100;
				const size = Math.random() * 4 + 2;
				const duration = Math.random() * 20 + 15;
				const delay = Math.random() * 5;
				const opacity = Math.random() * 0.5 + 0.2;

				this.particles.push({
					id: i,
					style: `left:${left}%;top:${top}%;width:${size}rpx;height:${size}rpx;opacity:${opacity};animation-duration:${duration}s;animation-delay:${delay}s;`
				});
			}
		},

		async getUserMenus(){
				  const res = await this.$myRequest({
				  			  url:'user/userInfoCtl/userMenus',
				  			  method: 'GET',
				  });
				  console.log(res.data);
				  this.menus = res.data.data.menus;
		},
		
		// 加载活动和公告数据
		async loadActivities() {
			try {
				// TODO: 替换为真实API调用
				const res = await this.$myRequest({
				  url: '/user/comCtl/getCommunityInfo',
				  method: 'GET',
				});
				this.activities = res.data.data.activities;
				this.announcements = res.data.data.notices;
			} catch (error) {
				console.error('加载活动数据失败:', error);
				uni.showToast({
					title: '加载活动失败',
					icon: 'error'
				});
			}
		},
		// 显示活动详情
		showActivityDetail(activity) {
			this.selectedActivity = activity;
			// 处理富文本内容
			this.processedContent = this.processRichText(activity.content);
			this.showActivityPopup = true;
		},
		
		// 显示公告详情
		showNoticeDetail(notice) {
			this.selectedNotice = notice;
			this.showNoticePopup = true;
		},
		
		// 关闭活动弹窗
		closeActivityPopup() {
			this.showActivityPopup = false;
		},
		
		// 关闭公告弹窗
		closeNoticePopup() {
			this.showNoticePopup = false;
		},
		
		// 处理富文本内容
		processRichText(htmlContent) {
			if (!htmlContent) return '';
			
			// 确保图片路径完整
			let processedHtml = htmlContent.replace(
				/<img[^>]+src="([^"]*)"[^>]*>/g,
				(match, src) => {
					// 如果是相对路径，补充完整URL
					if (!src.startsWith('http')) {
						src = this.$baseUrl + src;
					}
					// 添加样式确保图片适配
					return match.replace(/style="[^"]*"/g, '').replace(/src="[^"]*"/, `src="${src}" style="max-width:100%;height:auto;display:block;margin:10px auto;border-radius:8px;"`);
				}
			);
			
			return processedHtml;
		},
		
		// 图片预览
		previewImage(src) {
			uni.previewImage({
				urls: [src],
				current: src
			});
		},
		
		  emergencyHelp() {
			uni.showModal({
			  title: '紧急求助',
			  content: '确定要联系紧急救援吗？',
			  success: (res) => {
				if (res.confirm) {
				  uni.makePhoneCall({ phoneNumber: '120' });
				}
			  }
			});
		  },
		  //验证登录
		  checkLoginStatus() {
			if (!this.token) {
			  // 未登录，跳转到登录页
			  uni.reLaunch({
				url: '/pages/login/login'
			  })
			  return
			}
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
				
				if (typeof weatherData === 'string') {
				  try {
					weatherData = JSON.parse(weatherData);
				  } catch (e) {
					console.error('JSON解析失败:', e);
					return;
				  }
				}
				
				if (weatherData && typeof weatherData === 'object' && weatherData.code !== undefined) {
				  if (weatherData.code == 0 && weatherData.data) {
					weatherData = weatherData.data;
				  }
				}
				
				if (weatherData && weatherData.city) {
				  this.cityInfo = {
					cityName: weatherData.city.name || '西安市',
					provinceName: weatherData.city.pname || '陕西省'
				  };
				}
				
				if (weatherData && weatherData.forecast && Array.isArray(weatherData.forecast) && weatherData.forecast.length > 0) {
				  this.todayWeather = weatherData.forecast[0];
				  this.$forceUpdate();
				}
			  }
			} catch (error) {
			  console.error('获取天气失败:', error);
			}
		  }
    },
  }
</script>

<style>
  /* ========== 粒子背景效果 ========== */
  .particles-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
  }

  .particle {
    position: absolute;
    background: radial-gradient(circle, rgba(30, 58, 138, 0.8) 0%, rgba(30, 58, 138, 0) 70%);
    border-radius: 50%;
    animation: float linear infinite;
    will-change: transform, opacity;
  }

  @keyframes float {
    0% {
      transform: translateY(100vh) translateX(0) scale(1);
      opacity: 0;
    }
    10% {
      opacity: var(--particle-opacity, 0.5);
    }
    90% {
      opacity: var(--particle-opacity, 0.5);
    }
    100% {
      transform: translateY(-100vh) translateX(100px) scale(0.5);
      opacity: 0;
    }
  }

  /* ========== 全局容器 ========== */
  .container {
    min-height: 100vh;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    padding-bottom: 40rpx;
    position: relative;
    z-index: 1;
  }
  
  /* ========== 轮播图 ========== */
  .banner {
    width: calc(100% - 48rpx);
    height: 360rpx;
    margin: 24rpx 24rpx 20rpx 24rpx;
    border-radius: 20rpx;
    overflow: hidden;
    box-shadow: 0 10rpx 30rpx rgba(30, 58, 138, 0.12);
    position: relative;
    z-index: 1;
    border: 1rpx solid rgba(30, 58, 138, 0.08);
    animation: slideInDown 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    background: linear-gradient(135deg, rgba(30, 58, 138, 0.05) 0%, rgba(249, 115, 22, 0.05) 100%);
  }
  
  .banner image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .banner::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 50%, rgba(249, 115, 22, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(30, 58, 138, 0.1) 0%, transparent 50%);
    pointer-events: none;
    z-index: 1;
    animation: shimmer 3s ease-in-out infinite;
  }

  @keyframes shimmer {
    0%, 100% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
  }
  
  @keyframes slideInDown {
    from {
      opacity: 0;
      transform: translateY(-20rpx);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* ========== 天气预报卡片 ========== */
  .weather-section {
    background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    margin: 0 24rpx 20rpx 24rpx;
    padding: 40rpx 32rpx;
    border-radius: 20rpx;
    box-shadow: 0 10rpx 30rpx rgba(30, 58, 138, 0.08);
    border: 1rpx solid rgba(30, 58, 138, 0.06);
    animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
    position: relative;
    overflow: hidden;
  }

  .weather-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.05) 0%, transparent 70%);
    animation: rotate-glow 20s linear infinite;
    pointer-events: none;
  }

  @keyframes rotate-glow {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .weather-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32rpx;
  }

  .location-info {
    display: flex;
    align-items: center;
  }

  .location-icon {
    font-size: 32rpx;
    margin-right: 12rpx;
  }

  .city-name {
    font-size: 32rpx;
    font-weight: 700;
    color: #1e3a8a;
    letter-spacing: -0.5rpx;
  }

  .today-weather {
    margin-bottom: 32rpx;
  }

  .weather-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
  }

  .temp-area {
    display: flex;
    flex-direction: column;
  }

  .temp-now {
    font-size: 96rpx;
    font-weight: 300;
    line-height: 1;
    margin-bottom: 8rpx;
    color: #1e3a8a;
    letter-spacing: -3rpx;
  }

  .temp-range {
    font-size: 26rpx;
    color: #6b7280;
    font-weight: 500;
    letter-spacing: -0.2rpx;
  }

  .weather-desc {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .condition-text {
    font-size: 36rpx;
    font-weight: 700;
    margin-bottom: 8rpx;
    color: #1f2937;
    letter-spacing: -0.5rpx;
  }

  .humidity-text {
    font-size: 26rpx;
    color: #6b7280;
    font-weight: 500;
  }

  .weather-details {
    display: flex;
    justify-content: space-around;
    padding: 28rpx 0;
    margin-top: 24rpx;
    border-top: 2rpx solid #e5e7eb;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10rpx;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    padding: 12rpx 16rpx;
    border-radius: 12rpx;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }

  .detail-item::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.3) 0%, transparent 70%);
    transform: translate(-50%, -50%);
    transition: width 300ms ease-out, height 300ms ease-out;
    pointer-events: none;
  }

  .detail-item:active {
    background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
    transform: scale(0.95);
  }

  .detail-item:active::before {
    width: 200rpx;
    height: 200rpx;
  }

  .detail-icon {
    font-size: 32rpx;
  }

  .detail-text {
    font-size: 24rpx;
    color: #6b7280;
    font-weight: 500;
  }

  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(20rpx);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* ========== 快捷服务 ========== */
  .quick-services {
    background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    padding: 40rpx 32rpx;
    margin: 0 24rpx 20rpx 24rpx;
    border-radius: 20rpx;
    box-shadow: 0 10rpx 30rpx rgba(30, 58, 138, 0.08);
    border: 1rpx solid rgba(30, 58, 138, 0.06);
    animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
  }
  
  .section-title {
    font-size: 40rpx;
    font-weight: 800;
    color: #1e3a8a;
    margin-bottom: 32rpx;
    display: block;
    letter-spacing: -0.8rpx;
    position: relative;
    padding-bottom: 16rpx;
  }

  .section-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 60rpx;
    height: 6rpx;
    background: linear-gradient(90deg, #f97316 0%, #fed7aa 100%);
    border-radius: 3rpx;
  }
  
  .service-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    gap: 32rpx 0;
  }
  
  .service-item {
    width: 20%;
    text-align: center;
  }
  
  .service-navigator {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: inherit;
  }
  
  .service-icon {
    width: 120rpx;
    height: 120rpx;
    margin-bottom: 16rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
    border-radius: 16rpx;
    border: 2rpx solid rgba(30, 58, 138, 0.1);
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }

  .service-icon::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, transparent 100%);
    opacity: 0;
    transition: opacity 200ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .service-icon::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.3) 0%, transparent 70%);
    transform: translate(-50%, -50%);
    opacity: 0;
    transition: opacity 200ms cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
  }
  
  .service-icon:active {
    transform: scale(0.92);
    background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
    box-shadow: 0 8rpx 20rpx rgba(30, 58, 138, 0.15);
  }

  .service-icon:active::before {
    opacity: 1;
  }

  .service-icon:active::after {
    opacity: 1;
    animation: pulse-glow 0.6s ease-out;
  }

  @keyframes pulse-glow {
    0% {
      transform: translate(-50%, -50%) scale(1);
      opacity: 1;
    }
    100% {
      transform: translate(-50%, -50%) scale(1.5);
      opacity: 0;
    }
  }
  
  .service-image {
    width: 80rpx;
    height: 80rpx;
    position: relative;
    z-index: 1;
  }
  
  .service-name {
    font-size: 26rpx;
    color: #1f2937;
    font-weight: 600;
    letter-spacing: -0.3rpx;
  }

  /* ========== 最新活动 ========== */
  .latest-activities {
    background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    padding: 40rpx 32rpx;
    margin: 0 24rpx 20rpx 24rpx;
    border-radius: 20rpx;
    box-shadow: 0 10rpx 30rpx rgba(30, 58, 138, 0.08);
    border: 1rpx solid rgba(30, 58, 138, 0.06);
    animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
  }
  
  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .activity-item {
    position: relative;
    border-radius: 16rpx;
    overflow: hidden;
    height: 240rpx;
    box-shadow: 0 8rpx 24rpx rgba(30, 58, 138, 0.1);
    border: 1rpx solid rgba(30, 58, 138, 0.06);
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .activity-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 0%, rgba(249, 115, 22, 0.2) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 200ms cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 2;
    pointer-events: none;
  }
  
  .activity-item:active {
    transform: scale(0.98);
    box-shadow: 0 12rpx 32rpx rgba(30, 58, 138, 0.15);
  }

  .activity-item:active::before {
    opacity: 1;
  }
  
  .activity-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    top: 0;
    left: 0;
  }
  
  .activity-info {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 32rpx 28rpx;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.85) 0%, rgba(0, 0, 0, 0.5) 50%, transparent 100%);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
  }
  
  .activity-title {
    font-size: 34rpx;
    color: #ffffff;
    margin-bottom: 10rpx;
    font-weight: 700;
    line-height: 1.3;
    letter-spacing: -0.5rpx;
    text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.4);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .activity-time {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.95);
    font-weight: 500;
    text-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.3);
  }

  /* ========== 社区公告 ========== */
  .announcements {
    background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    padding: 40rpx 32rpx;
    margin: 0 24rpx 20rpx 24rpx;
    border-radius: 20rpx;
    box-shadow: 0 10rpx 30rpx rgba(30, 58, 138, 0.08);
    border: 1rpx solid rgba(30, 58, 138, 0.06);
    animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.4s both;
  }
  
  .announcement-list {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
  }
  
  .announcement-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24rpx 28rpx;
    border-radius: 12rpx;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    border-left: 5rpx solid #f97316;
    box-shadow: 0 4rpx 12rpx rgba(30, 58, 138, 0.06);
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }

  .announcement-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, rgba(249, 115, 22, 0.05) 0%, transparent 100%);
    opacity: 0;
    transition: opacity 200ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .announcement-item::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, 
      transparent 0%, 
      rgba(249, 115, 22, 0.1) 50%, 
      transparent 100%);
    opacity: 0;
    animation: none;
  }
  
  .announcement-item:active {
    transform: scale(0.98);
    background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
    box-shadow: 0 8rpx 20rpx rgba(30, 58, 138, 0.12);
  }

  .announcement-item:active::before {
    opacity: 1;
  }

  .announcement-item:active::after {
    opacity: 1;
    animation: shimmer-line 0.8s ease-in-out;
  }

  @keyframes shimmer-line {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }
  
  .announcement-title {
    font-size: 28rpx;
    color: #1f2937;
    flex: 1;
    margin-right: 20rpx;
    font-weight: 600;
    line-height: 1.4;
    letter-spacing: -0.3rpx;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
    position: relative;
    z-index: 1;
  }
  
  .announcement-time {
    font-size: 24rpx;
    color: #9ca3af;
    white-space: nowrap;
    font-weight: 500;
    position: relative;
    z-index: 1;
  }

  /* ========== 弹窗样式 ========== */
  .popup-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(20rpx);
    -webkit-backdrop-filter: blur(20rpx);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40rpx;
    animation: fadeIn 200ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .popup-content {
    background: #ffffff;
    border-radius: 28rpx;
    padding: 0;
    max-height: 80vh;
    overflow: hidden;
    width: 90%;
    max-width: 650rpx;
    box-shadow: 0 25rpx 50rpx rgba(0, 0, 0, 0.25);
    animation: popupIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
  }

  .popup-scroll {
    flex: 1;
    height: 100%;
    max-height: calc(80vh - 120rpx);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes popupIn {
    from {
      opacity: 0;
      transform: scale(0.92) translateY(40rpx);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 32rpx;
    border-bottom: 1rpx solid #e5e7eb;
    background: #ffffff;
    border-radius: 28rpx 28rpx 0 0;
  }

  .popup-title {
    font-size: 34rpx;
    font-weight: 800;
    color: #1f2937;
    flex: 1;
    margin-right: 20rpx;
    line-height: 1.4;
    letter-spacing: -0.5rpx;
  }

  .popup-close {
    width: 56rpx;
    height: 56rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;
    background: #f3f4f6;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    flex-shrink: 0;
  }

  .popup-close:active {
    background: #e5e7eb;
    transform: scale(0.9);
  }

  .close-icon {
    font-size: 40rpx;
    color: #9ca3af;
    line-height: 1;
    font-weight: 300;
  }

  .popup-time {
    padding: 24rpx 32rpx;
    display: flex;
    align-items: center;
    background: #f9fafb;
    flex-shrink: 0;
  }

  .time-label {
    font-size: 26rpx;
    color: #9ca3af;
    margin-right: 12rpx;
    font-weight: 500;
  }

  .time-value {
    font-size: 26rpx;
    color: #1f2937;
    font-weight: 600;
  }

  .popup-image {
    padding: 24rpx 32rpx;
    text-align: center;
    flex-shrink: 0;
  }

  .detail-image {
    width: 100%;
    max-width: 600rpx;
    border-radius: 16rpx;
    box-shadow: 0 8rpx 24rpx rgba(30, 58, 138, 0.12);
  }

  .popup-body {
    padding: 32rpx;
  }

  .rich-content {
    line-height: 1.8;
    font-size: 28rpx;
    color: #1f2937;
    letter-spacing: -0.2rpx;
  }

  /* 富文本内容样式 */
  .rich-content >>> p {
    margin-bottom: 20rpx;
    text-align: justify;
  }

  .rich-content >>> strong {
    font-weight: 700;
    color: #1e3a8a;
  }

  .rich-content >>> ul, .rich-content >>> ol {
    padding-left: 40rpx;
    margin-bottom: 20rpx;
  }

  .rich-content >>> li {
    margin-bottom: 12rpx;
    line-height: 1.6;
  }

  .rich-content >>> img {
    max-width: 100% !important;
    height: auto !important;
    display: block !important;
    margin: 20rpx auto !important;
    border-radius: 16rpx !important;
    box-shadow: 0 8rpx 24rpx rgba(30, 58, 138, 0.12) !important;
  }

  .notice-content {
    line-height: 1.8;
    font-size: 28rpx;
    color: #1f2937;
    text-align: justify;
    letter-spacing: -0.2rpx;
  }

  /* ========== 深色主题覆盖（立即生效） ========== */
  .container {
    background: linear-gradient(135deg, #07111f 0%, #0c1a2e 45%, #10233d 100%) !important;
  }

  .quick-services,
  .weather-section,
  .latest-activities,
  .announcements {
    background: rgba(12, 26, 46, 0.72) !important;
    border: 1rpx solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 12rpx 28rpx rgba(2, 8, 23, 0.35) !important;
  }

  .section-title {
    color: #e6edf7 !important;
  }

  .section-title::after {
    background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%) !important;
  }

  .city-name,
  .condition-text,
  .announcement-title,
  .service-name,
  .detail-text,
  .temp-range,
  .humidity-text {
    color: #dbe7f5 !important;
  }

  .announcement-time,
  .activity-time {
    color: #9fb1c8 !important;
  }

  .service-icon,
  .detail-item,
  .announcement-item {
    background: rgba(255, 255, 255, 0.06) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
  }

  .popup-content {
    background: #0e2135 !important;
    border: 1rpx solid rgba(255, 255, 255, 0.12) !important;
  }

  .popup-header,
  .popup-time {
    background: rgba(255, 255, 255, 0.04) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
  }

  .popup-title,
  .time-value,
  .rich-content,
  .notice-content {
    color: #e6edf7 !important;
  }

  .time-label,
  .close-icon {
    color: #9fb1c8 !important;
  }

  .popup-close {
    background: rgba(255, 255, 255, 0.08) !important;
  }

  /* ========== 高级质感强化 ========== */
  .banner,
  .quick-services,
  .weather-section,
  .latest-activities,
  .announcements {
    backdrop-filter: blur(16rpx);
    -webkit-backdrop-filter: blur(16rpx);
  }

  .banner {
    border: 1rpx solid rgba(255,255,255,0.16) !important;
    box-shadow: 0 16rpx 36rpx rgba(2,8,23,.45) !important;
  }

  .section-title {
    letter-spacing: 1rpx;
  }

/* ========== 浅色高级拟态主题（最终覆盖） ========== */
.container {
  background:
    radial-gradient(circle at 14% 10%, rgba(130, 162, 255, 0.35) 0%, rgba(130, 162, 255, 0) 34%),
    radial-gradient(circle at 88% 86%, rgba(132, 224, 255, 0.28) 0%, rgba(132, 224, 255, 0) 30%),
    linear-gradient(145deg, #e7eeff 0%, #dce8ff 100%) !important;
}

.quick-services,
.weather-section,
.latest-activities,
.announcements,
.popup-content,
.banner {
  background: #edf3ff !important;
  border: 1rpx solid rgba(255, 255, 255, 0.75) !important;
  box-shadow: 14rpx 14rpx 28rpx rgba(128, 151, 199, 0.28), -14rpx -14rpx 28rpx rgba(255, 255, 255, 0.95) !important;
}

.section-title,
.city-name,
.condition-text,
.announcement-title,
.service-name,
.detail-text,
.temp-range,
.humidity-text,
.activity-title,
.popup-title,
.time-value,
.rich-content,
.notice-content {
  color: #334f7c !important;
}

.announcement-time,
.activity-time,
.time-label,
.close-icon {
  color: #7890b4 !important;
}

.service-icon,
.detail-item,
.announcement-item,
.popup-header,
.popup-time,
.popup-close {
  background: #edf3ff !important;
  border: 1rpx solid rgba(255,255,255,0.7) !important;
  box-shadow: inset 8rpx 8rpx 14rpx rgba(159, 179, 220, 0.2), inset -8rpx -8rpx 14rpx rgba(255, 255, 255, 0.9) !important;
}


/* ========== 2026 全局终极统一主题覆盖（首页） ========== */
.container {
  background:
    radial-gradient(circle at 14% 8%, rgba(125, 166, 255, 0.30) 0%, rgba(125, 166, 255, 0) 34%),
    linear-gradient(145deg, #eaf1ff 0%, #e0eaff 100%) !important;
}

.banner,
.quick-services,
.latest-activities,
.announcements,
.popup-content {
  background: #edf3ff !important;
  border: 1rpx solid rgba(255,255,255,0.82) !important;
  box-shadow: 0 12rpx 28rpx rgba(123, 146, 194, 0.20) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

/* 天气预报：大背景，不做小玻璃模块 */
.weather-section {
  background: #edf3ff !important;
  border: 1rpx solid rgba(255,255,255,0.82) !important;
  box-shadow: 0 12rpx 28rpx rgba(123, 146, 194, 0.20) !important;
}

.today-weather,
.weather-main,
.weather-details,
.detail-item {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.city-name,
.temp-now,
.condition-text,
.temp-range,
.humidity-text,
.detail-text {
  color: #2f4672 !important;
}

.section-title,
.activity-title,
.announcement-title,
.service-name,
.popup-title,
.time-value,
.rich-content,
.notice-content {
  color: #2f4672 !important;
}

.announcement-time,
.activity-time,
.time-label,
.close-icon {
  color: #7389af !important;
}


/* ========== 2026 首页终局覆盖（天气大背景版） ========== */
.container {
  background:
    radial-gradient(circle at 14% 8%, rgba(125, 166, 255, 0.30) 0%, rgba(125, 166, 255, 0) 34%),
    linear-gradient(145deg, #eaf1ff 0%, #e0eaff 100%) !important;
}

.banner,
.quick-services,
.latest-activities,
.announcements,
.popup-content {
  background: #edf3ff !important;
  border: 1rpx solid rgba(255,255,255,0.82) !important;
  box-shadow: 0 12rpx 28rpx rgba(123,146,194,0.20) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.weather-section {
  background: #edf3ff !important;
  border: 1rpx solid rgba(255,255,255,0.82) !important;
  box-shadow: 0 12rpx 28rpx rgba(123, 146, 194, 0.20) !important;
}

.today-weather,
.weather-main,
.weather-details,
.detail-item {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.city-name,
.temp-now,
.condition-text,
.temp-range,
.humidity-text,
.detail-text,
.weather-header,
.location-info,
.time-value {
  color: #2f4672 !important;
}

.section-title,
.activity-title,
.announcement-title,
.service-name,
.popup-title,
.rich-content,
.notice-content {
  color: #2f4672 !important;
}

.announcement-time,
.activity-time,
.time-label,
.close-icon {
  color: #7389af !important;
}

</style>
