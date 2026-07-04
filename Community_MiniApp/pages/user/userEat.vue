<template>
  <view class="container">
    <view class="summary-panel summary-eat">
      <view class="summary-top">
        <view>
          <text class="summary-tag">餐饮订单</text>
          <view class="summary-title">今日餐食安排</view>
          <view class="summary-desc">按订单状态查看送餐进度，重要信息一眼就能看到。</view>
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
          <text class="card-type">餐饮配送</text>
          <text class="card-status status-0" v-if="order.orderStatus === 0">待配送</text>
          <text class="card-status status-1" v-else-if="order.orderStatus === 1">配送中</text>
          <text class="card-status status-2" v-else>已完成</text>
        </view>

        <view class="card-order-no">订单号：{{ order.id }}</view>

        <view class="hero-box eat-hero">
          <view>
            <text class="hero-title">{{ getOrderTitle(order) }}</text>
            <text class="hero-time">{{ formatTime(order.startTime) }}</text>
          </view>
          <view class="hero-price-wrap">
            <text class="hero-price-label">合计</text>
            <text class="hero-price">¥{{ order.amount }}</text>
          </view>
        </view>

        <view class="section-box list-box" v-if="order.items && order.items.length">
          <view class="section-title-row">
            <text class="dot dot-eat"></text>
            <text class="section-title">餐品清单</text>
          </view>
          <view class="food-row" v-for="(item, idx) in order.items" :key="idx">
            <view>
              <text class="food-name">{{ item.name }}</text>
              <text class="food-meta">份数 x{{ item.quantity }}</text>
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
          <text class="info-label">配送员</text>
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
            <button v-if="order.orderStatus === 1 && order.send" class="action-btn btn-contact" size="mini" @tap.stop="contactDelivery(order.send.phone)">联系配送员</button>
            <button v-if="order.orderStatus === 2" class="action-btn btn-review" size="mini" @tap.stop="reviewOrder(order.id)">评价</button>
          </view>
        </view>
      </view>

      <view class="empty-state" v-if="filteredOrders.length === 0">
        <text class="empty-icon">📋</text>
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
          <view class="detail-section">
            <text class="section-title">订单信息</text>
            <view class="detail-item"><text class="detail-label">订单号：</text><text class="detail-value">ORDER{{ selectedOrder.id ? selectedOrder.id.toString().padStart(8, '0') : '' }}</text></view>
            <view class="detail-item"><text class="detail-label">下单时间：</text><text class="detail-value">{{ formatTime(selectedOrder.startTime) }}</text></view>
            <view class="detail-item"><text class="detail-label">订单状态：</text><text class="detail-value status" :class="'status-' + selectedOrder.orderStatus">{{ getStatusText(selectedOrder.orderStatus) }}</text></view>
          </view>
          <view class="detail-section">
            <text class="section-title">客户信息</text>
            <view class="detail-item"><text class="detail-label">姓名：</text><text class="detail-value">{{ selectedOrder.user ? selectedOrder.user.name : '' }}</text></view>
            <view class="detail-item"><text class="detail-label">电话：</text><text class="detail-value">{{ selectedOrder.deliveryPhone }}</text></view>
            <view class="detail-item"><text class="detail-label">配送地址：</text><text class="detail-value">{{ selectedOrder.deliveryAddress }}</text></view>
            <view class="detail-item" v-if="selectedOrder.remark"><text class="detail-label">备注：</text><text class="detail-value">{{ selectedOrder.remark }}</text></view>
          </view>
          <view class="detail-section" v-if="selectedOrder.orderStatus === 1 && selectedOrder.send">
            <text class="section-title">配送员信息</text>
            <view class="detail-item"><text class="detail-label">姓名：</text><text class="detail-value">{{ selectedOrder.send.name }}</text></view>
            <view class="detail-item"><text class="detail-label">电话：</text><text class="detail-value">{{ selectedOrder.send.phone }}</text></view>
          </view>
          <view class="detail-section">
            <text class="section-title">商品清单</text>
            <view v-if="selectedOrder.items && selectedOrder.items.length > 0" class="food-list-container">
              <view v-for="(item, idx) in selectedOrder.items" :key="idx" class="food-item">
                <view class="food-info"><text class="food-name">{{ item.name }}</text><text class="food-price">¥{{ item.price }}</text></view>
                <view class="food-quantity">x{{ item.quantity || 1 }}</view>
              </view>
            </view>
          </view>
          <view class="detail-section">
            <text class="section-title">费用明细</text>
            <view class="detail-item total"><text class="detail-label">订单总计：</text><text class="detail-value">¥{{ selectedOrder.amount }}</text></view>
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
      //   orderStatus: Number, // 0-待接单 1-配送中 2-已完成 3-已取消
      //   user: { id: Number, name: String },
      //   send: { id: Number, name: String, phone: String }, // 配送员信息
      //   items: [{ id: Number, name: String, price: Number, quantity: Number }]
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
          url: '/user/ordersCtl/userEatOrder',
          method: 'GET'
        });
        
        uni.hideLoading();
        
        if (res.data.code === 200) {
          this.orders = res.data.data || [];
          console.log('餐饮订单列表:', this.orders);
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
    getOrderTitle(order) {
      if (!order.items || !order.items.length) return '餐饮订单已提交';
      return order.orderStatus === 0 ? '营养配餐已接单' : order.items[0].name + (order.items.length > 1 ? ' 等餐品' : '');
    },
    getStatusText(status) {
      const statusMap = {
        0: '待配送',
        1: '配送中',
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
        content: '确定要取消此订单吗？',
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
          title: '已提醒商家加快配送',
          icon: 'success'
        });
      }, 1000);
    },
    reviewOrder(orderId) {
      uni.showToast({
        title: '评价功能开发中',
        icon: 'none'
      });
      // uni.navigateTo({ url: `/pages/review/review?orderId=${orderId}&type=eat` });
    },
    contactDelivery(phone) {
      uni.showModal({
        title: '联系配送员',
        content: `是否拨打配送员电话 ${phone}？`,
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
  background: #fffdf8;
  box-shadow: 0 10rpx 24rpx rgba(233, 205, 160, 0.16);
}

.summary-eat {
  background: linear-gradient(180deg, #fffaf2 0%, #fffdf9 100%);
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
  color: #d59a5d;
  margin-bottom: 14rpx;
  font-weight: 600;
}

.summary-title {
  font-size: 56rpx;
  line-height: 1.16;
  color: #4d3726;
  font-weight: 700;
  margin-bottom: 14rpx;
}

.summary-desc {
  font-size: 28rpx;
  line-height: 1.65;
  color: #b3936f;
}

.summary-count {
  min-width: 150rpx;
  padding: 22rpx 0;
  border-radius: 999rpx;
  text-align: center;
  font-size: 38rpx;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #ffb464 0%, #f59a4f 100%);
  box-shadow: 0 10rpx 18rpx rgba(245, 154, 79, 0.22);
}

.summary-tabs {
  display: flex;
  gap: 18rpx;
  background: #fff7ec;
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
  background: linear-gradient(135deg, #ffb36a 0%, #f7a257 100%);
  box-shadow: 0 8rpx 16rpx rgba(243, 167, 94, 0.24);
}

.summary-tab-label {
  display: block;
  font-size: 32rpx;
  color: #9e7b58;
  font-weight: 700;
}

.summary-tab-count {
  display: block;
  margin-top: 10rpx;
  font-size: 28rpx;
  color: #b6a186;
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
  background: rgba(255,255,255,0.96);
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
  background: #fff3df;
  color: #d59a5d;
  font-size: 28rpx;
  font-weight: 700;
}

.card-order-no,
.hero-time,
.info-label,
.foot-label,
.food-meta,
.empty-text {
  color: #a99884;
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
  color: #e6a93a;
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
  background: #fffaf2;
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
.section-title,
.appointment-time {
  color: #4d3726;
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

.hero-price-label,
.hero-inline-label {
  display: block;
  font-size: 28rpx;
  color: #b3946f;
  margin-bottom: 8rpx;
}

.hero-price {
  font-size: 50rpx;
  color: #403126;
  font-weight: 700;
}

.section-box,
.worker-box,
.remark-box,
.appointment-box {
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

.dot-eat {
  background: #ffb36a;
}

.food-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f2e4d2;
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
  color: #ff8c4d;
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

.worker-box,
.remark-box {
  display: flex;
  flex-direction: column;
}

.remark-label {
  color: #d59a5d;
  font-size: 28rpx;
  font-weight: 700;
  margin-bottom: 10rpx;
}

.remark-value {
  color: #7f6f5e;
  font-size: 28rpx;
  line-height: 1.6;
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
