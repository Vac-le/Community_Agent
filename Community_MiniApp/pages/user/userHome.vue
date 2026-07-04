<template>
  <view class="container">
    <view class="summary-panel summary-home">
      <view class="summary-top">
        <view>
          <text class="summary-tag">家政订单</text>
          <view class="summary-title">居家服务安排</view>
          <view class="summary-desc">把预约时间、上门信息和师傅联系方式集中展示，页面更清晰。</view>
        </view>
        <view class="summary-count">{{ orders.length }}单</view>
      </view>

      <view class="summary-tabs">
        <view 
          v-for="(tab, index) in tabs" 
          :key="index" 
          class="summary-tab" 
          :class="{ active: currentTab === index }"
          @tap="switchTab(index)">
          <text class="summary-tab-label">{{ tab }}</text>
          <text class="summary-tab-count">{{ getStatusCount(index) }}</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="order-list" @scrolltolower="loadMore">
      <view class="order-card" v-for="order in filteredOrders" :key="order.id">
        <view class="card-head">
          <text class="card-type">上门家政</text>
          <text class="card-status status-0" v-if="order.orderStatus === 0">待服务</text>
          <text class="card-status status-1" v-else-if="order.orderStatus === 1">服务中</text>
          <text class="card-status status-2" v-else>已完成</text>
        </view>

        <view class="card-order-no">订单号：{{ order.id }}</view>

        <view class="hero-box home-hero">
          <view class="home-hero-left">
            <text class="home-icon">{{ getServiceIcon(order.home ? order.home.name : '') }}</text>
            <view>
              <text class="hero-title">{{ order.home ? order.home.name : '家政服务' }}</text>
              <text class="hero-time">下单时间 {{ formatTime(order.startTime) }}</text>
              <text class="hero-price-label hero-inline-label">费用</text>
            </view>
          </view>
          <text class="hero-price">¥{{ order.amount }}</text>
        </view>

        <view class="appointment-box" v-if="order.orderDate">
          <text class="info-label">预约上门</text>
          <text class="appointment-time">{{ formatDate(order.orderDate) }}</text>
        </view>

        <view class="section-box list-box" v-if="order.home">
          <view class="section-title-row">
            <text class="dot dot-home"></text>
            <text class="section-title">服务项目</text>
          </view>
          <view class="food-row">
            <view>
              <text class="food-name">{{ order.home.name }}</text>
            </view>
            <text class="food-price">¥{{ order.home.price }}</text>
          </view>
        </view>

        <view class="info-grid">
          <view class="info-box">
            <text class="info-label">服务地址</text>
            <text class="info-value">{{ order.deliveryAddress }}</text>
          </view>
          <view class="info-box">
            <text class="info-label">联系人</text>
            <text class="info-value">{{ order.user.name }} {{ order.deliveryPhone }}</text>
          </view>
        </view>

        <view class="remark-box" v-if="order.remark">
          <text class="remark-label">备注</text>
          <text class="remark-value">{{ order.remark }}</text>
        </view>

        <view class="worker-box" v-if="order.send">
          <text class="info-label">服务人员</text>
          <text class="info-value">{{ order.send.name }} {{ order.send.phone }}</text>
        </view>

        <view class="card-foot">
          <view>
            <text class="foot-label">服务费用</text>
            <text class="foot-price">¥{{ order.amount }}</text>
          </view>
          <view class="action-buttons">
            <button v-if="order.orderStatus === 0" class="action-btn btn-cancel" size="mini" @tap.stop="cancelOrder(order.id)">取消订单</button>
            <button v-if="order.orderStatus === 1 && order.send" class="action-btn btn-contact" size="mini" @tap.stop="contactWorker(order.send.phone)">联系师傅</button>
            <button v-if="order.orderStatus === 2" class="action-btn btn-review" size="mini" @tap.stop="reviewOrder(order.id)">评价</button>
          </view>
        </view>
      </view>

      <view class="empty-state" v-if="filteredOrders.length === 0">
        <text class="empty-icon">🏠</text>
        <text class="empty-text">暂无订单</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      tabs: ['待服务', '服务中', '已完成'],
      currentTab: 0,
      orders: []
      // 后端数据结构：
      // {
      //   id: Number,
      //   startTime: Date, // 订单创建时间（用于显示下单时间）
      //   amount: Number,
      //   deliveryAddress: String,
      //   deliveryPhone: String,
      //   remark: String,
      //   orderStatus: Number, // 0-待接单 1-服务中 2-已完成 3-已取消
      //   orderDate: String, // 预约服务日期（格式：yyyy-MM-dd）
      //   user: { id: Number, name: String },
      //   send: { id: Number, name: String, phone: String }, // 服务人员信息
      //   home: { id: Number, name: String, price: Number } // 家政服务（单个对象）
      // }
    }
  },
  computed: {
    filteredOrders() {
      return this.orders.filter(order => order.orderStatus === this.currentTab);
    }
  },
  onLoad() {
    this.loadOrders();
  },
  onShow() {
    this.loadOrders();
  },
  onPullDownRefresh() {
    this.loadOrders();
  },
  onUnload() {
    // 页面卸载
  },
  methods: {
    // 加载订单列表
    async loadOrders() {
      try {
        uni.showLoading({ title: '加载中...' });
        const res = await this.$myRequest({
          url: '/user/ordersCtl/userHomeOrder',
          method: 'GET'
        });
        uni.hideLoading();
        uni.stopPullDownRefresh();
        
        if (res.data.code === 200) {
          this.orders = res.data.data || [];
          console.log('家政订单列表:', this.orders);
        } else {
          uni.showToast({
            title: res.data.message || '加载失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        uni.stopPullDownRefresh();
        console.error('获取订单失败:', error);
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    },
    
    switchTab(index) {
      this.currentTab = index;
    },
    
    getStatusCount(status) {
      return this.orders.filter(order => order.orderStatus === status).length;
    },
    getStatusText(status) {
      const statusMap = {
        0: '待服务',
        1: '服务中',
        2: '已完成'
      };
      return statusMap[status] || '';
    },
    
    getServiceIcon(serviceType) {
      const iconMap = {
        '家庭保洁': '🧹',
        '管道疏通': '🔧',
        '家电维修': '⚡',
        '月嫂服务': '👶',
        '空调清洗': '❄️',
        '开荒保洁': '✨',
        '保姆服务': '👩',
        '育儿嫂': '🍼',
        '钟点工': '⏰'
      };
      return iconMap[serviceType] || '🏠';
    },
    
    formatTime(timeStr) {
      if (!timeStr) return '';
      const date = new Date(timeStr);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '';
      // 如果已经是日期格式（yyyy-MM-dd），直接返回
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return dateStr;
      }
      // 否则解析并格式化
      const date = new Date(dateStr);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    cancelOrder(orderId) {
      uni.showModal({
        title: '取消订单',
        content: '确定要取消此家政订单吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              uni.showLoading({ title: '处理中...' });
              // TODO: 调用取消订单的后端接口
              // const response = await this.$myRequest({
              //   url: '/user/ordersCtl/cancelHomeOrder',
              //   method: 'POST',
              //   data: { orderId }
              // });
              uni.hideLoading();
              uni.showToast({
                title: '订单已取消',
                icon: 'success'
              });
              // 重新加载订单列表
              this.loadOrders();
            } catch (error) {
              uni.hideLoading();
              console.error('取消订单失败:', error);
              uni.showToast({
                title: '取消失败，请重试',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    
    contactWorker(phone) {
      if (!phone) {
        uni.showToast({
          title: '暂无服务人员联系方式',
          icon: 'none'
        });
        return;
      }
      uni.showModal({
        title: '联系服务人员',
        content: `是否拨打服务人员电话 ${phone}？`,
        success: (res) => {
          if (res.confirm) {
            uni.makePhoneCall({ 
              phoneNumber: phone,
              fail: (err) => {
                console.error('拨打电话失败:', err);
                uni.showToast({
                  title: '拨打电话失败',
                  icon: 'none'
                });
              }
            });
          }
        }
      });
    },
    
    reviewOrder(orderId) {
      uni.showToast({
        title: '评价功能开发中',
        icon: 'none'
      });
      // uni.navigateTo({ url: `/pages/review/review?orderId=${orderId}&type=home` });
    },
    
    loadMore() {
      // 加载更多数据
      console.log('加载更多');
    }
  }
}
</script>

<style scoped>
.container {
  height: 100vh;
  background: linear-gradient(180deg, #edf3ff 0%, #f7f8fd 24%, #f5f6fb 100%);
  display: flex;
  flex-direction: column;
}

.summary-panel {
  margin: 24rpx 24rpx 18rpx;
  padding: 34rpx 30rpx 28rpx;
  border-radius: 30rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(191, 199, 232, 0.16);
}

.summary-home {
  background: linear-gradient(180deg, #fcfdff 0%, #ffffff 100%);
}

.summary-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 26rpx;
}

.summary-tag {
  display: inline-block;
  font-size: 28rpx;
  color: #7a9de3;
  margin-bottom: 14rpx;
  font-weight: 600;
}

.summary-title {
  font-size: 56rpx;
  line-height: 1.16;
  color: #334f7b;
  font-weight: 700;
  margin-bottom: 14rpx;
}

.summary-desc {
  font-size: 28rpx;
  line-height: 1.65;
  color: #92a8c6;
}

.summary-count {
  min-width: 150rpx;
  padding: 22rpx 0;
  border-radius: 999rpx;
  text-align: center;
  font-size: 38rpx;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #7caaf3 0%, #7dd2ca 100%);
  box-shadow: 0 10rpx 18rpx rgba(117, 188, 218, 0.22);
}

.summary-tabs {
  display: flex;
  gap: 18rpx;
  background: #f0f6ff;
  border-radius: 26rpx;
  padding: 16rpx;
}

.summary-tab {
  flex: 1;
  border-radius: 22rpx;
  padding: 22rpx 10rpx;
  text-align: center;
}

.summary-tab.active {
  background: linear-gradient(135deg, #78a8f3 0%, #7fd0c8 100%);
  box-shadow: 0 8rpx 16rpx rgba(117, 188, 218, 0.22);
}

.summary-tab-label {
  display: block;
  font-size: 32rpx;
  color: #6f92c2;
  font-weight: 700;
}

.summary-tab-count {
  display: block;
  margin-top: 10rpx;
  font-size: 28rpx;
  color: #9cb4cf;
}

.summary-tab.active .summary-tab-label,
.summary-tab.active .summary-tab-count {
  color: #ffffff;
}

.order-list {
  flex: 1;
  padding: 0 24rpx 24rpx;
  box-sizing: border-box;
}

.order-card {
  background: rgba(255,255,255,0.98);
  border-radius: 30rpx;
  padding: 28rpx;
  margin-bottom: 22rpx;
  box-shadow: 0 12rpx 26rpx rgba(196, 206, 228, 0.14);
}

.card-head,
.card-foot,
.info-grid,
.hero-box,
.food-row,
.home-hero-left,
.appointment-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-head {
  margin-bottom: 16rpx;
}

.card-type {
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: #eef4ff;
  color: #6e95e1;
  font-size: 28rpx;
  font-weight: 700;
}

.card-order-no,
.hero-time,
.info-label,
.foot-label,
.empty-text,
.remark-value,
.hero-inline-label {
  color: #95aaca;
  font-size: 28rpx;
}

.card-order-no {
  margin-bottom: 14rpx;
}

.card-status {
  padding: 12rpx 22rpx;
  border-radius: 999rpx;
  font-size: 30rpx;
  font-weight: 700;
}

.status-0 {
  background: #fff2db;
  color: #e3a735;
}

.status-1 {
  background: #e9f2ff;
  color: #5e8df5;
}

.status-2 {
  background: #e8f7ee;
  color: #58b37a;
}

.hero-box,
.section-box,
.info-box,
.worker-box,
.remark-box,
.appointment-box {
  background: #f7fbff;
  border-radius: 24rpx;
}

.hero-box {
  padding: 26rpx 24rpx;
  margin-bottom: 20rpx;
}

.home-hero-left {
  gap: 20rpx;
  justify-content: flex-start;
}

.home-icon {
  font-size: 58rpx;
}

.hero-title,
.food-name,
.info-value,
.foot-price,
.section-title,
.appointment-time {
  color: #35527d;
  font-weight: 700;
}

.hero-title {
  display: block;
  font-size: 44rpx;
  margin-bottom: 12rpx;
}

.hero-price {
  font-size: 50rpx;
  color: #35527d;
  font-weight: 700;
}

.appointment-box,
.section-box,
.worker-box,
.remark-box {
  padding: 24rpx;
  margin-bottom: 18rpx;
}

.appointment-time {
  font-size: 38rpx;
  color: #4c75c3;
}

.section-title-row {
  display: flex;
  align-items: center;
  margin-bottom: 18rpx;
}

.dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  margin-right: 14rpx;
}

.dot-home {
  background: #8fd0ff;
}

.food-row {
  padding: 6rpx 0;
}

.food-name {
  display: block;
  font-size: 40rpx;
}

.food-price {
  font-size: 38rpx;
  color: #5f8eed;
  font-weight: 700;
}

.info-grid {
  gap: 18rpx;
  margin-bottom: 18rpx;
}

.info-box {
  flex: 1;
  padding: 20rpx;
}

.info-label {
  display: block;
  margin-bottom: 12rpx;
}

.info-value {
  display: block;
  font-size: 26rpx;
  word-break: break-all;
}

.remark-label {
  color: #6e95e1;
  font-size: 28rpx;
  font-weight: 700;
  margin-bottom: 10rpx;
}

.card-foot {
  margin-top: 6rpx;
}

.foot-label {
  display: block;
  margin-bottom: 10rpx;
}

.foot-price {
  display: block;
  font-size: 48rpx;
}

.action-buttons {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.action-btn {
  min-height: 72rpx;
  padding: 0 28rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  line-height: 1;
  border: none;
}

.btn-cancel {
  background: #fff1ee;
  color: #e98374;
}

.btn-contact {
  background: #eef4ff;
  color: #6794ec;
}

.btn-review {
  background: #eef8ef;
  color: #65a96f;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 140rpx 0;
}

.empty-icon {
  font-size: 110rpx;
  margin-bottom: 20rpx;
}
</style>
.container {
  width: 100%;
  height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 导航栏 */
.tabs-container {
  background: #FFFFFF;
  flex-shrink: 0;
  z-index: 100;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.tabs {
  display: flex;
  padding: 0 24rpx;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 28rpx 0 20rpx;
  position: relative;
  transition: all 0.3s;
}

.tab-text {
  font-size: 30rpx;
  color: #666666;
  font-weight: 500;
  transition: all 0.3s;
}

.tab-item.active .tab-text {
  color: #75A3F8;
  font-weight: 600;
  font-size: 32rpx;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  width: 48rpx;
  height: 6rpx;
  background: linear-gradient(90deg, #75A3F8 0%, #6292F0 100%);
  border-radius: 3rpx;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    width: 0;
    opacity: 0;
  }
  to {
    width: 48rpx;
    opacity: 1;
  }
}

/* 订单列表 */
.order-list {
  flex: 1;
  height: calc(100vh - 160rpx);
  padding: 24rpx;
  box-sizing: border-box;
}

.order-item {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.order-item:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #F0F0F0;
}

.order-number {
  font-size: 26rpx;
  color: #999999;
  font-family: 'SF Mono', monospace;
}

.order-status {
  font-size: 24rpx;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-weight: 600;
}

.status-0 {
  background: #FFF3E0;
  color: #FF9800;
}

.status-1 {
  background: #E3F2FD;
  color: #2196F3;
}

.status-2 {
  background: #E8F5E9;
  color: #4CAF50;
}

.order-content {
  margin-bottom: 24rpx;
}

.service-info {
  margin-bottom: 20rpx;
}

.service-type-row {
  display: flex;
  align-items: center;
}

.service-icon {
  font-size: 48rpx;
  margin-right: 16rpx;
}

.service-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.service-type {
  font-size: 32rpx;
  color: #1A1A1A;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.service-duration {
  font-size: 24rpx;
  color: #999999;
}

.time-info {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  padding: 16rpx 20rpx;
  background: #F8F9FA;
  border-radius: 12rpx;
}

.time-label {
  font-size: 26rpx;
  color: #666666;
  margin-right: 8rpx;
}

.time-value {
  flex: 1;
  font-size: 28rpx;
  color: #75A3F8;
  font-weight: 600;
}

.service-items {
  background: #F8F9FA;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #E8E8E8;
}

.item-row:last-child {
  border-bottom: none;
}

.item-name {
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
}

.item-price {
  font-size: 28rpx;
  color: #75A3F8;
  font-weight: 600;
}

.special-requirements {
  display: flex;
  background: #FFF3E0;
  padding: 16rpx 20rpx;
  border-radius: 12rpx;
  margin-bottom: 16rpx;
  font-size: 26rpx;
}

.req-label {
  color: #F57C00;
  margin-right: 8rpx;
  font-weight: 600;
}

.req-text {
  flex: 1;
  color: #666666;
}

.address-info,
.customer-info,
.worker-info {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
  font-size: 26rpx;
}

.address-label,
.customer-label,
.worker-label {
  color: #666666;
  margin-right: 8rpx;
}

.address-value {
  flex: 1;
  color: #333333;
}

.customer-name,
.worker-name {
  color: #333333;
  margin-right: 24rpx;
}

.customer-phone,
.worker-phone {
  color: #75A3F8;
}

.worker-info {
  margin-top: 8rpx;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 2rpx solid #F0F0F0;
}

.total-price {
  display: flex;
  align-items: baseline;
}

.price-label {
  font-size: 26rpx;
  color: #666666;
  margin-right: 8rpx;
}

.price-value {
  font-size: 36rpx;
  color: #75A3F8;
  font-weight: 700;
}

.action-buttons {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.btn {
  padding: 12rpx 24rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 600;
  border: none;
}

.btn-cancel {
  background: #FFFFFF;
  color: #FF6B6B;
  border: 2rpx solid #FF6B6B;
}

.btn-worker {
  background: #FFFFFF;
  color: #75A3F8;
  border: 2rpx solid #75A3F8;
}

.btn-review {
  background: #FFFFFF;
  color: #67C23A;
  border: 2rpx solid #67C23A;
}

.btn-contact {
  background: #FFFFFF;
  color: #75A3F8;
  border: 2rpx solid #75A3F8;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 24rpx;
  opacity: 0.5;
}

.empty-text {
  font-size: 28rpx;
  color: #999999;
}

/* ========== 全局统一主题覆盖（用户-家政订单页） ========== */
.container {
  background:
    radial-gradient(circle at 14% 8%, rgba(122, 163, 255, 0.28) 0%, rgba(122, 163, 255, 0) 36%),
    linear-gradient(145deg, #e8efff 0%, #dce8ff 100%) !important;
}

.tabs-container,
.order-item,
.service-info,
.order-footer {
  background: #edf3ff !important;
  border-color: rgba(255,255,255,0.78) !important;
  box-shadow: 10rpx 10rpx 22rpx rgba(128,151,199,0.22), -10rpx -10rpx 22rpx rgba(255,255,255,0.95) !important;
}

.tab-text,
.service-type,
.price-value,
.address-value,
.customer-name,
.worker-name {
  color: #334f7c !important;
}

.order-number,
.service-duration,
.time-label,
.time-value,
.address-label,
.customer-label,
.worker-label,
.empty-text {
  color: #7890b4 !important;
}

.btn {
  min-height: 72rpx !important;
  border-radius: 999rpx !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  line-height: 1 !important;
}
</style>
