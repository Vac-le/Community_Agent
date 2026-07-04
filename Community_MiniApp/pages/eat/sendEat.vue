<template>
  <view class="service-page light-theme">
    <view class="page-shell">
      <view class="top-panel">
        <view class="hero-card hero-delivery">
          <view class="hero-deco deco-one"></view>
          <view class="hero-deco deco-two"></view>
          <view class="hero-content">
            <view class="hero-copy">
              <text class="hero-label">DELIVERY CONSOLE</text>
              <text class="hero-title">即时配送工作台</text>
            </view>
            <view class="summary-row">
              <view class="summary-card warm">
                <text class="summary-value">{{ pendingCount }}</text>
                <text class="summary-label">待接单</text>
              </view>
              <view class="summary-card sky">
                <text class="summary-value">{{ deliveringCount }}</text>
                <text class="summary-label">配送中</text>
              </view>
              <view class="summary-card mint">
                <text class="summary-value">{{ completedCount }}</text>
                <text class="summary-label">已完成</text>
              </view>
            </view>
          </view>
        </view>

        <view class="status-panel soft-card">
          <view 
            class="status-tab" 
            :class="{ active: currentTab === 'pending' }" 
            @click="switchTab('pending')"
          >
            <text class="tab-title">待接单</text>
            <text class="tab-count">{{ pendingCount }}</text>
          </view>
          <view 
            class="status-tab" 
            :class="{ active: currentTab === 'delivering' }" 
            @click="switchTab('delivering')"
          >
            <text class="tab-title">配送中</text>
            <text class="tab-count">{{ deliveringCount }}</text>
          </view>
          <view 
            class="status-tab" 
            :class="{ active: currentTab === 'completed' }" 
            @click="switchTab('completed')"
          >
            <text class="tab-title">已完成</text>
            <text class="tab-count">{{ completedCount }}</text>
          </view>
        </view>
      </view>

      <scroll-view scroll-y class="order-list" @scrolltolower="loadMore">
        <view v-if="!filteredOrders.length" class="empty-state soft-card">
          <text class="empty-icon">✦</text>
          <text class="empty-title">当前暂无{{ tabNames[currentTab] }}订单</text>
          <text class="empty-text">新订单会自动同步到这里，保持在线即可及时响应。</text>
        </view>
        
        <view v-else class="order-feed">
          <view 
            v-for="order in filteredOrders" 
            :key="order.id" 
            class="order-card soft-card"
            @click="viewOrderDetail(order)"
          >
            <view class="card-head">
              <view>
                <text class="order-kicker">ORDER</text>
                <text class="order-number">#{{ order.id }}</text>
              </view>
              <view class="order-status" :class="{
                'status-pending': order.orderStatus === 0,
                'status-delivering': order.orderStatus === 1,
                'status-completed': order.orderStatus === 2
              }">
                {{ getStatusText(order.orderStatus) }}
              </view>
            </view>

            <view class="route-card">
              <view class="route-point start">
                <text class="route-dot"></text>
                <view class="route-copy">
                  <text class="route-label">客户</text>
                  <text class="route-value">{{ order.user.name }}</text>
                </view>
              </view>
              <view class="route-line"></view>
              <view class="route-point end">
                <text class="route-dot"></text>
                <view class="route-copy">
                  <text class="route-label">送达地</text>
                  <text class="route-value clamp-1">{{ order.deliveryAddress }}</text>
                </view>
              </view>
            </view>

            <view class="info-grid">
              <view class="info-box">
                <text class="info-label">联系电话</text>
                <text class="info-value">{{ order.deliveryPhone }}</text>
              </view>
              <view class="info-box">
                <text class="info-label">下单时间</text>
                <text class="info-value">{{ formatTime(order.startTime) }}</text>
              </view>
            </view>

            <view class="items-panel">
              <view class="panel-head">
                <text class="panel-title">商品清单</text>
                <text class="panel-meta">共 {{ order.items.length }} 件</text>
              </view>
              <view v-for="item in order.items.slice(0, 2)" :key="item.id" class="item-row">
                <text class="item-name clamp-1">{{ item.name }}</text>
                <text class="item-quantity">x{{ item.quantity }}</text>
              </view>
              <text v-if="order.items.length > 2" class="more-items">还有 {{ order.items.length - 2 }} 件商品待查看</text>
            </view>

            <view class="card-footer">
              <view class="amount-block">
                <text class="amount-label">订单金额</text>
                <text class="amount-value">¥{{ order.amount }}</text>
              </view>
              
              <view class="action-buttons">
                <button 
                  v-if="order.orderStatus === 0" 
                  class="action-btn primary" 
                  @click.stop="acceptOrder(order)"
                >
                  接单
                </button>
                
                <view v-if="order.orderStatus === 1" class="delivering-actions">
                  <button class="action-btn secondary" @click.stop="contactCustomer(order)">
                    联系客户
                  </button>
                  <button class="action-btn primary" @click.stop="completeDelivery(order)">
                    确认送达
                  </button>
                </view>
                
                <button 
                  v-if="order.orderStatus === 2" 
                  class="action-btn secondary" 
                  @click.stop="viewOrderDetail(order)"
                >
                  查看详情
                </button>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>

      <view v-if="showOrderDetail" class="order-detail-modal" @click="closeOrderDetail">
        <view class="modal-content soft-card" @click.stop>
          <view class="modal-header">
            <view>
              <text class="hero-label modal-label">DELIVERY DETAIL</text>
              <text class="modal-title">订单详情 · #{{ selectedOrder.id }}</text>
            </view>
            <text class="close-btn" @click="closeOrderDetail">×</text>
          </view>
          
          <scroll-view scroll-y class="modal-body">
            <view class="detail-hero">
              <view class="detail-status" :class="{
                'status-pending': selectedOrder.orderStatus === 0,
                'status-delivering': selectedOrder.orderStatus === 1,
                'status-completed': selectedOrder.orderStatus === 2
              }">
                {{ getStatusText(selectedOrder.orderStatus) }}
              </view>
              <text class="detail-amount">¥{{ selectedOrder.amount }}</text>
            </view>

            <view class="detail-section section-shell">
              <text class="section-title">订单信息</text>
              <view class="detail-item">
                <text class="detail-label">订单编号</text>
                <text class="detail-value">#{{ selectedOrder.id }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">下单时间</text>
                <text class="detail-value">{{ formatTime(selectedOrder.startTime) }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">订单状态</text>
                <text class="detail-value">{{ getStatusText(selectedOrder.orderStatus) }}</text>
              </view>
            </view>

            <view class="detail-section section-shell">
              <text class="section-title">客户信息</text>
              <view class="detail-item">
                <text class="detail-label">姓名</text>
                <text class="detail-value">{{ selectedOrder.user ? selectedOrder.user.name : '' }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">电话</text>
                <text class="detail-value">{{ selectedOrder.deliveryPhone }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">配送地址</text>
                <text class="detail-value address-text">{{ selectedOrder.deliveryAddress }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">备注</text>
                <text class="detail-value">{{ selectedOrder.remark || '无' }}</text>
              </view>
            </view>

            <view class="detail-section section-shell">
              <view class="panel-head detail-panel-head">
                <text class="section-title no-margin">商品清单</text>
                <text class="panel-meta">{{ selectedOrder.items && selectedOrder.items.length ? selectedOrder.items.length : 0 }} 件</text>
              </view>
              <view v-if="selectedOrder.items && selectedOrder.items.length > 0" class="food-list-container">
                <view v-for="item in selectedOrder.items" :key="item.id" class="food-item">
                  <view class="food-info">
                    <text class="food-name">{{ item.name }}</text>
                    <text class="food-price">¥{{ item.price }}</text>
                  </view>
                  <view class="food-quantity">x{{ item.quantity || 1 }}</view>
                </view>
              </view>
              <view v-else class="no-items">
                <text class="no-items-text">暂无商品信息</text>
              </view>
            </view>

            <view class="detail-section section-shell">
              <text class="section-title">费用明细</text>
              <view class="detail-item total-row">
                <text class="detail-label">订单总计</text>
                <text class="detail-value amount-emphasis">¥{{ selectedOrder.amount }}</text>
              </view>
            </view>
          </scroll-view>
        </view>
      </view>

      <view class="refresh-btn" @click="refreshOrders">
        <text class="refresh-icon">↻</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'pending',
      orders: [],
      showOrderDetail: false,
      selectedOrder: {},
      loading: false,
      refreshTimer: null,
      tabNames: {
        pending: '待接单',
        delivering: '配送中',
        completed: '已完成'
      }
    }
  },
  
  computed: {
    filteredOrders() {
      return this.orders.filter(order => {
        switch (this.currentTab) {
        case 'pending':
          return order.orderStatus == 0;
        case 'delivering':
          return order.orderStatus == 1;
        case 'completed':
          return order.orderStatus == 2;
          default:
            return false;
        }
      });
    },
    pendingCount() {
      return this.orders.filter(order => order.orderStatus === 0).length;
    },
    deliveringCount() {
      return this.orders.filter(order => order.orderStatus === 1).length;
    },
    completedCount() {
      return this.orders.filter(order => order.orderStatus === 2).length;
    }
  },
  
  onLoad() {
    this.startAutoRefresh();
  },
  
  onShow() {
    this.loadOrders();
  },
  
  onUnload() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  },
  
  onPullDownRefresh() {
    uni.showToast({
      title: '刷新成功',
      icon: 'success',
      duration: 1000
    });
    setTimeout(() => {
      uni.stopPullDownRefresh();
    }, 1000);
  },
  
  methods: {
    switchTab(tab) {
      this.currentTab = tab;
    },
    
    async loadOrders() {
      try {
        uni.showLoading({ title: '加载中...' });
        
        const res = await this.$myRequest({
          url: '/user/deliveryCtl/orderList',
          method: 'GET',
        });
        if (res.data.code === 200) {
          this.orders = res.data.data || [];
		  console.log(this.orders);
        } else {
          uni.showToast({
            title: res.data.message || '加载失败',
            icon: 'error'
          });
        }
      } catch (error) {
        console.error('加载订单失败:', error);
        uni.showToast({
          title: '网络错误',
          icon: 'error'
        });
      } finally {
        uni.hideLoading();
      }
    },
    
    async refreshOrders() {
      await this.loadOrders(); 
      uni.showToast({
        title: '刷新成功',
        icon: 'success',
        duration: 1000
      });
    },
    
    startAutoRefresh() {
       this.refreshTimer = setInterval(() => {
         this.loadOrders();
       }, 30000); 
    },
    
    async acceptOrder(order) {
      try {
        uni.showModal({
          title: '确认接单',
          content: `确定要接受订单 ORDER${order.id ? order.id.toString().padStart(8, '0') : ''} 吗？`,
          success: async (res) => {
            if (res.confirm) {
              uni.showLoading({ title: '接单中...' });
              const response = await this.$myRequest({
                url: '/user/deliveryCtl/accept?orderId='+order.id,
                method: 'POST',
              });
              
              if (response.data.code === 200) {
                uni.showToast({
                  title: '接单成功',
                  icon: 'success'
                });
                const orderIndex = this.orders.findIndex(o => o.id === order.id);
                if (orderIndex !== -1) {
                  this.orders[orderIndex].orderStatus = 1;
                  this.orders[orderIndex].acceptedTime = new Date();
                }
                this.currentTab = 'delivering';
                this.closeOrderDetail();
              } else {
                uni.showToast({
                  title: response.data.message || '接单失败',
                  icon: 'error'
                });
              }
            }
          }
        });
      } catch (error) {
        console.error('接单失败:', error);
        uni.showToast({
          title: '网络错误',
          icon: 'error'
        });
      }
    },
    
    contactCustomer(order) {
      uni.showActionSheet({
        itemList: ['拨打电话', '发送短信'],
        success: (res) => {
          if (res.tapIndex === 0) {
            uni.makePhoneCall({
              phoneNumber: order.deliveryPhone
            });
          } else if (res.tapIndex === 1) {
            uni.showToast({
              title: '请手动发送短信',
              icon: 'none'
            });
          }
        }
      });
    },
    
    async completeDelivery(order) {
      try {
        uni.showModal({
          title: '确认送达',
          content: `确认订单 ORDER${order.id ? order.id.toString().padStart(8, '0') : ''} 已送达客户吗？`,
          success: async (res) => {
            if (res.confirm) {
              uni.showLoading({ title: '确认中...' });
              
              const response = await this.$myRequest({
                url: '/user/deliveryCtl/complete?orderId='+order.id,
                method: 'POST',
              });
              
              if (response.data.code === 200) {
                uni.showToast({
                  title: '配送完成',
                  icon: 'success'
                });
                
                const orderIndex = this.orders.findIndex(o => o.id === order.id);
                if (orderIndex !== -1) {
                  this.orders[orderIndex].orderStatus = 2;
                  this.orders[orderIndex].completedTime = new Date();
                }
                this.currentTab = 'completed';
                this.closeOrderDetail();
              } else {
                uni.showToast({
                  title: response.data.message || '操作失败',
                  icon: 'error'
                });
              }
            }
          }
        });
      } catch (error) {
        console.error('完成配送失败:', error);
        uni.showToast({
          title: '网络错误',
          icon: 'error'
        });
      }
    },
    
    viewOrderDetail(order) {
      this.selectedOrder = order;
      this.showOrderDetail = true;
    },
    
    closeOrderDetail() {
      this.showOrderDetail = false;
      this.selectedOrder = {};
    },
    
    loadMore() {
      console.log('加载更多订单');
    },
    
    formatTime(time) {
      if (!time) return '';
      
      let date;
      if (typeof time === 'string') {
        date = new Date(time);
      } else if (time instanceof Date) {
        date = time;
      } else {
        date = new Date(time);
      }
      
      if (isNaN(date.getTime())) {
        return '时间格式错误';
      }
      
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      
      if (diff < 60000) {
        return '刚刚';
      } else if (diff < 3600000) {
        return Math.floor(diff / 60000) + '分钟前';
      } else if (diff < 86400000) {
        return Math.floor(diff / 3600000) + '小时前';
      } else {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      }
    },
    
    getStatusText(orderStatus) {
      const statusMap = {
        0: '待接单',
        1: '配送中',
        2: '已完成'
      };
      return statusMap[orderStatus] || '未知状态';
    },
    
    getStatusClass(orderStatus) {
      const classMap = {
        0: 'status-pending',
        1: 'status-delivering', 
        2: 'status-completed'
      };
      return classMap[orderStatus] || 'status-unknown';
    },
    
  }
}
</script>

<style scoped>
.light-theme {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 216, 201, 0.7), transparent 28%),
    radial-gradient(circle at 86% 14%, rgba(205, 232, 255, 0.8), transparent 24%),
    linear-gradient(180deg, #fffaf6 0%, #f6f8ff 42%, #f4fbff 100%);
}

.page-shell {
  min-height: 100vh;
  padding: 28rpx 24rpx 140rpx;
  box-sizing: border-box;
  position: relative;
}

.soft-card {
  background: rgba(255, 255, 255, 0.92);
  border: 1rpx solid rgba(229, 235, 250, 0.95);
  box-shadow: 0 18rpx 42rpx rgba(191, 203, 230, 0.28);
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

.hero-delivery {
  background: linear-gradient(135deg, #fff3ec 0%, #f4f4ff 54%, #eef9ff 100%);
}

.hero-deco {
  position: absolute;
  border-radius: 50%;
}

.deco-one {
  width: 220rpx;
  height: 220rpx;
  right: -50rpx;
  top: -50rpx;
  background: rgba(252, 196, 164, 0.24);
}

.deco-two {
  width: 180rpx;
  height: 180rpx;
  left: -35rpx;
  bottom: -45rpx;
  background: rgba(174, 220, 255, 0.24);
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-copy {
  margin-bottom: 24rpx;
}

.hero-label,
.modal-label,
.order-kicker {
  display: block;
  font-size: 20rpx;
  letter-spacing: 4rpx;
  color: #92a4c4;
}

.hero-title {
  display: block;
  margin-top: 12rpx;
  font-size: 48rpx;
  font-weight: 700;
  color: #2d3f63;
}

.hero-subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #71819f;
}

.summary-row {
  display: flex;
  gap: 14rpx;
}

.summary-card {
  flex: 1;
  padding: 18rpx 16rpx;
  border-radius: 22rpx;
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
}

.status-tab.active {
  background: linear-gradient(135deg, #ffe5d4 0%, #e9f4ff 100%);
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
  height: calc(100vh - 340rpx);
}

.order-feed {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.empty-state {
  padding: 100rpx 42rpx;
  border-radius: 30rpx;
  text-align: center;
}

.empty-icon {
  font-size: 86rpx;
  color: #a6b7d6;
}

.empty-title {
  display: block;
  margin-top: 18rpx;
  font-size: 32rpx;
  color: #304263;
  font-weight: 600;
}

.empty-text {
  display: block;
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
.panel-head,
.detail-item,
.food-item,
.detail-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-head {
  margin-bottom: 18rpx;
}

.order-number {
  display: block;
  margin-top: 8rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #304263;
}

.order-status,
.detail-status {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.status-pending {
  background: #fff1e5;
  color: #d5873a;
}

.status-delivering {
  background: #eaf4ff;
  color: #4a84c8;
}

.status-completed {
  background: #e9fbf3;
  color: #3c9d7d;
}

.route-card {
  border-radius: 22rpx;
  padding: 22rpx;
  background: linear-gradient(135deg, #fff7f1 0%, #f4f9ff 100%);
  margin-bottom: 18rpx;
}

.route-point {
  display: flex;
  align-items: flex-start;
}

.route-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  margin-top: 10rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.route-point.start .route-dot {
  background: #f0a36d;
}

.route-point.end .route-dot {
  background: #76acd7;
}

.route-copy {
  flex: 1;
  min-width: 0;
}

.route-label,
.info-label,
.amount-label,
.detail-label,
.panel-meta {
  font-size: 22rpx;
  color: #91a0b8;
}

.route-value,
.info-value,
.detail-value,
.food-name,
.item-name {
  display: block;
  margin-top: 8rpx;
  font-size: 28rpx;
  color: #304263;
}

.route-line {
  width: 2rpx;
  height: 30rpx;
  margin: 10rpx 0 10rpx 7rpx;
  background: linear-gradient(180deg, #f0a36d, #76acd7);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14rpx;
  margin-bottom: 18rpx;
}

.info-box,
.section-shell,
.items-panel {
  border-radius: 22rpx;
  background: #f9fbff;
}

.info-box {
  padding: 18rpx 20rpx;
}

.items-panel {
  padding: 20rpx 22rpx;
  margin-bottom: 20rpx;
}

.panel-head {
  margin-bottom: 14rpx;
}

.panel-title,
.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #314466;
}

.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 0;
  border-top: 1rpx solid rgba(213, 222, 241, 0.6);
}

.item-row:first-of-type {
  border-top: none;
}

.item-quantity,
.food-quantity {
  font-size: 24rpx;
  color: #8ca0c1;
}

.more-items {
  display: block;
  margin-top: 10rpx;
  font-size: 22rpx;
  color: #8ea0bf;
}

.amount-block {
  display: flex;
  flex-direction: column;
}

.amount-value,
.detail-amount,
.amount-emphasis {
  margin-top: 8rpx;
  font-size: 40rpx;
  font-weight: 700;
  color: #e88966;
}

.action-buttons,
.delivering-actions {
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.action-btn {
  min-width: 138rpx;
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 600;
  border: none;
  padding: 0 24rpx;
}

.action-btn::after {
  border: none;
}

.primary {
  background: linear-gradient(135deg, #ffcfb8 0%, #a8d6ff 100%);
  color: #314466;
}

.secondary {
  background: #f2f6ff;
  color: #6a7a99;
}

.order-detail-modal {
  position: fixed;
  inset: 0;
  background: rgba(112, 127, 158, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28rpx;
  z-index: 999;
}

.modal-content {
  width: 100%;
  max-width: 720rpx;
  max-height: 86vh;
  border-radius: 32rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 28rpx 28rpx 22rpx;
  border-bottom: 1rpx solid #eef2fb;
}

.modal-title {
  display: block;
  margin-top: 8rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #304263;
}

.close-btn {
  width: 54rpx;
  height: 54rpx;
  border-radius: 50%;
  background: #f2f6ff;
  color: #7b8ba8;
  font-size: 34rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 22rpx;
  flex: 1;
  box-sizing: border-box;
}

.detail-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6rpx 4rpx 18rpx;
}

.detail-section {
  padding: 20rpx 22rpx;
  margin-bottom: 16rpx;
}

.detail-item {
  padding: 12rpx 0;
  border-top: 1rpx solid rgba(213, 222, 241, 0.6);
  align-items: flex-start;
}

.detail-item:first-of-type {
  border-top: none;
  padding-top: 0;
}

.detail-value {
  flex: 1;
  text-align: right;
  margin-top: 0;
}

.address-text {
  max-width: 440rpx;
  line-height: 1.6;
}

.no-margin {
  margin: 0;
}

.food-list-container {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.food-item {
  padding: 16rpx 18rpx;
  border-radius: 18rpx;
  background: #f6f9ff;
}

.food-price {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #7f98bc;
}

.no-items {
  padding: 16rpx 0 6rpx;
  text-align: center;
}

.no-items-text {
  font-size: 24rpx;
  color: #8fa0bd;
}

.refresh-btn {
  position: fixed;
  right: 28rpx;
  bottom: 56rpx;
  width: 92rpx;
  height: 92rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffd3c0 0%, #b7ddff 100%);
  box-shadow: 0 16rpx 32rpx rgba(187, 203, 230, 0.34);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 90;
}

.refresh-icon {
  font-size: 38rpx;
  color: #304263;
  font-weight: 700;
}

.clamp-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
