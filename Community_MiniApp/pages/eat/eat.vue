<template>
  <view class="eat-page">
    <view class="hero-banner">
      <view class="hero-mask"></view>
      <view class="hero-inner">
        <text class="hero-kicker">COMMUNITY DINING</text>
        <text class="hero-title">餐饮服务</text>
        <text class="hero-desc">社区食堂每日供应，现做现送，健康又省心</text>
      </view>
    </view>

    <view class="eat-body">
      <view class="filter-card glass-card">
        <view class="card-header">
          <view>
            <text class="card-title">菜品分类</text>
            <text class="card-subtitle">切换分类后，右侧菜品会即时筛选</text>
          </view>
          <text class="count-pill">{{ filteredFoods.length }}款</text>
        </view>

        <scroll-view scroll-x class="category-scroll" show-scrollbar="false">
          <view class="category-line">
            <view
              class="category-pill"
              :class="{ active: currentCategory.id === 0 }"
              @click="selectCategory(all)"
            >
              <text class="pill-emoji">🍽</text>
              <text class="pill-text">全部</text>
            </view>
            <view
              v-for="category in foodTypes"
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
        <text class="selected-name">{{ currentCategory.name || '全部菜品' }}</text>
      </view>

      <view class="food-section">
        <view class="section-header">
          <view>
            <text class="section-title">今日菜品</text>
            <text class="section-subtitle">点击查看详情，点击加号可快速加入购物车</text>
          </view>
        </view>

        <view v-if="filteredFoods.length" class="food-grid">
          <view
            v-for="food in filteredFoods"
            :key="food.id"
            class="food-card"
            @click="selectFood(food)"
          >
            <image class="food-image" :src="food.img || defaultFoodImage" mode="aspectFill"></image>
            <view class="food-content">
              <view class="food-top">
                <text class="food-name">{{ food.name }}</text>
                <text class="food-price">¥{{ Number(food.price).toFixed(2) }}</text>
              </view>
              <text class="food-tag">{{ getFoodTag(food) }}</text>
              <text class="food-desc">{{ food.description || '社区精选菜品，口味稳定，适合日常订餐。' }}</text>
            </view>
            <view class="add-fab" @click.stop="addToCart(food)">
              <text class="add-symbol">+</text>
            </view>
          </view>
        </view>

        <view v-else class="empty-card glass-card">
          <text class="empty-mark">🍲</text>
          <text class="empty-title">暂无菜品</text>
          <text class="empty-tip">当前分类下还没有可展示的菜品</text>
        </view>
      </view>
    </view>

    <view v-if="cartItems.length > 0" class="floating-cart" :class="{ expanded: cartExpanded }">
      <view class="cart-summary" @click="toggleCart">
        <view class="cart-main">
          <view class="cart-badge">{{ cartItems.length }}</view>
          <view>
            <text class="cart-title">购物车</text>
            <text class="cart-subtitle">总计 ¥{{ totalPrice.toFixed(2) }}</text>
          </view>
        </view>
        <text class="cart-arrow" :class="{ rotated: cartExpanded }">⌃</text>
      </view>

      <view v-show="cartExpanded" class="cart-detail">
        <view class="delivery-box">
          <view class="delivery-head">
            <text class="delivery-title">配送信息</text>
            <text class="delivery-edit" @click="editDeliveryInfo">修改</text>
          </view>
          <text class="delivery-line">地址：{{ deliveryAddress || '请先设置配送地址' }}</text>
          <text class="delivery-line">电话：{{ deliveryPhone || '请先设置联系电话' }}</text>
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
        <view class="cart-submit" @click="placeOrder">立即下单</view>
      </view>
    </view>

    <view v-if="showOrderModal" class="modal-mask" @click="hideOrderModal">
      <view class="order-modal" @click.stop>
        <view class="modal-top">
          <view>
            <text class="modal-title">确认下单</text>
            <text class="modal-subtitle">请核对菜品、配送信息与备注</text>
          </view>
          <view class="modal-close" @click="hideOrderModal">×</view>
        </view>

        <view class="order-overview">
          <view class="overview-card">
            <text class="overview-label">商品件数</text>
            <text class="overview-value">{{ cartItems.length }}件</text>
          </view>
          <view class="overview-card total-card">
            <text class="overview-label">订单金额</text>
            <text class="overview-value price">¥{{ totalPrice.toFixed(2) }}</text>
          </view>
        </view>

        <view class="modal-section">
          <text class="section-caption">商品清单</text>
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
          <text class="section-caption">配送信息</text>
          <view class="field-card">
            <text class="field-label">配送地址</text>
            <textarea
              class="field-area address-field"
              v-model="deliveryAddress"
              placeholder="请输入配送地址"
              maxlength="100"
              :show-confirm-bar="false"
            ></textarea>
          </view>
          <view class="field-card">
            <text class="field-label">联系电话</text>
            <input
              class="field-input"
              type="number"
              v-model="deliveryPhone"
              placeholder="请输入联系电话"
              maxlength="11"
            />
          </view>
        </view>

        <view class="modal-section">
          <text class="section-caption">订单备注</text>
          <view class="field-card">
            <textarea
              class="field-area"
              v-model="orderRemark"
              placeholder="请输入口味偏好、少辣少盐等备注（选填）"
              maxlength="100"
              :show-confirm-bar="false"
            ></textarea>
            <text class="remark-count">{{ orderRemark.length }}/100</text>
          </view>
        </view>

        <view class="modal-actions">
          <view class="modal-btn light" @click="hideOrderModal">取消</view>
          <view class="modal-btn strong" @click="confirmOrder">确认下单</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      all: { id: 0, name: '全部菜品' },
      currentCategory: { id: 0, name: '全部菜品' },
      cartExpanded: false,
      foodTypes: [],
      foods: [],
      cartItems: [],
      deliveryAddress: '',
      deliveryPhone: '',
      showOrderModal: false,
      orderRemark: '',
      defaultFoodImage: 'https://dummyimage.com/320x320/e8eef6/7a8ba1.png&text=%E7%A4%BE%E5%8C%BA%E9%A4%90%E9%A5%AE'
    }
  },

  computed: {
    filteredFoods() {
      const foods = Array.isArray(this.foods) ? this.foods : [];
      if (this.currentCategory.id === 0) {
        return foods;
      }
      return foods.filter(food => {
        const foodTypeId = food.foodType && typeof food.foodType === 'object'
          ? food.foodType.id
          : (food.foodTypeId !== undefined ? food.foodTypeId : food.foodType);
        return String(foodTypeId) === String(this.currentCategory.id);
      });
    },

    totalPrice() {
      return this.cartItems.reduce((total, item) => total + (Number(item.price) * item.quantity), 0);
    }
  },

  onLoad() {
    this.loadUserInfo();
  },

  onShow() {
    this.loadUserInfo();
    this.getFoodList();
    this.getFoodTypes();
  },

  methods: {
    loadUserInfo() {
      this.deliveryAddress = uni.getStorageSync('userAddress') || '';
      this.deliveryPhone = uni.getStorageSync('userPhone') || '';
    },

    async getFoodList() {
      const res = await this.$myRequest({
        url: '/user/ordersCtl/foodList',
        method: 'GET'
      });
      const responseData = res && res.data ? res.data : {};
      this.foods = Array.isArray(responseData.data) ? responseData.data.map(item => ({
        ...item,
        id: item.id,
        name: item.name || '',
        description: item.description || '',
        img: item.img || '',
        price: Number(item.price) || 0,
        foodType: item.foodType,
        foodTypeId: item.foodTypeId
      })) : [];
    },

    async getFoodTypes() {
      const res = await this.$myRequest({
        url: '/user/ordersCtl/foodTypes',
        method: 'GET'
      });
      const responseData = res && res.data ? res.data : {};
      this.foodTypes = Array.isArray(responseData.data) ? responseData.data : [];
    },

    selectCategory(category) {
      this.currentCategory = category;
    },

    selectFood(food) {
      uni.showModal({
        title: food.name,
        content: `${food.description || '社区精选菜品'}\n价格: ¥${Number(food.price).toFixed(2)}/份`,
        confirmText: '加入购物车',
        success: (res) => {
          if (res.confirm) {
            this.addToCart(food);
          }
        }
      });
    },

    getCategoryEmoji(name) {
      const text = name || '';
      if (text.includes('汤')) return '🥣';
      if (text.includes('粥')) return '🍚';
      if (text.includes('甜')) return '🍮';
      if (text.includes('菜')) return '🥬';
      if (text.includes('肉')) return '🍖';
      if (text.includes('主食')) return '🍛';
      return '🍽';
    },

    getFoodTag(food) {
      if (food.foodType && typeof food.foodType === 'object' && food.foodType.name) {
        return food.foodType.name;
      }
      const matched = this.foodTypes.find(item => String(item.id) === String(food.foodTypeId || food.foodType));
      return matched && matched.name ? matched.name : '营养配餐';
    },

    toggleCart() {
      this.cartExpanded = !this.cartExpanded;
    },

    addToCart(food) {
      const existingItem = this.cartItems.find(item => item.id === food.id);
      if (existingItem) {
        existingItem.quantity += 1;
      } else {
        this.cartItems.push({
          id: food.id,
          name: food.name,
          price: Number(food.price),
          quantity: 1
        });
        this.cartExpanded = true;
      }

      uni.showToast({
        title: '已添加到购物车',
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

    placeOrder() {
      if (this.cartItems.length === 0) {
        uni.showToast({
          title: '购物车为空',
          icon: 'none'
        });
        return;
      }
      this.showOrderModal = true;
    },

    hideOrderModal() {
      this.showOrderModal = false;
      this.orderRemark = '';
    },

    async confirmOrder() {
      await this.submitOrder();
    },

    editDeliveryInfo() {
      uni.navigateTo({
        url: '/pages/userInfo/userInfo'
      });
    },

    async submitOrder() {
      try {
        uni.showLoading({
          title: '下单中...'
        });

        const userId = uni.getStorageSync('userId');
        if (!userId) {
          uni.hideLoading();
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          });
          return;
        }

        if (!this.deliveryAddress || !this.deliveryPhone) {
          uni.hideLoading();
          uni.showModal({
            title: '配送信息不完整',
            content: '请先设置配送地址和联系电话',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) {
                uni.navigateTo({
                  url: '/pages/userInfo/userInfo'
                });
              }
            }
          });
          return;
        }

        const orderData = {
          userId: parseInt(userId),
          communityId: uni.getStorageSync('communityId'),
          amount: this.totalPrice,
          deliveryAddress: this.deliveryAddress,
          deliveryPhone: this.deliveryPhone,
          remark: this.orderRemark,
          orderStatus: 0,
          orderItems: this.cartItems.map(item => ({
            foodId: item.id,
            quantity: item.quantity
          }))
        };

        const res = await this.$myRequest({
          url: '/user/ordersCtl/createOrder',
          method: 'POST',
          data: orderData
        });

        uni.hideLoading();

        if (res.data.code === 200) {
          uni.showToast({
            title: '下单成功',
            icon: 'success'
          });
          this.cartItems = [];
          this.cartExpanded = false;
          this.hideOrderModal();
        } else {
          uni.showToast({
            title: res.data.message || '下单失败',
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
    }
  }
}
</script>

<style>
.eat-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(71, 209, 172, 0.18), transparent 24%),
    linear-gradient(180deg, #0f2e2f 0%, #174448 28%, #eef4f3 28%, #eef4f3 100%);
  padding-bottom: 260rpx;
  box-sizing: border-box;
}

.hero-banner {
  position: relative;
  min-height: 360rpx;
  padding-top: var(--status-bar-height, 0px);
  background-image: url('https://bpic.588ku.com/back_pic/06/12/10/946230530305816.jpg');
  background-size: cover;
  background-position: center;
  overflow: hidden;
}

.hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(9, 32, 33, 0.88), rgba(23, 68, 72, 0.46));
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
  color: rgba(228, 255, 248, 0.72);
  margin-bottom: 14rpx;
}

.hero-title {
  font-size: 58rpx;
  color: #f5fffb;
  font-weight: 800;
  margin-bottom: 12rpx;
}

.hero-desc {
  font-size: 25rpx;
  line-height: 1.7;
  color: rgba(232, 248, 243, 0.9);
}

.eat-body {
  margin-top: -24rpx;
  position: relative;
  z-index: 2;
  padding: 0 22rpx;
}

.glass-card {
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(18rpx);
  border: 1rpx solid rgba(21, 77, 70, 0.08);
  border-radius: 28rpx;
  box-shadow: 0 16rpx 40rpx rgba(17, 60, 57, 0.1);
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
  color: #123634;
  font-weight: 800;
}

.card-subtitle,
.section-subtitle,
.modal-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #67817e;
}

.count-pill {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: #123634;
  color: #effcf7;
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
  background: #f7fcfa;
  border: 1rpx solid rgba(25, 90, 82, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.category-pill.active {
  background: linear-gradient(135deg, #103733 0%, #1c7c68 100%);
  box-shadow: 0 12rpx 28rpx rgba(16, 55, 51, 0.22);
}

.category-pill.active .pill-text,
.category-pill.active .pill-emoji {
  color: #effffb;
}

.pill-emoji {
  font-size: 38rpx;
}

.pill-text {
  font-size: 24rpx;
  color: #28524d;
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
  color: #6d8783;
}

.selected-name {
  font-size: 28rpx;
  color: #0f312f;
  font-weight: 700;
}

.food-section {
  margin-top: 28rpx;
}

.food-grid {
  margin-top: 18rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.food-card {
  position: relative;
  display: flex;
  gap: 18rpx;
  padding: 18rpx;
  border-radius: 28rpx;
  background: #ffffff;
  box-shadow: 0 12rpx 30rpx rgba(18, 54, 52, 0.08);
}

.food-image {
  width: 190rpx;
  height: 190rpx;
  border-radius: 22rpx;
  flex-shrink: 0;
  background: #dbe8e4;
}

.food-content {
  flex: 1;
  min-width: 0;
  padding-right: 52rpx;
}

.food-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14rpx;
}

.food-name {
  flex: 1;
  font-size: 31rpx;
  line-height: 1.4;
  color: #153836;
  font-weight: 700;
}

.food-price {
  font-size: 32rpx;
  color: #ff9f45;
  font-weight: 800;
}

.food-tag {
  display: inline-flex;
  align-self: flex-start;
  margin-top: 12rpx;
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: rgba(21, 94, 80, 0.08);
  color: #27665a;
  font-size: 20rpx;
}

.food-desc {
  margin-top: 14rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #667f7b;
}

.add-fab {
  position: absolute;
  right: 18rpx;
  bottom: 18rpx;
  width: 62rpx;
  height: 62rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffb14a 0%, #ff8d33 100%);
  box-shadow: 0 12rpx 22rpx rgba(255, 149, 58, 0.24);
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
  color: #173a37;
  font-weight: 700;
}

.empty-tip {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #718885;
}

.floating-cart {
  position: fixed;
  left: 22rpx;
  right: 22rpx;
  bottom: 24rpx;
  border-radius: 28rpx;
  background: rgba(12, 31, 29, 0.96);
  box-shadow: 0 20rpx 36rpx rgba(10, 27, 26, 0.26);
  color: #f3fffb;
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
  background: linear-gradient(135deg, #ffb14a, #ff8f33);
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
  color: rgba(234, 255, 248, 0.76);
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
  border-top: 1rpx solid rgba(236, 255, 249, 0.08);
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
  color: #89e0c7;
}

.delivery-line {
  display: block;
  margin-top: 12rpx;
  font-size: 23rpx;
  color: rgba(235, 255, 248, 0.86);
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
  border-bottom: 1rpx solid rgba(236, 255, 249, 0.06);
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
  color: #f3fffb;
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
  background: linear-gradient(135deg, #ffb14a, #ff8d33);
}

.step-count {
  font-size: 24rpx;
  min-width: 26rpx;
  text-align: center;
}

.cart-item-price,
.cart-total {
  font-size: 28rpx;
  color: #ffb14a;
  font-weight: 700;
}

.cart-submit {
  min-width: 188rpx;
  padding: 18rpx 0;
  text-align: center;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1ec99a 0%, #13896d 100%);
  color: #f5fffb;
  font-size: 28rpx;
  font-weight: 700;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(6, 22, 20, 0.5);
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
  background: #f6fbf9;
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
  box-shadow: 0 10rpx 24rpx rgba(20, 73, 67, 0.06);
}

.total-card {
  background: linear-gradient(135deg, #153d3a 0%, #1f7660 100%);
}

.overview-label {
  display: block;
  font-size: 22rpx;
  color: #748986;
}

.overview-value {
  display: block;
  margin-top: 10rpx;
  font-size: 34rpx;
  color: #153836;
  font-weight: 800;
}

.total-card .overview-label,
.total-card .overview-value,
.overview-value.price {
  color: #f6fffb;
}

.modal-section {
  margin-top: 24rpx;
}

.section-caption {
  display: block;
  margin-bottom: 14rpx;
  font-size: 26rpx;
  color: #183a37;
  font-weight: 700;
}

.modal-list,
.field-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 20rpx;
  box-shadow: 0 10rpx 24rpx rgba(20, 73, 67, 0.05);
}

.modal-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #edf4f1;
}

.modal-item:last-child {
  border-bottom: none;
}

.modal-item-name {
  flex: 1;
  font-size: 26rpx;
  color: #173936;
}

.modal-item-right {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.modal-item-count,
.modal-item-price,
.field-label,
.remark-count {
  font-size: 23rpx;
  color: #6d8481;
}

.field-card {
  margin-top: 14rpx;
}

.field-label {
  display: block;
  margin-bottom: 12rpx;
}

.field-input,
.field-area {
  width: 100%;
  border-radius: 18rpx;
  background: #f5faf8;
  padding: 18rpx;
  box-sizing: border-box;
  font-size: 25rpx;
  color: #173936;
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
  background: #e7efec;
  color: #47615d;
}

.modal-btn.strong {
  background: linear-gradient(135deg, #1fc89b 0%, #157b64 100%);
  color: #f7fffc;
}

.modal-close {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: #eaf2ef;
  color: #355653;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
}
</style>
