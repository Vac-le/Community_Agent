<template>
  <view class="service-page light-theme">
    <view class="page-shell">
      <view class="top-panel">
        <view class="hero-card hero-home">
          <view class="hero-deco deco-one"></view>
          <view class="hero-deco deco-two"></view>
          <view class="hero-content">
            <view class="hero-copy">
              <text class="hero-label">HOME SERVICE DESK</text>
              <text class="hero-title">家政服务工作台</text>
            </view>
            <view class="summary-row">
              <view class="summary-card warm">
                <text class="summary-value">{{ statusCounts[0] || 0 }}</text>
                <text class="summary-label">待接单</text>
              </view>
              <view class="summary-card sky">
                <text class="summary-value">{{ statusCounts[1] || 0 }}</text>
                <text class="summary-label">进行中</text>
              </view>
              <view class="summary-card mint">
                <text class="summary-value">{{ statusCounts[2] || 0 }}</text>
                <text class="summary-label">已完成</text>
              </view>
            </view>
          </view>
        </view>

        <view class="status-panel soft-card">
          <view 
            class="status-tab" 
            :class="{ active: currentStatus === 0 }" 
            @tap="selectStatus(0)"
          >
            <text class="tab-title">待接单</text>
            <text class="tab-count">{{ statusCounts[0] || 0 }}</text>
          </view>
          <view 
            class="status-tab" 
            :class="{ active: currentStatus === 1 }" 
            @tap="selectStatus(1)"
          >
            <text class="tab-title">进行中</text>
            <text class="tab-count">{{ statusCounts[1] || 0 }}</text>
          </view>
          <view 
            class="status-tab" 
            :class="{ active: currentStatus === 2 }" 
            @tap="selectStatus(2)"
          >
            <text class="tab-title">已完成</text>
            <text class="tab-count">{{ statusCounts[2] || 0 }}</text>
          </view>
        </view>
      </view>

      <scroll-view scroll-y class="order-list">
        <view v-if="filteredOrders.length === 0" class="empty-state soft-card">
          <text class="empty-icon">✦</text>
          <text class="empty-title">当前暂无订单</text>
          <text class="empty-text">新的家政服务订单到来后会自动显示在这里。</text>
        </view>

        <view v-else class="order-feed">
          <block v-for="(order, index) in filteredOrders" :key="index">
            <view class="order-card soft-card" @tap="viewOrderDetail(order)">
              <view class="card-head">
                <view>
                  <text class="order-kicker">SERVICE ORDER</text>
                  <text class="order-number">#{{ order.id }}</text>
                </view>
                <view 
                  class="order-status"
                  :class="{
                    'status-0': order.orderStatus === 0,
                    'status-1': order.orderStatus === 1,
                    'status-2': order.orderStatus === 2
                  }"
                >
                  <text>{{ getStatusText(order.orderStatus) }}</text>
                </view>
              </view>

              <view class="service-banner">
                <view>
                  <text class="service-label">服务项目</text>
                  <text class="service-name">{{ order.home.name }}</text>
                </view>
                <text class="service-type">{{ order.homeType.name }}</text>
              </view>

              <view class="detail-panel">
                <view class="detail-row">
                  <text class="detail-label">服务时间</text>
                  <text class="detail-value">{{ formatDate(order.orderDate) }}</text>
                </view>
                <view class="detail-row">
                  <text class="detail-label">服务地址</text>
                  <text class="detail-value address-text">{{ order.deliveryAddress }}</text>
                </view>
                <view class="detail-row">
                  <text class="detail-label">联系电话</text>
                  <text class="detail-value">{{ order.deliveryPhone }}</text>
                </view>
                <view class="detail-row" v-if="order.remark">
                  <text class="detail-label">备注信息</text>
                  <text class="detail-value remark">{{ order.remark }}</text>
                </view>
              </view>

              <view class="card-footer">
                <view class="amount-block">
                  <text class="amount-label">服务金额</text>
                  <text class="amount-value">¥{{ order.amount }}</text>
                </view>
                
                <view class="action-group">
                  <button 
                    v-if="order.orderStatus === 0" 
                    class="action-btn primary" 
                    @tap.stop="acceptOrder(order)"
                  >
                    接单
                  </button>
                  <button 
                    v-if="order.orderStatus === 1" 
                    class="action-btn primary" 
                    @tap.stop="completeOrder(order)"
                  >
                    完成
                  </button>
                  <button 
                    class="action-btn secondary" 
                    @tap.stop="viewOrderDetail(order)"
                  >
                    详情
                  </button>
                </view>
              </view>
            </view>
          </block>
        </view>
      </scroll-view>

      <view v-if="showOrderDetail" class="modal-overlay" @tap="closeOrderDetail">
        <view class="modal-content soft-card" @tap.stop>
          <view class="modal-header">
            <view>
              <text class="hero-label modal-label">SERVICE DETAIL</text>
              <text class="modal-title">订单详情</text>
            </view>
            <view class="close-btn" @tap="closeOrderDetail">×</view>
          </view>
          
          <view class="modal-body">
            <view class="detail-section section-shell">
              <text class="section-title">订单信息</text>
              <view class="info-row">
                <text class="info-label">订单号</text>
                <text class="info-value">{{ selectedOrder.id }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">订单状态</text>
                <text class="info-value">{{ getStatusText(selectedOrder.orderStatus) }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">下单时间</text>
                <text class="info-value">{{ formatDateTime(selectedOrder.startTime) }}</text>
              </view>
            </view>

            <view class="detail-section section-shell">
              <text class="section-title">服务信息</text>
              <view class="info-row">
                <text class="info-label">服务名称</text>
                <text class="info-value">{{ selectedOrder.home.name }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">服务时间</text>
                <text class="info-value">{{ formatDate(selectedOrder.orderDate) }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">服务金额</text>
                <text class="info-value amount">¥{{ selectedOrder.amount }}</text>
              </view>
            </view>

            <view class="detail-section section-shell">
              <text class="section-title">客户信息</text>
              <view class="info-row">
                <text class="info-label">联系电话</text>
                <text class="info-value">{{ selectedOrder.deliveryPhone }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">服务地址</text>
                <text class="info-value address-text">{{ selectedOrder.deliveryAddress }}</text>
              </view>
              <view class="info-row" v-if="selectedOrder.remark">
                <text class="info-label">备注信息</text>
                <text class="info-value">{{ selectedOrder.remark }}</text>
              </view>
            </view>
          </view>
          
          <view class="modal-footer">
            <button 
              v-if="selectedOrder.orderStatus === 0" 
              class="modal-action-btn primary" 
              @tap="acceptOrder(selectedOrder)"
            >
              接单
            </button>
            <button 
              v-if="selectedOrder.orderStatus === 1" 
              class="modal-action-btn primary" 
              @tap="completeOrder(selectedOrder)"
            >
              完成订单
            </button>
            <button class="modal-action-btn secondary" @tap="closeOrderDetail">关闭</button>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentStatus: 0,
      showOrderDetail: false,
      selectedOrder: {},
      statusCounts: {
        0: 0,
        1: 0,
        2: 0
      },
      orders: []
    }
  },
  
  computed: {
    filteredOrders() {
      return this.orders.filter(order => order.orderStatus === this.currentStatus);
    }
  },
  
  onLoad() {
    this.updateStatusCounts();
  },
  
  onShow() {
    this.updateStatusCounts();
	this.loadOrders();
  },
  
  methods: {
	async loadOrders() {
      try {
        uni.showLoading({
          title: '加载中...'
        });
        
        const res = await this.$myRequest({
          url: '/user/deliveryCtl/homeOrderList',
          method: 'GET'
        });
        uni.hideLoading();
        if (res.data.code === 200) {
          this.orders = res.data.data;
          this.updateStatusCounts();
        } else {
          uni.showToast({
            title: res.data.message || '加载失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    },
    
    updateStatusCounts() {
      this.statusCounts = {
        0: this.orders.filter(o => o.orderStatus === 0).length,
        1: this.orders.filter(o => o.orderStatus === 1).length,
        2: this.orders.filter(o => o.orderStatus === 2).length
      };
    },
    
    selectStatus(status) {
      this.currentStatus = status;
    },
    
    viewOrderDetail(order) {
      this.selectedOrder = order;
      this.showOrderDetail = true;
    },
    
    closeOrderDetail() {
      this.showOrderDetail = false;
      this.selectedOrder = {};
    },
    
    async acceptOrder(order) {
      try {
        await new Promise((resolve) => {
          uni.showModal({
            title: '确认接单',
            content: `确定要接受订单 ${order.id} 吗？`,
            success: (res) => {
              resolve(res.confirm);
            }
          });
        });
        
        uni.showLoading({
          title: '处理中...'
        });
        
        const res = await this.$myRequest({
          url: '/user/deliveryCtl/acceptHomeOrder?orderId='+order.id,
          method: 'POST',
        });
        
        uni.hideLoading();
        
        if (res.data.code === 200) {
          uni.showToast({
            title: '接单成功',
            icon: 'success'
          });
          this.closeOrderDetail();
          this.loadOrders();
        } else {
          uni.showToast({
            title: res.data.message || '接单失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.showToast({
          title: '操作失败，请重试',
          icon: 'none'
        });
      }
    },
    
    async completeOrder(order) {
      try {
        await new Promise((resolve) => {
          uni.showModal({
            title: '确认完成',
            content: `确定已完成订单 ${order.id} 的服务吗？`,
            success: (res) => {
              resolve(res.confirm);
            }
          });
        });
        uni.showLoading({
          title: '处理中...'
        });
        
        const res = await this.$myRequest({
          url: '/user/deliveryCtl/completeHomeOrder?orderId='+order.id,
          method: 'POST',
        });
        
        uni.hideLoading();
        
        if (res.data.code === 200) {
          uni.showToast({
            title: '订单已完成',
            icon: 'success'
          });
          this.closeOrderDetail();
          this.loadOrders();
        } else {
          uni.showToast({
            title: res.data.message || '操作失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.showToast({
          title: '操作失败，请重试',
          icon: 'none'
        });
      }
    },
    
    getStatusText(status) {
      const statusMap = {
        0: '待接单',
        1: '进行中',
        2: '已完成',
        3: '已取消'
      };
      return statusMap[status] || '未知';
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    
    formatDateTime(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    }
  }
}
</script>

<style scoped>
.light-theme {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 215, 192, 0.65), transparent 28%),
    radial-gradient(circle at 88% 12%, rgba(196, 231, 255, 0.8), transparent 26%),
    linear-gradient(180deg, #fffaf6 0%, #f6f8ff 42%, #f5fbff 100%);
}

.page-shell {
  min-height: 100vh;
  padding: 28rpx 24rpx 60rpx;
  box-sizing: border-box;
}

.soft-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1rpx solid rgba(226, 232, 250, 0.95);
  box-shadow: 0 18rpx 40rpx rgba(191, 203, 230, 0.28);
}

.top-panel {
  margin-bottom: 24rpx;
}

.hero-card {
  position: relative;
  overflow: hidden;
  border-radius: 32rpx;
  padding: 30rpx 26rpx;
  margin-bottom: 18rpx;
}

.hero-home {
  background: linear-gradient(135deg, #fff4ea 0%, #f6f5ff 52%, #eef9ff 100%);
}

.hero-deco {
  position: absolute;
  border-radius: 50%;
}

.deco-one {
  width: 240rpx;
  height: 240rpx;
  right: -60rpx;
  top: -40rpx;
  background: rgba(251, 202, 168, 0.28);
}

.deco-two {
  width: 180rpx;
  height: 180rpx;
  left: -30rpx;
  bottom: -50rpx;
  background: rgba(180, 216, 255, 0.24);
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-copy {
  margin-bottom: 24rpx;
}

.hero-label,
.order-kicker,
.modal-label {
  display: block;
  font-size: 20rpx;
  letter-spacing: 4rpx;
  color: #90a2c4;
}

.hero-title {
  display: block;
  margin-top: 12rpx;
  font-size: 48rpx;
  font-weight: 700;
  color: #2b395a;
}

.hero-subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #6f7f9d;
}

.summary-row {
  display: flex;
  gap: 14rpx;
}

.summary-card {
  flex: 1;
  padding: 18rpx 16rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.65);
}

.summary-card.warm { background: #fff2e8; }
.summary-card.sky { background: #edf5ff; }
.summary-card.mint { background: #edfdf7; }

.summary-value {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #33466b;
}

.summary-label {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #7f8eaa;
}

.status-panel {
  display: flex;
  gap: 12rpx;
  border-radius: 26rpx;
  padding: 10rpx;
}

.status-tab {
  flex: 1;
  border-radius: 20rpx;
  padding: 20rpx 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: transparent;
}

.status-tab.active {
  background: linear-gradient(135deg, #ffe5d4 0%, #eaf4ff 100%);
}

.tab-title {
  font-size: 24rpx;
  color: #6b7c99;
}

.tab-count {
  margin-top: 8rpx;
  font-size: 32rpx;
  font-weight: 700;
  color: #314466;
}

.order-list {
  height: calc(100vh - 330rpx);
}

.order-feed {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.empty-state {
  border-radius: 30rpx;
  padding: 100rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.empty-icon {
  font-size: 86rpx;
  color: #a7b8d7;
}

.empty-title {
  margin-top: 18rpx;
  font-size: 32rpx;
  color: #2f4164;
  font-weight: 600;
}

.empty-text {
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #8594ae;
}

.order-card {
  border-radius: 28rpx;
  padding: 24rpx;
}

.card-head,
.card-footer,
.detail-row,
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-head {
  margin-bottom: 18rpx;
}

.order-number {
  display: block;
  margin-top: 8rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #2f4164;
}

.order-status {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.status-0 {
  background: #fff1e5;
  color: #d78a3f;
}

.status-1 {
  background: #eaf4ff;
  color: #4b84c7;
}

.status-2 {
  background: #e9fbf3;
  color: #3e9f7e;
}

.service-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 22rpx;
  border-radius: 22rpx;
  background: linear-gradient(135deg, #fff7f1 0%, #f4f8ff 100%);
  margin-bottom: 18rpx;
}

.service-label,
.detail-label,
.info-label,
.amount-label {
  font-size: 22rpx;
  color: #91a0b8;
}

.service-name,
.detail-value,
.info-value {
  display: block;
  margin-top: 8rpx;
  font-size: 28rpx;
  color: #304263;
}

.service-type {
  font-size: 22rpx;
  color: #6d82a8;
  padding: 10rpx 18rpx;
  background: rgba(255, 255, 255, 0.78);
  border-radius: 999rpx;
}

.detail-panel,
.section-shell {
  padding: 20rpx 22rpx;
  border-radius: 22rpx;
  background: #f9fbff;
}

.detail-panel {
  margin-bottom: 18rpx;
}

.detail-row,
.info-row {
  padding: 12rpx 0;
  align-items: flex-start;
  border-top: 1rpx solid rgba(213, 222, 241, 0.6);
}

.detail-row:first-child,
.info-row:first-child {
  border-top: none;
  padding-top: 0;
}

.address-text {
  max-width: 430rpx;
  text-align: right;
  line-height: 1.6;
}

.remark {
  color: #c47a63;
}

.amount-block {
  display: flex;
  flex-direction: column;
}

.amount-value,
.info-value.amount {
  margin-top: 8rpx;
  font-size: 40rpx;
  font-weight: 700;
  color: #ea8b68;
}

.action-group {
  display: flex;
  gap: 12rpx;
}

.action-btn,
.modal-action-btn {
  min-width: 138rpx;
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 999rpx;
  padding: 0 24rpx;
  font-size: 24rpx;
  font-weight: 600;
  border: none;
}

.action-btn::after,
.modal-action-btn::after {
  border: none;
}

.primary {
  background: linear-gradient(135deg, #ffcfb8 0%, #a8d6ff 100%);
  color: #314466;
}

.secondary {
  background: #f2f6ff;
  color: #6b7b99;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(112, 127, 158, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30rpx;
  z-index: 999;
}

.modal-content {
  width: 100%;
  max-width: 710rpx;
  max-height: 84vh;
  overflow: hidden;
  border-radius: 32rpx;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx;
  border-bottom: 1rpx solid #eef2fb;
}

.modal-title {
  display: block;
  margin-top: 8rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #2f4164;
}

.close-btn {
  width: 54rpx;
  height: 54rpx;
  border-radius: 50%;
  background: #f2f6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  color: #7a8aa7;
}

.modal-body {
  padding: 22rpx;
  max-height: 62vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 16rpx;
}

.section-title {
  display: block;
  margin-bottom: 8rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #314466;
}

.modal-footer {
  display: flex;
  gap: 14rpx;
  padding: 24rpx 28rpx 28rpx;
  border-top: 1rpx solid #eef2fb;
}
</style>
