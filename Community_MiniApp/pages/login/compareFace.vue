<template>
  <view class="face-login-container">
    <!-- 顶部标题 -->
    <view class="header-section">
      <text class="title">人脸识别登录</text>
      <text class="subtitle">请拍摄或上传您的正面照片</text>
    </view>

    <!-- 手机号输入区域 -->
    <view class="phone-section">
      <view class="input-wrapper">
        <text class="input-label">手机号码</text>
        <input 
          class="phone-input" 
          v-model="phoneNumber" 
          type="number" 
          placeholder="请输入您的手机号码"
          maxlength="11"
        />
      </view>
    </view>

    <!-- 照片预览区域 -->
    <view class="photo-section">
      <view v-if="!photoPath" class="photo-placeholder" @click="showActionSheet">
        <text class="placeholder-icon">📷</text>
        <text class="placeholder-text">点击拍照或选择照片</text>
      </view>
      <view v-else class="photo-preview">
        <image :src="photoPath" mode="aspectFit" class="preview-image" />
        <view class="photo-actions">
          <text class="action-btn" @click="showActionSheet">重新拍摄</text>
        </view>
      </view>
    </view>

    <!-- 温馨提示 -->
    <view class="tips-section">
      <text class="tips-title">📋 温馨提示</text>
      <text class="tips-item">• 请保持光线充足</text>
      <text class="tips-item">• 请正面拍摄，露出完整五官</text>
      <text class="tips-item">• 请摘下口罩、墨镜等遮挡物</text>
    </view>

    <!-- 底部按钮 -->
    <view class="button-section">
      <button 
        class="submit-btn" 
        @click="handleFaceLogin"
        :disabled="!photoPath || !phoneNumber || isLoading"
      >
        {{ isLoading ? '识别中...' : '开始识别' }}
      </button>
      <button class="back-btn" @click="goBack">返回登录</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      photoPath: '', // 照片路径
      isLoading: false, // 加载状态
      phoneNumber: '' // 手机号码
    }
  },
  
  methods: {
    // 验证手机号格式
    validatePhone(phone) {
      const phoneRegex = /^1[3-9]\d{9}$/;
      return phoneRegex.test(phone);
    },

    // 显示选择菜单
    showActionSheet() {
      uni.showActionSheet({
        itemList: ['拍照', '从相册选择'],
        success: (res) => {
          if (res.tapIndex === 0) {
            this.takePhoto();
          } else if (res.tapIndex === 1) {
            this.choosePhoto();
          }
        }
      });
    },

    // 拍照
    takePhoto() {
      uni.chooseImage({
        count: 1,
        sourceType: ['camera'],
        sizeType: ['compressed'],
        success: (res) => {
          this.photoPath = res.tempFilePaths[0];
          console.log('拍照成功:', this.photoPath);
        },
        fail: (err) => {
          console.error('拍照失败:', err);
          uni.showToast({
            title: '拍照失败',
            icon: 'none',
            duration: 2000
          });
        }
      });
    },

    // 从相册选择
    choosePhoto() {
      uni.chooseImage({
        count: 1,
        sourceType: ['album'],
        sizeType: ['compressed'],
        success: (res) => {
          this.photoPath = res.tempFilePaths[0];
          console.log('选择照片成功:', this.photoPath);
        },
        fail: (err) => {
          console.error('选择照片失败:', err);
          uni.showToast({
            title: '选择照片失败',
            icon: 'none',
            duration: 2000
          });
        }
      });
    },

    // 人脸识别登录
    async handleFaceLogin() {
      if (!this.photoPath) {
        uni.showToast({
          title: '请先拍摄或选择照片',
          icon: 'none',
          duration: 2000
        });
        return;
      }

      if (!this.phoneNumber) {
        uni.showToast({
          title: '请输入手机号码',
          icon: 'none',
          duration: 2000
        });
        return;
      }

      if (!this.validatePhone(this.phoneNumber)) {
        uni.showToast({
          title: '请输入正确的手机号码',
          icon: 'none',
          duration: 2000
        });
        return;
      }

      this.isLoading = true;

      try {
        // 上传照片到后端进行人脸识别
        const resp = await uni.uploadFile({
          url: this.$baseUrl + '/api/loginCtl/faceLogin?phone='+this.phoneNumber, // 替换为您的后端接口地址
          filePath: this.photoPath,
          name: 'file',
        });
		
		console.log('完整响应:', resp);
		
		// 解析返回的JSON数据
		const result = JSON.parse(resp.data);
		console.log('解析后的数据:', result);
		
        if (result.code === 200) {
          // 人脸识别成功
          uni.showToast({
            title: '人脸识别成功！',
            icon: 'success',
            duration: 2000
          });

          // 保存登录信息
		  const userData = result.data;
		  uni.setStorageSync("token", userData.token);
		  uni.setStorageSync("userId", userData.id);
		  uni.setStorageSync("userAddress", userData.address);
		  uni.setStorageSync("communityId", userData.communityId);
		  uni.setStorageSync("userPhone", userData.phone);
		  
          // 延迟跳转到首页
          setTimeout(() => {
            uni.switchTab({
              url: '/pages/index/index'
            });
          }, 1500);
        } else if (result.code === 1) {
          // 处理两种code=1的情况
          if (result.message === '该账号未注册') {
            uni.showModal({
              title: '账号未注册',
              content: '该手机号尚未注册，是否前往注册？',
              confirmText: '去注册',
              cancelText: '取消',
              success: (res) => {
                if (res.confirm) {
                  // 跳转到注册页面
                  uni.navigateTo({
                    url: '/pages/register/register'
                  });
                }
              }
            });
          } else if (result.message === '人脸识别失败') {
            uni.showModal({
              title: '人脸识别失败',
              content: '人脸匹配度不够，请确保光线充足，正面拍摄，或重新录入人脸信息',
              confirmText: '重新拍摄',
              cancelText: '取消',
              success: (res) => {
                if (res.confirm) {
                  // 清空当前照片，重新拍摄
                  this.photoPath = '';
                }
              }
            });
          } else {
            // 其他code=1的情况
            uni.showToast({
              title: result.message || '操作失败',
              icon: 'none',
              duration: 2000
            });
          }
        } else if (result.code === 2) {
          // 未录入人脸信息
          uni.showModal({
            title: '未录入人脸信息',
            content: '您还没有录入人脸信息，请先到个人资料页面录入人脸图片',
          });
        } else {
          // 其他未知错误
          uni.showToast({
            title: result.message || '识别失败，请重试',
            icon: 'none',
            duration: 2000
          });
        }
      } catch (error) {
        console.error('人脸识别失败:', error);
        uni.showToast({
          title: '识别失败，请重试',
          icon: 'none',
          duration: 2000
        });
      } finally {
        this.isLoading = false;
      }
    },

    // 返回登录页面
    goBack() {
      uni.navigateBack();
    }
  }
}
</script>

<style scoped>
/* 整体容器 */
.face-login-container {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f0f2f5 0%, #ffffff 100%);
  padding: 40rpx;
  box-sizing: border-box;
}

/* 顶部标题 */
.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
}

.title {
  font-size: 44rpx;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 26rpx;
  color: #909399;
}

/* 照片区域 */
.photo-section {
  width: 100%;
  margin-bottom: 50rpx;
}

.photo-placeholder {
  width: 100%;
  height: 500rpx;
  background: #ffffff;
  border-radius: 16rpx;
  border: 3rpx dashed #d9d9d9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.photo-placeholder:active {
  transform: scale(0.98);
  border-color: #1890ff;
}

.placeholder-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.placeholder-text {
  font-size: 28rpx;
  color: #909399;
}

.photo-preview {
  width: 100%;
  background: #ffffff;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.preview-image {
  width: 100%;
  height: 500rpx;
}

.photo-actions {
  padding: 20rpx;
  text-align: center;
  border-top: 1rpx solid #f0f0f0;
}

.action-btn {
  font-size: 28rpx;
  color: #1890ff;
  padding: 10rpx 20rpx;
}

/* 手机号输入区域 */
.phone-section {
  margin-bottom: 40rpx;
}

.input-wrapper {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  border: 2rpx solid #f0f0f0;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: #1890ff;
  box-shadow: 0 2rpx 12rpx rgba(24, 144, 255, 0.15);
}

.input-label {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16rpx;
}

.phone-input {
  width: 100%;
  height: 80rpx;
  font-size: 32rpx;
  color: #303133;
  background: #f8f9fa;
  border: 2rpx solid #e9ecef;
  border-radius: 8rpx;
  padding: 0 20rpx;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

.phone-input:focus {
  background: #ffffff;
  border-color: #1890ff;
  outline: none;
}

.phone-input::placeholder {
  color: #909399;
  font-size: 28rpx;
}

/* 温馨提示 */
.tips-section {
  background: #fffbe6;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 50rpx;
  border-left: 4rpx solid #faad14;
}

.tips-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16rpx;
}

.tips-item {
  display: block;
  font-size: 26rpx;
  color: #606266;
  line-height: 2;
  margin-left: 20rpx;
}

/* 按钮区域 */
.button-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #1890ff 0%, #0c7cd5 100%);
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 44rpx;
  border: none;
  box-shadow: 0 6rpx 16rpx rgba(24, 144, 255, 0.35);
  transition: all 0.3s ease;
}

.submit-btn:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(24, 144, 255, 0.25);
}

.submit-btn[disabled] {
  opacity: 0.6;
}

.back-btn {
  width: 100%;
  height: 88rpx;
  background: #ffffff;
  color: #606266;
  font-size: 28rpx;
  border-radius: 44rpx;
  border: 2rpx solid #d9d9d9;
  transition: all 0.3s ease;
}

.back-btn:active {
  background: #f5f5f5;
  transform: scale(0.98);
}

/* ========== 全局统一主题覆盖（人脸登录） ========== */
.face-login-container {
  background:
    radial-gradient(circle at 16% 10%, rgba(122, 163, 255, 0.3) 0%, rgba(122, 163, 255, 0) 35%),
    linear-gradient(145deg, #e8efff 0%, #dce8ff 100%) !important;
}

.input-wrapper,
.photo-placeholder,
.photo-preview,
.tips-section,
.phone-input {
  background: #edf3ff !important;
  border: 1rpx solid rgba(255,255,255,0.78) !important;
  box-shadow: 12rpx 12rpx 24rpx rgba(128,151,199,0.22), -12rpx -12rpx 24rpx rgba(255,255,255,0.95) !important;
}

.title,
.input-label,
.tips-title {
  color: #334f7c !important;
}

.subtitle,
.placeholder-text,
.tips-item {
  color: #7890b4 !important;
}

.phone-input {
  height: 84rpx !important;
  font-size: 30rpx !important;
  padding: 0 22rpx !important;
  border-radius: 18rpx !important;
}

.submit-btn,
.back-btn {
  height: 84rpx !important;
  border-radius: 999rpx !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  line-height: 1 !important;
}

.submit-btn {
  background: linear-gradient(145deg, #84a7ff 0%, #5f86ff 100%) !important;
}

.back-btn {
  background: #edf3ff !important;
  color: #5975a3 !important;
}
</style>
