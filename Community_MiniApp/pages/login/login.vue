<template>
  <view class="login-container">
    <view class="auth-card">
      <view class="title-wrap">
        <text class="title-main">智慧社区</text>
      </view>

      <view class="form-section">
        <view class="input-row">
          <text class="input-icon">👤</text>
          <input
            class="input-field"
            type="number"
            placeholder="User name"
            v-model="phoneNumber"
          />
        </view>

        <view class="input-row">
          <text class="input-icon">🔒</text>
          <input
            class="input-field"
            type="password"
            password
            placeholder="Password"
            v-model="password"
          />
        </view>

        <view class="forgot-wrap">
          <text class="forgot-text" @click="goToRegister">注册账号</text>
        </view>

        <button class="login-button" @click="phoneLogin">登录</button>

        <view class="face-wrap">
          <text class="face-link" @click="goFaceLogin">人脸识别登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        phoneNumber: '',
        password: ''
      }
    },
    methods: {
      // 手机号登录
      async phoneLogin() {
        if (!this.phoneNumber) {
          uni.showToast({ title: '请输入手机号', icon: 'none', duration: 2000 });
          return;
        }
        if (!this.password) {
          uni.showToast({ title: '请输入密码', icon: 'none', duration: 2000 });
          return;
        }

        uni.showLoading({ title: '登录中...', mask: true });
        setTimeout(() => uni.hideLoading(), 1500);

        const resp = await this.$myRequest({
          url: 'api/loginCtl/login',
          method: 'POST',
          data: {
            phone: this.phoneNumber,
            password: this.password,
          }
        });

        if (resp.data.code == 200) {
          uni.showToast({ title: '登录成功', icon: 'success', duration: 2000 });
          uni.setStorageSync('token', resp.data.data.token);
          uni.setStorageSync('userId', resp.data.data.id);
          uni.setStorageSync('userAddress', resp.data.data.address);
          uni.setStorageSync('communityId', resp.data.data.communityId);
          uni.setStorageSync('cityId', resp.data.data.cityId);
          uni.setStorageSync('userPhone', resp.data.data.phone);
          uni.switchTab({ url: '/pages/index/index' });
        }

        if (resp.data.code == 1) {
          uni.showToast({ title: '账号或密码错误', icon: 'none', duration: 2000 });
        }
      },
      goFaceLogin() {
        uni.navigateTo({ url: '/pages/login/compareFace' });
      },
      goToRegister() {
        uni.navigateTo({ url: '/pages/register/register' });
      }
    }
  }
</script>

<style>
.login-container {
  height: 100vh;
  width: 100%;
  padding: 0;
  background: linear-gradient(135deg, #b5bdf6 0%, #9fc9ef 46%, #78b8e8 100%);
  display: flex;
}

.auth-card {
  width: 100%;
  min-height: 100vh;
  border-radius: 0;
  padding: 30rpx 24rpx 80rpx;
  background:
    radial-gradient(circle at 12% 8%, rgba(255,255,255,0.42) 0%, rgba(255,255,255,0) 42%),
    linear-gradient(160deg, rgba(235,246,255,0.92) 0%, rgba(176,221,248,0.82) 55%, rgba(101,173,220,0.78) 100%);
  box-shadow: none;
}

.title-wrap {
  margin: 48rpx 0 64rpx;
  display: flex;
  justify-content: center;
}

.title-main {
  font-size: 58rpx;
  letter-spacing: 2rpx;
  font-weight: 800;
  color: #557389;
  text-align: center;
}

.form-section {
  margin-top: 40rpx;
}

.input-row {
  width: 100%;
  box-sizing: border-box;
  height: 86rpx;
  border-radius: 999rpx;
  background: rgba(236, 246, 253, 0.86);
  border: 1rpx solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 10rpx 20rpx rgba(116, 156, 190, 0.20);
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  margin-bottom: 26rpx;
}

.input-icon {
  width: 34rpx;
  margin-right: 14rpx;
  font-size: 24rpx;
  opacity: 0.55;
}

.input-field {
  flex: 1;
  height: 100%;
  font-size: 28rpx;
  color: #5c788f;
  background: transparent;
}

.forgot-wrap {
  display: flex;
  justify-content: flex-end;
  margin: 14rpx 6rpx 90rpx;
}

.forgot-text {
  font-size: 27rpx;
  color: #5f7e96;
  font-weight: 600;
}

.login-button {
  width: 100%;
  height: 90rpx;
  border-radius: 999rpx;
  border: 1rpx solid rgba(255,255,255,0.82);
  background: linear-gradient(145deg, #8ea8ff 0%, #698df4 100%);
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 700;
  box-shadow: 0 12rpx 20rpx rgba(111, 151, 185, 0.20);
}

.face-wrap {
  margin-top: 28rpx;
  display: flex;
  justify-content: center;
}

.face-link {
  font-size: 26rpx;
  color: #6f8ea4;
}
</style>
