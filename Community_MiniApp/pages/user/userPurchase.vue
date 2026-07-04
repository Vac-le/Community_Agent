<template>
  <view class="container">
    <view class="summary-panel summary-purchase">
      <view class="summary-top">
        <view>
          <text class="summary-tag">代购订单</text>
          <view class="summary-title">日常代购进度</view>
          <view class="summary-desc">重点展示采购清单、配送信息和采购员联系方式，浏览更轻松。</view>
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
      <view class="order-card" v-for="order in filteredOrders" :key="order.id" @tap="viewOrderDetail(order)">
        <view class="card-head">
          <text class="card-type">社区代购</text>
          <text class="card-status status-0" v-if="order.orderStatus === 0">待采购</text>
          <text class="card-status status-1" v-else-if="order.orderStatus === 1">采购中</text>
          <text class="card-status status-2" v-else>已完成</text>
        </view>

        <view class="card-order-no">订单号：{{ order.id }}</view>

        <view class="hero-box purchase-hero">
          <view>
            <text class="hero-title">代购需求已提交</text>
            <text class="hero-time">{{ formatTime(order.startTime) }}</text>
          </view>
          <view class="hero-price-wrap">
            <text class="hero-price-label">预算</text>
            <text class="hero-price">¥{{ order.amount }}</text>
          </view>
        </view>

        <view class="section-box list-box" v-if="order.purchasesItems && order.purchasesItems.length">
          <view class="section-title-row">
            <text class="dot dot-purchase"></text>
            <text class="section-title">代购清单</text>
          </view>
          <view class="food-row" v-for="(item, idx) in order.purchasesItems" :key="idx">
            <view>
              <text class="food-name">{{ item.name }}</text>
              <text class="food-meta">数量 x{{ item.quantity }}</text>
            </view>
            <text class="food-price">¥{{ item.price }}</text>
          </view>
        </view>

        <view class="info-grid">
          <view class="info-box">
            <text class="info-label">送达地址</text>
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

        <view class="worker-box" v-if="order.orderStatus === 1 && order.send">
          <text class="info-label">采购员</text>
          <text class="info-value">{{ order.send.name }} {{ order.send.phone }}</text>
        </view>

        <view class="card-foot">
          <view>
            <text class="foot-label">订单金额</text>
            <text class="foot-price">¥{{ order.amount }}</text>
          </view>
          <view class="action-buttons">
            <button v-if="order.orderStatus === 0" class="action-btn btn-cancel" size="mini" @tap.stop="cancelOrder(order.id)">取消订单</button>
            <button v-if="order.orderStatus === 1" class="action-btn btn-remind" size="mini" @tap.stop="remindOrder(order.id)">催单</button>
            <button v-if="order.orderStatus === 1 && order.send" class="action-btn btn-contact" size="mini" @tap.stop="contactPurchaser(order.send.phone)">联系采购员</button>
            <button v-if="order.orderStatus === 2" class="action-btn btn-review" size="mini" @tap.stop="reviewOrder(order.id)">评价</button>
          </view>
        </view>
      </view>

      <view class="empty-state" v-if="filteredOrders.length === 0">
        <text class="empty-icon">🛒</text>
        <text class="empty-text">暂无订单</text>
      </view>
    </scroll-view>

    <view v-if="showOrderDetail" class="order-detail-modal" @tap="closeOrderDetail">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">订单详情 - ORDER{{ selectedOrder.id ? selectedOrder.id.toString().padStart(8, '0') : '' }}</text>
          <text class="close-btn" @tap="closeOrderDetail">×</text>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="detail-section"><text class="section-title">订单信息</text><view class="detail-item"><text class="detail-label">订单号：</text><text class="detail-value">ORDER{{ selectedOrder.id ? selectedOrder.id.toString().padStart(8, '0') : '' }}</text></view><view class="detail-item"><text class="detail-label">下单时间：</text><text class="detail-value">{{ formatTime(selectedOrder.startTime) }}</text></view><view class="detail-item"><text class="detail-label">订单状态：</text><text class="detail-value status" :class="'status-' + selectedOrder.orderStatus">{{ getStatusText(selectedOrder.orderStatus) }}</text></view></view>
          <view class="detail-section"><text class="section-title">客户信息</text><view class="detail-item"><text class="detail-label">姓名：</text><text class="detail-value">{{ selectedOrder.user ? selectedOrder.user.name : '' }}</text></view><view class="detail-item"><text class="detail-label">电话：</text><text class="detail-value">{{ selectedOrder.deliveryPhone }}</text></view><view class="detail-item"><text class="detail-label">配送地址：</text><text class="detail-value">{{ selectedOrder.deliveryAddress }}</text></view><view class="detail-item" v-if="selectedOrder.remark"><text class="detail-label">备注：</text><text class="detail-value">{{ selectedOrder.remark }}</text></view></view>
          <view class="detail-section" v-if="selectedOrder.orderStatus === 1 && selectedOrder.send"><text class="section-title">采购员信息</text><view class="detail-item"><text class="detail-label">姓名：</text><text class="detail-value">{{ selectedOrder.send.name }}</text></view><view class="detail-item"><text class="detail-label">电话：</text><text class="detail-value">{{ selectedOrder.send.phone }}</text></view></view>
          <view class="detail-section"><text class="section-title">代购清单</text><view v-if="selectedOrder.purchasesItems && selectedOrder.purchasesItems.length > 0" class="food-list-container"><view v-for="(item, idx) in selectedOrder.purchasesItems" :key="idx" class="food-item"><view class="food-info"><text class="food-name">{{ item.name }}</text><text class="food-price">¥{{ item.price }}</text></view><view class="food-quantity">x{{ item.quantity || 1 }}</view></view></view></view>
          <view class="detail-section"><text class="section-title">费用明细</text><view class="detail-item total"><text class="detail-label">订单总计：</text><text class="detail-value">¥{{ selectedOrder.amount }}</text></view></view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      tabs: ['待服务', '服务中', '已完成'],
      currentTab: 0,
      orders: [],
      showOrderDetail: false,
      selectedOrder: {}
      // 后端数据结构：
      // {
      //   id: Number,
      //   startTime: Date,
      //   amount: Number,
      //   deliveryAddress: String,
      //   deliveryPhone: String,
      //   remark: String,
      //   orderStatus: Number, // 0-待接单 1-采购中 2-已完成 3-已取消
      //   user: { id: Number, name: String },
      //   send: { id: Number, name: String, phone: String }, // 采购员信息
      //   purchasesItems: [{ id: Number, name: String, price: Number, quantity: Number }]
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
    this.loadOrders().then(() => {
      uni.stopPullDownRefresh();
    });
  },
  methods: {
    // 加载订单列表
    async loadOrders() {
      try {
        uni.showLoading({ title: '加载中...' });
        
        const res = await this.$myRequest({
          url: '/user/ordersCtl/userPurchaseOrder',
          method: 'GET'
        });
        
        uni.hideLoading();
        
        if (res.data.code === 200) {
          this.orders = res.data.data || [];
          console.log('代购订单列表:', this.orders);
        } else {
          uni.showToast({
            title: res.data.message || '加载失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
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
        0: '待采购',
        1: '采购中',
        2: '已完成'
      };
      return statusMap[status] || '';
    },
    viewOrderDetail(order) {
      this.selectedOrder = order;
      this.showOrderDetail = true;
    },
    
    closeOrderDetail() {
      this.showOrderDetail = false;
      this.selectedOrder = {};
    },
    cancelOrder(orderId) {
      uni.showModal({
        title: '取消订单',
        content: '确定要取消此代购订单吗？',
        success: (res) => {
          if (res.confirm) {
            uni.showLoading({ title: '处理中...' });
            setTimeout(() => {
              const index = this.orders.findIndex(o => o.id === orderId);
              if (index !== -1) {
                this.orders.splice(index, 1);
              }
              uni.hideLoading();
              uni.showToast({
                title: '订单已取消',
                icon: 'success'
              });
            }, 1000);
          }
        }
      });
    },
    remindOrder(orderId) {
      uni.showLoading({ title: '发送中...' });
      setTimeout(() => {
        uni.hideLoading();
        uni.showToast({
          title: '已提醒采购员加快进度',
          icon: 'success'
        });
      }, 1000);
    },
    reviewOrder(orderId) {
      uni.showToast({
        title: '评价功能开发中',
        icon: 'none'
      });
      // uni.navigateTo({ url: `/pages/review/review?orderId=${orderId}&type=purchase` });
    },
    contactPurchaser(phone) {
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
    },
    loadMore() {
      // 加载更多数据
      console.log('加载更多');
    },
    // 格式化时间
    formatTime(time) {
      if (!time) return '';
      const date = new Date(time);
      const now = new Date();
      const diff = now - date;
      
      // 一分钟内
      if (diff < 60000) {
        return '刚刚';
      }
      // 一小时内
      if (diff < 3600000) {
        return Math.floor(diff / 60000) + '分钟前';
      }
      // 一天内
      if (diff < 86400000) {
        return Math.floor(diff / 3600000) + '小时前';
      }
      // 超过一天，显示完整日期
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hour = String(date.getHours()).padStart(2, '0');
      const minute = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hour}:${minute}`;
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

.summary-purchase {
  background: linear-gradient(180deg, #fcfbff 0%, #ffffff 100%);
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
  color: #8f8be9;
  margin-bottom: 14rpx;
  font-weight: 600;
}

.summary-title {
  font-size: 56rpx;
  line-height: 1.16;
  color: #3a376d;
  font-weight: 700;
  margin-bottom: 14rpx;
}

.summary-desc {
  font-size: 28rpx;
  line-height: 1.65;
  color: #9f9cc4;
}

.summary-count {
  min-width: 150rpx;
  padding: 22rpx 0;
  border-radius: 999rpx;
  text-align: center;
  font-size: 38rpx;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #7c73f2 0%, #63abf6 100%);
  box-shadow: 0 10rpx 18rpx rgba(109, 133, 243, 0.22);
}

.summary-tabs {
  display: flex;
  gap: 18rpx;
  background: #f5f3ff;
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
  background: linear-gradient(135deg, #7c73f2 0%, #68a8f6 100%);
  box-shadow: 0 8rpx 16rpx rgba(117, 122, 241, 0.22);
}

.summary-tab-label {
  display: block;
  font-size: 32rpx;
  color: #7e7aa9;
  font-weight: 700;
}

.summary-tab-count {
  display: block;
  margin-top: 10rpx;
  font-size: 28rpx;
  color: #aaa5ca;
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
.info-grid {
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
  background: #f0eeff;
  color: #7e7ae5;
  font-size: 28rpx;
  font-weight: 700;
}

.card-order-no,
.hero-time,
.info-label,
.foot-label,
.food-meta,
.empty-text,
.remark-value {
  color: #9d9aba;
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
.remark-box {
  background: #f7f7ff;
  border-radius: 24rpx;
}

.hero-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 26rpx 24rpx;
  margin-bottom: 20rpx;
}

.hero-title,
.food-name,
.info-value,
.foot-price,
.section-title {
  color: #3b376b;
  font-weight: 700;
}

.hero-title {
  display: block;
  font-size: 44rpx;
  margin-bottom: 12rpx;
}

.hero-price-wrap {
  text-align: right;
}

.hero-price-label {
  display: block;
  font-size: 28rpx;
  color: #9e9bc4;
  margin-bottom: 8rpx;
}

.hero-price {
  font-size: 50rpx;
  color: #3b376b;
  font-weight: 700;
}

.section-box,
.worker-box,
.remark-box {
  padding: 24rpx;
  margin-bottom: 18rpx;
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

.dot-purchase {
  background: #8e89ef;
}

.food-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #eceafd;
}

.food-row:last-child {
  border-bottom: none;
}

.food-name {
  display: block;
  font-size: 40rpx;
  margin-bottom: 8rpx;
}

.food-price {
  font-size: 38rpx;
  color: #5d77ff;
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
  color: #8f8be9;
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

.btn-remind {
  background: #fff1dd;
  color: #d6933c;
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

.order-detail-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-height: 80%;
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #eef1f6;
}

.modal-title {
  font-size: 30rpx;
  color: #33476f;
  font-weight: 700;
}

.close-btn {
  font-size: 42rpx;
  color: #92a2c2;
}

.modal-body {
  max-height: 900rpx;
  padding: 24rpx 30rpx 34rpx;
  box-sizing: border-box;
}

.detail-section {
  margin-bottom: 24rpx;
  padding: 22rpx;
  background: #f8faff;
  border-radius: 20rpx;
}

.detail-item,
.food-item,
.food-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-item {
  margin-top: 14rpx;
  font-size: 26rpx;
}

.detail-label,
.food-quantity {
  color: #93a3c3;
}

.detail-value {
  color: #33476f;
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

.restaurant-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.restaurant-name {
  font-size: 32rpx;
  color: #1A1A1A;
  font-weight: 600;
}

.order-time {
  font-size: 24rpx;
  color: #999999;
}

.order-items {
  background: #F8F9FA;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.item-row {
  display: flex;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #E8E8E8;
}

.item-row:last-child {
  border-bottom: none;
}

.item-name {
  flex: 1;
  font-size: 28rpx;
  color: #333333;
}

.item-quantity {
  font-size: 26rpx;
  color: #999999;
  margin-right: 24rpx;
}

.item-price {
  font-size: 28rpx;
  color: #FF6B6B;
  font-weight: 600;
}


.delivery-info,
.customer-info {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
  font-size: 26rpx;
}

.delivery-label,
.customer-label {
  color: #666666;
  margin-right: 8rpx;
}

.delivery-address {
  flex: 1;
  color: #333333;
}

.customer-name {
  color: #333333;
  margin-right: 24rpx;
}

.customer-phone {
  color: #75A3F8;
}

.purchaser-person {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
  font-size: 26rpx;
}

.purchaser-label {
  color: #666666;
  margin-right: 8rpx;
}

.purchaser-name {
  color: #333333;
  margin-right: 24rpx;
}

.purchaser-phone {
  color: #75A3F8;
}

.remark-info {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16rpx;
  font-size: 26rpx;
  background: #FFF9E6;
  padding: 12rpx 20rpx;
  border-radius: 12rpx;
  margin-top: 8rpx;
}

.remark-label {
  color: #F57C00;
  margin-right: 8rpx;
  font-weight: 600;
}

.remark-text {
  flex: 1;
  color: #666666;
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
  color: #FF6B6B;
  font-weight: 700;
}

.action-buttons {
  display: flex;
  gap: 16rpx;
}

.btn {
  padding: 12rpx 28rpx;
  border-radius: 20rpx;
  font-size: 26rpx;
  font-weight: 600;
  border: none;
}

.btn-cancel {
  background: #FFFFFF;
  color: #FF6B6B;
  border: 2rpx solid #FF6B6B;
}

.btn-remind {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
  color: #FFFFFF;
}

.btn-review {
  background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%);
  color: #FFFFFF;
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

/* 订单详情弹窗 */
.order-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 700rpx;
  max-height: 80%;
  background: white;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx;
  border-bottom: 2rpx solid #e0e0e0;
}

.modal-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.close-btn {
  font-size: 50rpx;
  color: #999;
  line-height: 1;
}

.modal-body {
  flex: 1;
  padding: 40rpx;
  box-sizing: border-box;
  overflow-x: hidden;
}

.detail-section {
  margin-bottom: 40rpx;
  width: 100%;
  box-sizing: border-box;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.detail-item {
  display: flex;
  margin-bottom: 15rpx;
  font-size: 28rpx;
  width: 100%;
  box-sizing: border-box;
}

.detail-item.total {
  border-top: 1rpx solid #f0f0f0;
  padding-top: 15rpx;
  font-weight: bold;
}

.detail-label {
  color: #606266;
  width: 160rpx;
  flex-shrink: 0;
  font-weight: 500;
}

.detail-value {
  color: #303133;
  flex: 1;
  word-wrap: break-word;
  word-break: break-all;
  overflow: hidden;
  font-weight: 500;
}

.detail-value.status {
  padding: 4rpx 12rpx;
  border-radius: 10rpx;
  font-size: 24rpx;
  font-weight: bold;
  max-width: 120rpx;
  text-align: center;
}

.food-list-container {
  width: 100%;
  border: 2rpx solid #e0e0e0;
  border-radius: 8rpx;
  padding: 20rpx;
  box-sizing: border-box;
}

.food-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 0;
  border-bottom: 2rpx solid #e0e0e0;
  width: 100%;
  box-sizing: border-box;
}

.food-item:last-child {
  border-bottom: none;
}

.food-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.food-name {
  font-size: 30rpx;
  color: #333;
  margin-bottom: 8rpx;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.food-price {
  font-size: 26rpx;
  color: #e74c3c;
  font-weight: bold;
}

.food-quantity {
  font-size: 26rpx;
  color: #666;
  margin-left: 20rpx;
  font-weight: 500;
  min-width: 50rpx;
  text-align: right;
  flex-shrink: 0;
}

/* ========== 全局统一主题覆盖（用户-代购订单页） ========== */
.container {
  background:
    radial-gradient(circle at 14% 8%, rgba(122, 163, 255, 0.28) 0%, rgba(122, 163, 255, 0) 36%),
    linear-gradient(145deg, #e8efff 0%, #dce8ff 100%) !important;
}

.tabs-container,
.order-item,
.modal-content,
.detail-section,
.order-header,
.order-footer {
  background: #edf3ff !important;
  border-color: rgba(255,255,255,0.78) !important;
  box-shadow: 10rpx 10rpx 22rpx rgba(128,151,199,0.22), -10rpx -10rpx 22rpx rgba(255,255,255,0.95) !important;
}

.tab-text,
.restaurant-name,
.price-value,
.modal-title,
.section-title,
.detail-value,
.item-name {
  color: #334f7c !important;
}

.order-number,
.order-time,
.delivery-label,
.customer-label,
.purchaser-label,
.detail-label,
.empty-text,
.item-quantity,
.item-price {
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
/* ========== 全局统一主题覆盖（用户-代购订单页） ========== */
.container {
  background:
    radial-gradient(circle at 12% 8%, rgba(122, 163, 255, 0.26) 0%, rgba(122, 163, 255, 0) 34%),
    linear-gradient(145deg, #e8efff 0%, #dce8ff 100%) !important;
}

.tabs-container,
.order-item,
.modal-content {
  background: rgba(237, 243, 255, 0.94) !important;
  border: 1rpx solid rgba(255,255,255,0.78) !important;
  box-shadow: 10rpx 10rpx 22rpx rgba(128,151,199,0.18), -10rpx -10rpx 22rpx rgba(255,255,255,0.92) !important;
}

.order-items,
.remark-info {
  border: 1rpx solid rgba(255,255,255,0.68);
}

.tab-text,
.restaurant-name,
.price-value,
.delivery-address,
.customer-name,
.purchaser-name,
.modal-title,
.section-title,
.detail-value,
.food-name {
  color: #334f7c !important;
}

.order-number,
.order-time,
.delivery-label,
.customer-label,
.price-label,
.remark-text,
.empty-text,
.detail-label,
.food-price,
.food-quantity,
.purchaser-label,
.purchaser-phone {
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
