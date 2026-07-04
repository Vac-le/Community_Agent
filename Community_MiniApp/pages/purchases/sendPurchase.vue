<template>
  <view class="service-page light-theme">
    <view class="page-shell">
      <view class="top-panel">
        <view class="hero-card hero-procurement">
          <view class="hero-deco deco-one"></view>
          <view class="hero-deco deco-two"></view>
          <view class="hero-content">
            <view class="hero-copy">
              <text class="hero-label">ERRAND OPERATIONS</text>
              <text class="hero-title">代购任务中枢</text>
            </view>
            <view class="summary-row">
              <view class="summary-card warm">
                <text class="summary-value">{{ pendingCount }}</text>
                <text class="summary-label">待接单</text>
              </view>
              <view class="summary-card sky">
                <text class="summary-value">{{ deliveringCount }}</text>
                <text class="summary-label">代购中</text>
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
            <text class="tab-title">代购中</text>
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
          <text class="empty-title">暂无{{ tabNames[currentTab] }}代购任务</text>
          <text class="empty-text">订单到来后会自动展示，建议保持页面常驻以便及时接单。</text>
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
                <text class="order-kicker">PURCHASE ORDER</text>
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

            <view class="customer-card section-shell">
              <view class="customer-top">
                <view>
                  <text class="section-mini">委托人</text>
                  <text class="customer-name">{{ order.user.name }}</text>
                </view>
                <text class="order-time">{{ formatTime(order.startTime) }}</text>
              </view>
              <view class="contact-row">
                <text class="contact-label">电话</text>
                <text class="contact-value">{{ order.deliveryPhone }}</text>
              </view>
              <view class="contact-row">
                <text class="contact-label">地址</text>
                <text class="contact-value address">{{ order.deliveryAddress }}</text>
              </view>
            </view>

            <view class="goods-card section-shell">
              <view class="panel-head">
                <text class="panel-title">代购清单</text>
                <text class="panel-meta">{{ order.purchasesItems ? order.purchasesItems.length : 0 }} 件</text>
              </view>
              <view v-for="item in (order.purchasesItems || []).slice(0, 2)" :key="item.id" class="item-row">
                <view class="item-copy">
                  <text class="item-name clamp-1">{{ item.name }}</text>
                  <text class="item-price">¥{{ item.price }}</text>
                </view>
                <text class="item-quantity">x{{ item.quantity }}</text>
              </view>
              <text v-if="order.purchasesItems && order.purchasesItems.length > 2" class="more-items">
                另有 {{ order.purchasesItems.length - 2 }} 件待查看
              </text>
            </view>

            <view v-if="order.remark" class="remark-box">
              <text class="remark-title">备注</text>
              <text class="remark-content">{{ order.remark }}</text>
            </view>

            <view class="card-footer">
              <view class="amount-block">
                <text class="amount-label">总计</text>
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
                
                <view v-if="order.orderStatus === 1" class="delivering-buttons">
                  <button class="action-btn secondary" @click.stop="contactCustomer(order)">
                    联系客户
                  </button>
                  <button class="action-btn primary" @click.stop="completeDelivery(order)">
                    完成代购
                  </button>
                </view>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>

      <view v-if="showOrderDetail" class="modal-overlay" @click="closeOrderDetail">
        <view class="modal-content soft-card" @click.stop>
          <view class="modal-header">
            <view>
              <text class="hero-label modal-label">PURCHASE DETAIL</text>
              <text class="modal-title">代购订单详情</text>
            </view>
            <view class="close-btn" @click="closeOrderDetail">×</view>
          </view>
          
          <view class="modal-body">
            <view class="overview-strip section-shell">
              <view>
                <text class="info-label">订单编号</text>
                <text class="info-value">#{{ selectedOrder.id }}</text>
              </view>
              <view class="order-status" :class="{
                'status-pending': selectedOrder.orderStatus === 0,
                'status-delivering': selectedOrder.orderStatus === 1,
                'status-completed': selectedOrder.orderStatus === 2
              }">
                {{ getStatusText(selectedOrder.orderStatus) }}
              </view>
            </view>

            <view class="detail-section section-shell">
              <view class="section-title">订单信息</view>
              <view class="detail-row">
                <text class="detail-label">代购单号</text>
                <text class="detail-value">{{ selectedOrder.id }}</text>
              </view>
              <view class="detail-row">
                <text class="detail-label">下单时间</text>
                <text class="detail-value">{{ formatTime(selectedOrder.startTime) }}</text>
              </view>
              <view class="detail-row">
                <text class="detail-label">订单状态</text>
                <text class="detail-value">{{ getStatusText(selectedOrder.orderStatus) }}</text>
              </view>
            </view>

            <view class="detail-section section-shell">
              <view class="section-title">客户信息</view>
              <view class="detail-row">
                <text class="detail-label">客户姓名</text>
                <text class="detail-value">{{ selectedOrder.user ? selectedOrder.user.name : '' }}</text>
              </view>
              <view class="detail-row">
                <text class="detail-label">联系电话</text>
                <text class="detail-value phone-number" @click="contactCustomer(selectedOrder)">
                  {{ selectedOrder.deliveryPhone }}
                </text>
              </view>
              <view class="detail-row">
                <text class="detail-label">配送地址</text>
                <text class="detail-value address">{{ selectedOrder.deliveryAddress }}</text>
              </view>
            </view>

            <view class="detail-section section-shell">
              <view class="panel-head">
                <view class="section-title">代购清单</view>
                <text class="panel-meta">{{ selectedOrder.purchasesItems ? selectedOrder.purchasesItems.length : 0 }} 件</text>
              </view>
              <view class="food-list-container">
                <view class="food-item" v-for="item in (selectedOrder.purchasesItems || [])" :key="item.id">
                  <view class="food-info">
                    <text class="food-name">{{ item.name }}</text>
                    <text class="food-price">¥{{ item.price }}</text>
                  </view>
                  <view class="food-quantity">x{{ item.quantity || 1 }}</view>
                </view>
              </view>
            </view>

            <view class="detail-section section-shell">
              <view class="section-title">费用明细</view>
              <view class="detail-row total-row">
                <text class="detail-label">订单总计</text>
                <text class="detail-value amount-value">¥{{ selectedOrder.amount }}</text>
              </view>
            </view>

            <view v-if="selectedOrder.remark" class="detail-section section-shell">
              <view class="section-title">备注信息</view>
              <view class="remark-box detail-remark">
                <text class="remark-content">{{ selectedOrder.remark }}</text>
              </view>
            </view>
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
      currentTab: 'pending',
      orders: [],
      showOrderDetail: false,
      selectedOrder: null,
      loading: false,
      tabNames: {
        pending: '待接单',
        delivering: '代购中',
        completed: '已完成'
      }
    }
  },
  
  computed: {
    filteredOrders() {
      return this.orders.filter(order => {
        switch (this.currentTab) {
          case 'pending':
            return order.orderStatus === 0;
          case 'delivering':
            return order.orderStatus === 1;
          case 'completed':
            return order.orderStatus === 2;
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
    this.loadOrders();
    this.startAutoRefresh();
  },
  
  onShow() {
    this.refreshOrders();
	this.getPurchasesOrders();
  },
  
  onUnload() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  },
  
  onPullDownRefresh() {
    this.refreshOrders().then(() => {
      uni.stopPullDownRefresh();
    });
  },
  
  methods: {
	async getPurchasesOrders(){
			  const res = await this.$myRequest({
			  		  url:'/user/deliveryCtl/purchasesOrdersList',
			  		  method: 'GET',
			  });
			  console.log(res.data);
			  this.orders = res.data.data;
	},  
    switchTab(tab) {
      this.currentTab = tab;
    },
    
    async loadOrders() {
      if (this.loading) return;
       
      this.loading = true;
       
      try {
        await this.getPurchasesOrders();
      } catch (error) {
        console.error('加载代购订单失败:', error);
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        });
      } finally {
        this.loading = false;
      }
    },
    
    async refreshOrders() {
      console.log('刷新代购订单数据');
      await this.loadOrders();
    },
    
    startAutoRefresh() {
      this.refreshTimer = setInterval(() => {
        this.refreshOrders();
      }, 30000);
    },

    async acceptOrder(order) {
      uni.showModal({
        title: '确认接单',
        content: `确定要接受代购单 ${order.id} 吗？`,
        success: async (res) => {
          if (res.confirm) {
			const resp = await this.$myRequest({
					url:'/user/deliveryCtl/acceptPurchasesOrder?orderId='+order.id,
					method: 'POST',
			});
			if(resp.data.code==200)
			{
				order.orderStatus = 1;
			}
            uni.showToast({
              title: '接单成功',
              icon: 'success'
            });
            console.log('接单成功:', order.id);
          }
        }
      });
    },
    
    contactCustomer(order) {
      uni.makePhoneCall({
        phoneNumber: order.deliveryPhone,
        success: () => {
          console.log('拨打电话成功');
        },
        fail: (err) => {
          console.error('拨打电话失败:', err);
          uni.showToast({
            title: '拨打失败',
            icon: 'none'
          });
        }
      });
    },
    
    completeDelivery(order) {
      uni.showModal({
        title: '确认完成',
        content: `确定已完成代购单 ${order.id} 吗？`,
        success: async (res) => {
          if (res.confirm) {
            const resp = await this.$myRequest({
            	url:'/user/deliveryCtl/completePurchasesOrder?orderId='+order.id,
            	method: 'POST',
            });
			if(resp.data.code==200)
			{
				order.orderStatus = 2;
			}
            uni.showToast({
              title: '代购完成',
              icon: 'success'
            });
            console.log('代购完成:', order.id);
          }
        }
      });
    },
    
    viewOrderDetail(order) {
      this.selectedOrder = order;
      this.showOrderDetail = true;
      console.log('查看代购订单详情:', order);
    },
    
    closeOrderDetail() {
      this.showOrderDetail = false;
      this.selectedOrder = null;
    },
    
    loadMore() {
      console.log('加载更多代购订单数据');
    },
    
    formatTime(date) {
      if (!date) return '';
      
      const now = new Date();
      const orderDate = new Date(date);
      const diff = now - orderDate;
      
      if (diff < 60000) {
        return '刚刚';
      }
      
      if (diff < 3600000) {
        return Math.floor(diff / 60000) + '分钟前';
      }
      
      if (diff < 86400000) {
        return Math.floor(diff / 3600000) + '小时前';
      }
      
      return orderDate.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    getStatusText(status) {
      const statusMap = {
        0: '待接单',
        1: '代购中',
        2: '已完成'
      };
      return statusMap[status] || '未知状态';
    }
  }
}
</script>

<style scoped>
.light-theme {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 216, 201, 0.72), transparent 28%),
    radial-gradient(circle at 88% 14%, rgba(205, 232, 255, 0.8), transparent 24%),
    linear-gradient(180deg, #fffaf6 0%, #f6f8ff 42%, #f4fbff 100%);
}

.page-shell {
  min-height: 100vh;
  padding: 28rpx 24rpx 60rpx;
  box-sizing: border-box;
}

.soft-card {
  background: rgba(255, 255, 255, 0.92);
  border: 1rpx solid rgba(229, 235, 250, 0.95);
  box-shadow: 0 18rpx 42rpx rgba(191, 203, 230, 0.28);
}

.hero-card {
  position: relative;
  overflow: hidden;
  border-radius: 32rpx;
  padding: 30rpx 26rpx;
  margin-bottom: 18rpx;
}

.hero-procurement {
  background: linear-gradient(135deg, #fff3eb 0%, #f4f4ff 54%, #eefbff 100%);
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
  margin-bottom: 24rpx;
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
  height: calc(100vh - 330rpx);
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
.customer-top,
.contact-row,
.detail-row,
.food-item,
.panel-head,
.overview-strip,
.item-row {
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
  color: #304263;
}

.order-status {
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

.section-shell {
  padding: 20rpx 22rpx;
  border-radius: 22rpx;
  background: #f9fbff;
}

.customer-card,
.goods-card,
.detail-section {
  margin-bottom: 16rpx;
}

.section-mini,
.contact-label,
.amount-label,
.detail-label,
.info-label,
.panel-meta {
  font-size: 22rpx;
  color: #91a0b8;
}

.customer-name,
.contact-value,
.detail-value,
.food-name,
.info-value,
.item-name {
  display: block;
  margin-top: 8rpx;
  font-size: 28rpx;
  color: #304263;
}

.order-time,
.item-price,
.food-price {
  font-size: 22rpx;
  color: #8094b7;
}

.address {
  max-width: 430rpx;
  text-align: right;
  line-height: 1.6;
}

.item-row {
  padding: 12rpx 0;
  border-top: 1rpx solid rgba(213, 222, 241, 0.6);
  align-items: flex-start;
}

.item-row:first-of-type,
.detail-row:first-of-type {
  border-top: none;
}

.item-copy {
  flex: 1;
  min-width: 0;
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

.remark-box {
  padding: 18rpx 20rpx;
  border-radius: 20rpx;
  background: #fff7ef;
  border: 1rpx solid #ffe6d8;
  margin-bottom: 16rpx;
}

.remark-title {
  display: block;
  font-size: 22rpx;
  color: #c48a69;
}

.remark-content {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #a46f55;
}

.amount-block {
  display: flex;
  flex-direction: column;
}

.amount-value {
  margin-top: 8rpx;
  font-size: 40rpx;
  font-weight: 700;
  color: #e88966;
}

.action-buttons,
.delivering-buttons {
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.action-btn {
  min-width: 138rpx;
  height: 72rpx;
  line-height: 72rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 600;
  border: none;
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(112, 127, 158, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 32rpx;
  box-sizing: border-box;
}

.modal-content {
  width: 100%;
  max-width: 710rpx;
  max-height: 84vh;
  overflow: hidden;
  border-radius: 30rpx;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx;
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  color: #7a8aa7;
}

.modal-body {
  padding: 24rpx;
  max-height: 68vh;
  overflow-y: auto;
}

.overview-strip {
  margin-bottom: 16rpx;
}

.section-title,
.panel-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #314466;
}

.detail-row {
  padding: 12rpx 0;
  border-top: 1rpx solid rgba(213, 222, 241, 0.6);
  align-items: flex-start;
}

.phone-number {
  color: #5b87c6;
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

.detail-remark {
  margin-bottom: 0;
}

.clamp-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
