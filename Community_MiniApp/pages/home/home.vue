<template>
  <view class="home-page">
    <view class="hero-banner">
      <view class="hero-mask"></view>
      <view class="hero-inner">
        <text class="hero-kicker">HOME CARE SERVICE</text>
        <text class="hero-title">家政服务</text>
        <text class="hero-desc">专业家政上门，清洁、护理、收纳等服务一键预约</text>
      </view>
    </view>

    <view class="home-body">
      <view class="filter-card glass-card">
        <view class="card-header">
          <view>
            <text class="card-title">服务分类</text>
            <text class="card-subtitle">按服务类型快速筛选，点击卡片查看详情</text>
          </view>
          <text class="count-pill">{{ filteredServices.length }}项</text>
        </view>

        <scroll-view scroll-x class="category-scroll" show-scrollbar="false">
          <view class="category-line">
            <view
              class="category-pill"
              :class="{ active: currentCategory.id === 0 }"
              @click="selectCategory(allCategory)"
            >
              <text class="pill-emoji">🏠</text>
              <text class="pill-text">全部</text>
            </view>
            <view
              v-for="category in serviceCategories"
              :key="category.id"
              class="category-pill"
              :class="{ active: currentCategory.id === category.id }"
              @click="selectCategory(category)"
            >
              <text class="pill-emoji">{{ getCategoryEmoji(category.name) }}</text>
              <text class="pill-text">{{ category.name }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <view class="selected-bar glass-card">
        <text class="selected-label">当前分类</text>
        <text class="selected-name">{{ currentCategory.name || '全部服务' }}</text>
      </view>

      <view class="service-section">
        <view class="section-header">
          <view>
            <text class="section-title">精选服务</text>
            <text class="section-subtitle">点击查看详情，右下角可快速加入预约清单</text>
          </view>
        </view>

        <view v-if="filteredServices.length" class="service-grid">
          <view
            v-for="service in filteredServices"
            :key="service.id"
            class="service-card"
            @click="selectService(service)"
          >
            <image class="service-image" :src="service.img || defaultServiceImage" mode="aspectFill"></image>
            <view class="service-content">
              <view class="service-top">
                <text class="service-name">{{ service.name }}</text>
                <text class="service-price">¥{{ Number(service.price).toFixed(2) }}</text>
              </view>
              <text class="service-tag">{{ getServiceTag(service) }}</text>
              <text class="service-desc">{{ service.description || '专业家政团队上门服务，省时省力更安心。' }}</text>
            </view>
            <view class="add-fab" @click.stop="addToCart(service)">
              <text class="add-symbol">+</text>
            </view>
          </view>
        </view>

        <view v-else class="empty-card glass-card">
          <text class="empty-mark">🧺</text>
          <text class="empty-title">暂无服务</text>
          <text class="empty-tip">当前分类下还没有可展示的家政服务</text>
        </view>
      </view>
    </view>

    <view v-if="cartItems.length > 0" class="floating-cart" :class="{ expanded: cartExpanded }">
      <view class="cart-summary" @click="toggleCart">
        <view class="cart-main">
          <view class="cart-badge">{{ cartItems.length }}</view>
          <view>
            <text class="cart-title">预约清单</text>
            <text class="cart-subtitle">预计金额 ¥{{ totalPrice.toFixed(2) }}</text>
          </view>
        </view>
        <text class="cart-arrow" :class="{ rotated: cartExpanded }">⌃</text>
      </view>

      <view v-show="cartExpanded" class="cart-detail">
        <view class="delivery-box">
          <view class="delivery-head">
            <text class="delivery-title">联系信息</text>
            <text class="delivery-edit" @click="editContactInfo">修改</text>
          </view>
          <text class="delivery-line">地址：{{ bookingForm.address || '请先设置服务地址' }}</text>
          <text class="delivery-line">电话：{{ bookingForm.phone || '请先设置联系电话' }}</text>
          <text class="delivery-line">预约日期：{{ bookingForm.date || '请选择上门日期' }}</text>
        </view>

        <view class="cart-items">
          <view v-for="item in cartItems" :key="item.id" class="cart-item">
            <view class="cart-item-left">
              <text class="cart-item-name">{{ item.name }}</text>
              <view class="cart-stepper">
                <view class="step-btn" @click.stop="decreaseQuantity(item)">−</view>
                <text class="step-count">{{ item.quantity }}</text>
                <view class="step-btn plus" @click.stop="increaseQuantity(item)">+</view>
              </view>
            </view>
            <text class="cart-item-price">¥{{ (item.price * item.quantity).toFixed(2) }}</text>
          </view>
        </view>
      </view>

      <view class="cart-bottom">
        <text class="cart-total">合计 ¥{{ totalPrice.toFixed(2) }}</text>
        <view class="cart-submit" @click="placeOrder">立即预约</view>
      </view>
    </view>

    <view v-if="showOrderModal" class="modal-mask" @click="hideOrderModal">
      <view class="order-modal" @click.stop>
        <view class="modal-top">
          <view>
            <text class="modal-title">确认预约</text>
            <text class="modal-subtitle">请核对服务项目、上门信息与备注</text>
          </view>
          <view class="modal-close" @click="hideOrderModal">×</view>
        </view>

        <view class="order-overview">
          <view class="overview-card">
            <text class="overview-label">服务数量</text>
            <text class="overview-value">{{ cartItems.length }}项</text>
          </view>
          <view class="overview-card total-card">
            <text class="overview-label">预计金额</text>
            <text class="overview-value price">¥{{ totalPrice.toFixed(2) }}</text>
          </view>
        </view>

        <view class="modal-section">
          <text class="section-caption">服务清单</text>
          <view class="modal-list">
            <view v-for="item in cartItems" :key="item.id" class="modal-item">
              <text class="modal-item-name">{{ item.name }}</text>
              <view class="modal-item-right">
                <text class="modal-item-count">x{{ item.quantity }}</text>
                <text class="modal-item-price">¥{{ (item.price * item.quantity).toFixed(2) }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="modal-section">
          <text class="section-caption">上门信息</text>
          <view class="field-card">
            <text class="field-label">预约日期</text>
            <picker mode="date" :value="bookingForm.date" @change="onDateChange">
              <view class="picker-box">
                <text :class="bookingForm.date ? 'picker-text filled' : 'picker-text'">{{ bookingForm.date || '请选择服务日期' }}</text>
                <text class="picker-arrow">›</text>
              </view>
            </picker>
          </view>
          <view class="field-card">
            <text class="field-label">联系电话</text>
            <input
              class="field-input"
              type="number"
              v-model="bookingForm.phone"
              placeholder="请输入联系电话"
              maxlength="11"
            />
          </view>
          <view class="field-card">
            <text class="field-label">服务地址</text>
            <textarea
              class="field-area address-field"
              v-model="bookingForm.address"
              placeholder="请输入详细服务地址"
              maxlength="100"
              :show-confirm-bar="false"
            ></textarea>
          </view>
        </view>

        <view class="modal-section">
          <text class="section-caption">特殊要求</text>
          <view class="field-card">
            <textarea
              class="field-area"
              v-model="bookingForm.requirements"
              placeholder="可填写时间偏好、注意事项等（选填）"
              maxlength="100"
              :show-confirm-bar="false"
            ></textarea>
            <text class="remark-count">{{ bookingForm.requirements.length }}/100</text>
          </view>
        </view>

        <view class="modal-actions">
          <view class="modal-btn light" @click="hideOrderModal">取消</view>
          <view class="modal-btn strong" @click="confirmOrder">确认预约</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      allCategory: { id: 0, name: '全部服务' },
      currentCategory: { id: 0, name: '全部服务' },
      cartExpanded: false,
      serviceCategories: [],
      homeServices: [],
      cartItems: [],
      showOrderModal: false,
      bookingForm: {
        date: '',
        phone: '',
        address: '',
        requirements: ''
      },
      defaultServiceImage: 'https://dummyimage.com/320x320/f2ede6/9b7b59.png&text=%E5%AE%B6%E6%94%BF%E6%9C%8D%E5%8A%A1'
    }
  },

  computed: {
    filteredServices() {
      const services = Array.isArray(this.homeServices) ? this.homeServices : [];
      if (this.currentCategory.id === 0) {
        return services;
      }
      return services.filter(service => {
        const typeId = service.homeType && typeof service.homeType === 'object'
          ? service.homeType.id
          : (service.homeTypeId !== undefined ? service.homeTypeId : service.homeType);
        return String(typeId) === String(this.currentCategory.id);
      });
    },

    totalPrice() {
      return this.cartItems.reduce((total, item) => total + Number(item.price) * item.quantity, 0);
    }
  },

  onLoad() {
    this.currentCategory = this.allCategory;
    this.loadUserContactInfo();
  },

  onShow() {
    this.getHomeTypes();
    this.getHomeList();
    this.loadUserContactInfo();
  },

  methods: {
    async getHomeList() {
      const res = await this.$myRequest({
        url: '/user/ordersCtl/homeList',
        method: 'GET'
      });
      const responseData = res && res.data ? res.data : {};
      this.homeServices = Array.isArray(responseData.data) ? responseData.data.map(item => ({
        ...item,
        id: item.id,
        name: item.name || '',
        description: item.description || '',
        img: item.img || '',
        price: Number(item.price) || 0,
        homeType: item.homeType,
        homeTypeId: item.homeTypeId
      })) : [];
    },

    async getHomeTypes() {
      const res = await this.$myRequest({
        url: '/user/ordersCtl/homeTypes',
        method: 'GET'
      });
      const responseData = res && res.data ? res.data : {};
      this.serviceCategories = Array.isArray(responseData.data) ? responseData.data : [];
    },

    loadUserContactInfo() {
      this.bookingForm.phone = uni.getStorageSync('userPhone') || '';
      this.bookingForm.address = uni.getStorageSync('userAddress') || '';
    },

    selectCategory(category) {
      this.currentCategory = category;
    },

    selectService(service) {
      uni.showModal({
        title: service.name,
        content: `${service.description || '专业家政服务'}\n价格: ¥${Number(service.price).toFixed(2)}/次`,
        confirmText: '加入预约清单',
        success: (res) => {
          if (res.confirm) {
            this.addToCart(service);
          }
        }
      });
    },

    getCategoryEmoji(name) {
      const text = name || '';
      if (text.includes('清洁')) return '🧼';
      if (text.includes('保洁')) return '🧽';
      if (text.includes('收纳')) return '🪄';
      if (text.includes('护理')) return '🩺';
      if (text.includes('维修')) return '🛠';
      if (text.includes('做饭')) return '🍳';
      return '🏠';
    },

    getServiceTag(service) {
      if (service.homeType && typeof service.homeType === 'object' && service.homeType.name) {
        return service.homeType.name;
      }
      const matched = this.serviceCategories.find(item => String(item.id) === String(service.homeTypeId || service.homeType));
      return matched && matched.name ? matched.name : '家政服务';
    },

    toggleCart() {
      this.cartExpanded = !this.cartExpanded;
    },

    addToCart(service) {
      const existingItem = this.cartItems.find(item => item.id === service.id);
      if (existingItem) {
        existingItem.quantity += 1;
      } else {
        this.cartItems.push({
          id: service.id,
          name: service.name,
          price: Number(service.price),
          quantity: 1
        });
        this.cartExpanded = true;
      }

      uni.showToast({
        title: '已加入预约清单',
        icon: 'success'
      });
    },

    increaseQuantity(item) {
      item.quantity += 1;
    },

    decreaseQuantity(item) {
      if (item.quantity > 1) {
        item.quantity -= 1;
      } else {
        this.cartItems = this.cartItems.filter(cartItem => cartItem.id !== item.id);
      }
    },

    editContactInfo() {
      uni.navigateTo({
        url: '/pages/userInfo/userInfo'
      });
    },

    onDateChange(e) {
      this.bookingForm.date = e.detail.value;
    },

    placeOrder() {
      if (this.cartItems.length === 0) {
        uni.showToast({
          title: '预约清单为空',
          icon: 'none'
        });
        return;
      }
      this.showOrderModal = true;
    },

    hideOrderModal() {
      this.showOrderModal = false;
      this.bookingForm.requirements = '';
    },

    async confirmOrder() {
      await this.submitOrder();
    },

    async submitOrder() {
      if (!this.bookingForm.date) {
        uni.showToast({ title: '请选择预约日期', icon: 'none' });
        return;
      }

      if (!this.bookingForm.phone) {
        uni.showToast({ title: '请输入联系电话', icon: 'none' });
        return;
      }

      if (!this.bookingForm.address) {
        uni.showToast({ title: '请输入服务地址', icon: 'none' });
        return;
      }

      try {
        uni.showLoading({ title: '提交中...' });

        const userId = uni.getStorageSync('userId');
        const communityId = uni.getStorageSync('communityId');

        if (!userId || !communityId) {
          uni.hideLoading();
          uni.showToast({ title: '请先登录', icon: 'none' });
          setTimeout(() => {
            uni.navigateTo({ url: '/pages/login/login' });
          }, 1500);
          return;
        }

        const firstItem = this.cartItems[0];
        const unitPrice = Number(firstItem.price) || 0;
        const amount = this.totalPrice;

        const res = await this.$myRequest({
          url: '/user/ordersCtl/createHomeOrder',
          method: 'POST',
          data: {
            userId: userId,
            communityId: communityId,
            homeId: firstItem.id,
            amount: amount || unitPrice,
            orderDate: this.bookingForm.date,
            deliveryPhone: this.bookingForm.phone,
            deliveryAddress: this.bookingForm.address,
            remark: this.buildRemark()
          }
        });

        uni.hideLoading();

        if (res.data.code === 200 || res.data.success) {
          uni.showToast({ title: '预约成功', icon: 'success' });
          this.cartItems = [];
          this.cartExpanded = false;
          this.hideOrderModal();
        } else {
          uni.showToast({
            title: res.data.message || '预约失败，请重试',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        uni.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
      }
    },

    buildRemark() {
      const cartSummary = this.cartItems.map(item => `${item.name}x${item.quantity}`).join('，');
      if (this.bookingForm.requirements) {
        return `预约项目：${cartSummary}；特殊要求：${this.bookingForm.requirements}`;
      }
      return `预约项目：${cartSummary}`;
    }
  }
}
</script>

<style>
.home-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(228, 181, 123, 0.2), transparent 26%),
    linear-gradient(180deg, #3e2a1f 0%, #7b573e 28%, #f5f0e8 28%, #f5f0e8 100%);
  padding-bottom: 260rpx;
  box-sizing: border-box;
}

.hero-banner {
  position: relative;
  min-height: 360rpx;
  padding-top: var(--status-bar-height, 0px);
  background-image: url('https://news11.oss-cn-chengdu.aliyuncs.com/%E5%AE%B6%E6%94%BF.jpg');
  background-size: cover;
  background-position: center;
  overflow: hidden;
}

.hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(54, 35, 22, 0.88), rgba(132, 94, 58, 0.42));
}

.hero-inner {
  position: relative;
  z-index: 1;
  min-height: 360rpx;
  padding: 58rpx 28rpx 44rpx;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  box-sizing: border-box;
}

.hero-kicker {
  font-size: 20rpx;
  letter-spacing: 6rpx;
  color: rgba(255, 245, 229, 0.74);
  margin-bottom: 14rpx;
}

.hero-title {
  font-size: 58rpx;
  color: #fff8f0;
  font-weight: 800;
  margin-bottom: 12rpx;
}

.hero-desc {
  font-size: 25rpx;
  line-height: 1.7;
  color: rgba(255, 243, 231, 0.9);
}

.home-body {
  margin-top: -24rpx;
  position: relative;
  z-index: 2;
  padding: 0 22rpx;
}

.glass-card {
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(18rpx);
  border: 1rpx solid rgba(98, 67, 42, 0.08);
  border-radius: 28rpx;
  box-shadow: 0 16rpx 40rpx rgba(67, 44, 24, 0.1);
}

.filter-card {
  padding: 26rpx 22rpx;
}

.card-header,
.section-header,
.delivery-head,
.modal-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18rpx;
}

.card-title,
.section-title,
.modal-title {
  display: block;
  font-size: 34rpx;
  color: #4b311f;
  font-weight: 800;
}

.card-subtitle,
.section-subtitle,
.modal-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #8a715c;
}

.count-pill {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: #4b311f;
  color: #fff8f0;
  font-size: 22rpx;
}

.category-scroll {
  white-space: nowrap;
  margin-top: 24rpx;
}

.category-line {
  display: inline-flex;
  gap: 16rpx;
  padding-right: 12rpx;
}

.category-pill {
  min-width: 156rpx;
  padding: 18rpx 16rpx;
  border-radius: 22rpx;
  background: #fffaf4;
  border: 1rpx solid rgba(104, 73, 44, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.category-pill.active {
  background: linear-gradient(135deg, #523521 0%, #a26f42 100%);
  box-shadow: 0 12rpx 28rpx rgba(82, 53, 33, 0.22);
}

.category-pill.active .pill-text,
.category-pill.active .pill-emoji {
  color: #fff9f1;
}

.pill-emoji {
  font-size: 38rpx;
}

.pill-text {
  font-size: 24rpx;
  color: #64462d;
  text-align: center;
  white-space: normal;
}

.selected-bar {
  margin-top: 20rpx;
  padding: 20rpx 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.selected-label {
  font-size: 22rpx;
  color: #88715f;
}

.selected-name {
  font-size: 28rpx;
  color: #4a301f;
  font-weight: 700;
}

.service-section {
  margin-top: 28rpx;
}

.service-grid {
  margin-top: 18rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.service-card {
  position: relative;
  display: flex;
  gap: 18rpx;
  padding: 18rpx;
  border-radius: 28rpx;
  background: #ffffff;
  box-shadow: 0 12rpx 30rpx rgba(75, 49, 31, 0.08);
}

.service-image {
  width: 190rpx;
  height: 190rpx;
  border-radius: 22rpx;
  flex-shrink: 0;
  background: #eadfce;
}

.service-content {
  flex: 1;
  min-width: 0;
  padding-right: 52rpx;
}

.service-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14rpx;
}

.service-name {
  flex: 1;
  font-size: 31rpx;
  line-height: 1.4;
  color: #4f3320;
  font-weight: 700;
}

.service-price {
  font-size: 32rpx;
  color: #d8892a;
  font-weight: 800;
}

.service-tag {
  display: inline-flex;
  align-self: flex-start;
  margin-top: 12rpx;
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: rgba(123, 87, 62, 0.08);
  color: #7a573e;
  font-size: 20rpx;
}

.service-desc {
  margin-top: 14rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #826d5d;
}

.add-fab {
  position: absolute;
  right: 18rpx;
  bottom: 18rpx;
  width: 62rpx;
  height: 62rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #f0b561 0%, #d68a31 100%);
  box-shadow: 0 12rpx 22rpx rgba(214, 138, 49, 0.24);
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-symbol {
  color: #fff;
  font-size: 40rpx;
  line-height: 1;
}

.empty-card {
  margin-top: 18rpx;
  padding: 80rpx 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-mark {
  font-size: 54rpx;
}

.empty-title {
  margin-top: 18rpx;
  font-size: 30rpx;
  color: #4f3320;
  font-weight: 700;
}

.empty-tip {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #8c7564;
}

.floating-cart {
  position: fixed;
  left: 22rpx;
  right: 22rpx;
  bottom: 24rpx;
  border-radius: 28rpx;
  background: rgba(45, 28, 17, 0.96);
  box-shadow: 0 20rpx 36rpx rgba(45, 28, 17, 0.26);
  color: #fff9f2;
  overflow: hidden;
  z-index: 99;
}

.cart-summary,
.cart-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22rpx 24rpx;
}

.cart-main {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.cart-badge {
  width: 58rpx;
  height: 58rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #f0b561, #d8892a);
  color: #fff;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
}

.cart-subtitle {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: rgba(255, 242, 229, 0.76);
}

.cart-arrow {
  font-size: 28rpx;
  transform: rotate(0deg);
  transition: all 0.2s ease;
}

.cart-arrow.rotated {
  transform: rotate(180deg);
}

.cart-detail {
  padding: 0 24rpx 8rpx;
  border-top: 1rpx solid rgba(255, 244, 235, 0.08);
}

.delivery-box {
  margin-top: 18rpx;
  padding: 22rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.06);
}

.delivery-title {
  font-size: 28rpx;
  font-weight: 700;
}

.delivery-edit {
  font-size: 24rpx;
  color: #f0c38c;
}

.delivery-line {
  display: block;
  margin-top: 12rpx;
  font-size: 23rpx;
  color: rgba(255, 245, 236, 0.86);
  line-height: 1.6;
}

.cart-items {
  margin-top: 18rpx;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 1rpx solid rgba(255, 244, 235, 0.06);
}

.cart-item:last-child {
  border-bottom: none;
}

.cart-item-left {
  flex: 1;
  min-width: 0;
}

.cart-item-name {
  display: block;
  font-size: 27rpx;
  color: #fff9f2;
  font-weight: 600;
}

.cart-stepper {
  margin-top: 12rpx;
  display: flex;
  align-items: center;
  gap: 14rpx;
}

.step-btn {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.step-btn.plus {
  background: linear-gradient(135deg, #f0b561, #d8892a);
}

.step-count {
  font-size: 24rpx;
  min-width: 26rpx;
  text-align: center;
}

.cart-item-price,
.cart-total {
  font-size: 28rpx;
  color: #f0b561;
  font-weight: 700;
}

.cart-submit {
  min-width: 188rpx;
  padding: 18rpx 0;
  text-align: center;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #b07b46 0%, #8a5a2f 100%);
  color: #fff9f2;
  font-size: 28rpx;
  font-weight: 700;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(32, 20, 12, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 26rpx;
  box-sizing: border-box;
  z-index: 199;
}

.order-modal {
  width: 100%;
  max-height: 86vh;
  overflow-y: auto;
  border-radius: 32rpx;
  background: #fbf7f2;
  padding: 28rpx;
  box-sizing: border-box;
}

.order-overview {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.overview-card {
  padding: 24rpx;
  border-radius: 24rpx;
  background: #ffffff;
  box-shadow: 0 10rpx 24rpx rgba(75, 49, 31, 0.06);
}

.total-card {
  background: linear-gradient(135deg, #523521 0%, #a26f42 100%);
}

.overview-label {
  display: block;
  font-size: 22rpx;
  color: #8a7564;
}

.overview-value {
  display: block;
  margin-top: 10rpx;
  font-size: 34rpx;
  color: #4f3320;
  font-weight: 800;
}

.total-card .overview-label,
.total-card .overview-value,
.overview-value.price {
  color: #fff9f2;
}

.modal-section {
  margin-top: 24rpx;
}

.section-caption {
  display: block;
  margin-bottom: 14rpx;
  font-size: 26rpx;
  color: #4f3320;
  font-weight: 700;
}

.modal-list,
.field-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 20rpx;
  box-shadow: 0 10rpx 24rpx rgba(75, 49, 31, 0.05);
}

.modal-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f0e8de;
}

.modal-item:last-child {
  border-bottom: none;
}

.modal-item-name {
  flex: 1;
  font-size: 26rpx;
  color: #4f3320;
}

.modal-item-right {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.modal-item-count,
.modal-item-price,
.field-label,
.remark-count,
.picker-text {
  font-size: 23rpx;
  color: #8b7360;
}

.field-card {
  margin-top: 14rpx;
}

.field-label {
  display: block;
  margin-bottom: 12rpx;
}

.field-input,
.field-area,
.picker-box {
  width: 100%;
  border-radius: 18rpx;
  background: #faf5ef;
  padding: 18rpx;
  box-sizing: border-box;
  font-size: 25rpx;
  color: #4f3320;
}

.picker-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.picker-text.filled {
  color: #4f3320;
}

.picker-arrow {
  font-size: 30rpx;
  color: #a08061;
}

.address-field {
  min-height: 120rpx;
}

.field-area {
  min-height: 140rpx;
}

.remark-count {
  display: block;
  text-align: right;
  margin-top: 10rpx;
}

.modal-actions {
  margin-top: 28rpx;
  display: flex;
  gap: 16rpx;
}

.modal-btn {
  flex: 1;
  text-align: center;
  padding: 22rpx 0;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.modal-btn.light {
  background: #efe7de;
  color: #6a5544;
}

.modal-btn.strong {
  background: linear-gradient(135deg, #b07b46 0%, #8a5a2f 100%);
  color: #fff9f2;
}

.modal-close {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: #f2e9df;
  color: #6b5647;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
}
</style>
