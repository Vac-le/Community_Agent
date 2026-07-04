<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <text class="header-title">个人资料</text>
      <text class="edit-button" @tap="toggleEditMode">编辑</text>
    </view>

    <!-- 用户信息卡片 -->
    <view class="info-card">
      <!-- 头像区域 -->
      <view class="avatar-section" @click="uploadAvatar">
        <image class="user-avatar" :src="userInfo.avatar" mode="aspectFill"></image>
        <text class="upload-tip">点击更换头像</text>
      </view>

      <!-- 人脸图片区域 -->
      <view class="face-image-section">
        <text class="section-title">人脸识别图片</text>
        <view class="face-image-container">
          <view class="face-image-wrapper" @click="chooseFaceImageSource">
            <image v-if="userInfo.faceImage" class="face-image" :src="userInfo.faceImage" mode="aspectFill"></image>
            <view v-else class="face-image-placeholder">
              <text class="placeholder-icon">📷</text>
              <text class="placeholder-text">点击添加人脸图片</text>
            </view>
          </view>
          <text class="face-image-tip">用于身份验证，请确保图片清晰</text>
        </view>
      </view>

      <!-- 基本信息表单 -->
      <view class="info-form">
        <view class="form-item">
          <text class="form-label">姓名:</text>
          <view v-if="isEditMode" class="form-input-wrapper">
            <input class="form-input" v-model="editForm.name" placeholder="请输入姓名" />
          </view>
          <text v-else class="form-value">{{userInfo.name}}</text>
        </view>

        <view class="form-item">
          <text class="form-label">性别:</text>
          <view v-if="isEditMode" class="form-radio-wrapper">
            <label class="radio-label" @tap="selectGender('男')">
              <radio value="男" :checked="editForm.gender === '男'" />男
            </label>
            <label class="radio-label" @tap="selectGender('女')">
              <radio value="女" :checked="editForm.gender === '女'" />女
            </label>
          </view>
          <text v-else class="form-value">{{userInfo.gender}}</text>
        </view>

        <view class="form-item">
          <text class="form-label">年龄:</text>
          <view v-if="isEditMode" class="form-input-wrapper">
            <input class="form-input" v-model.number="editForm.age" type="number" placeholder="请输入年龄" />
          </view>
          <text v-else class="form-value">{{userInfo.age}}岁</text>
        </view>

        <view class="form-item">
          <text class="form-label">手机号码:</text>
          <view v-if="isEditMode" class="form-input-wrapper">
            <input class="form-input" v-model="editForm.phone" type="number" placeholder="请输入手机号码" />
          </view>
          <text v-else class="form-value">{{userInfo.phone}}</text>
        </view>

        <view class="form-item">
          <text class="form-label">联系地址:</text>
          <view v-if="isEditMode" class="form-input-wrapper">
            <input class="form-input" v-model="editForm.address" placeholder="请输入联系地址" />
          </view>
          <text v-else class="form-value">{{userInfo.address}}</text>
        </view>
      </view>

      <!-- 保存按钮（编辑模式下显示） -->
      <view class="button-section" v-if="isEditMode">
        <button class="cancel-button" @tap="cancelEdit">取消</button>
        <button class="save-button" type="primary" @tap="saveUserInfo">保存</button>
      </view>
    </view>

    <!-- 注意事项 -->
    <view class="notice-section">
      <text class="notice-title">温馨提示</text>
      <text class="notice-content">1. 请确保个人信息真实有效，以便我们为您提供更好的服务
2. 如有特殊健康状况，请在健康档案中详细说明</text>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        isEditMode: false,
        userInfo: {
          name: "",
          gender: '',
          age: "",
          phone: '',
          address: '',
          avatar: '/static/logo.png',
          faceImage: '' // 人脸识别图片
        },
        editForm: {}
      }
    },
    onLoad() {
      // 初始化编辑表单
      this.resetEditForm();
	  this.getInfo();
    },
    methods: {
	  async getInfo(){
		  const res = await this.$myRequest({
		  			  url:'user/userInfoCtl/userInfo',
		  			  method: 'GET',
		  });
		  console.log(res.data);
		  this.userInfo = res.data.data;
		  this.userInfo.avatar = res.data.data.img;
		  this.userInfo.faceImage = res.data.data.userFace || ''; // 获取人脸图片
	  },
      // 返回上一页
      backToUser() {
        uni.navigateBack();
      },
      
      // 切换编辑模式
      toggleEditMode() {
        this.isEditMode = !this.isEditMode;
        if (this.isEditMode) {
          // 进入编辑模式时，复制用户信息到编辑表单
          this.resetEditForm();
        }
      },
      
      // 重置编辑表单
      resetEditForm() {
        this.editForm = {
          ...this.userInfo
        };
      },
      
      // 选择性别
      selectGender(gender) {
        this.editForm.gender = gender;
      },
      
      // 取消编辑
      cancelEdit() {
        this.isEditMode = false;
        this.resetEditForm();
      },
      
      // 保存用户信息
      saveUserInfo() {
        // 简单的表单验证
        if (!this.editForm.name) {
          uni.showToast({
            title: '请输入姓名',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        if (!this.editForm.phone || this.editForm.phone.length !== 11) {
          uni.showToast({
            title: '请输入正确的手机号码',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        // 显示加载提示
        uni.showLoading({
          title: '保存中...',
          mask: true
        });
        
        // 模拟网络请求延迟
        setTimeout(() => {
          // 更新用户信息
          this.userInfo = {
            ...this.editForm
          };
          
          // 退出编辑模式
          this.isEditMode = false;
          
          // 隐藏加载提示
          uni.hideLoading();
          
          // 显示保存成功提示
          uni.showToast({
            title: '保存成功',
            icon: 'success',
            duration: 2000
          });
        }, 1500);
      },
      
      // 上传头像
      uploadAvatar() {
        // 从相册选择图片
        uni.chooseImage({
          count: 1, // 只能选择1张图片
          sourceType: ['album'], // 只从相册选择
          sizeType: ['compressed'], // 使用压缩图
          success: (res) => {
            const tempFilePath = res.tempFilePaths[0];
            console.log('选择的图片路径:', tempFilePath);
            
            // 显示加载提示
            uni.showLoading({
              title: '上传中...',
              mask: true
            });
            
            // 构建上传URL
            const baseUrl = this.$baseUrl; 
            const userId = uni.getStorageSync('userId');
            const uploadUrl = baseUrl + '/user/userInfoCtl/uploadAvatar?userId=' + userId;
            
            console.log('上传URL:', uploadUrl);
            console.log('baseUrl:', baseUrl);
            console.log('userId:', userId);
            // 上传图片到后端
            uni.uploadFile({
              url: uploadUrl,
              filePath: tempFilePath,
              name: 'file', // 后端接收的文件参数名
              header: {
                'token': uni.getStorageSync('token')  // 根据您后端的要求选择 key 名称
              },
              success: (uploadRes) => {
                uni.hideLoading();
                
                try {
                  const result = JSON.parse(uploadRes.data);
                  console.log('上传结果:', result);
                  
                  if (result.code === 200) {
                    // 上传成功，更新头像
                    const avatarUrl = result.data;
                    this.userInfo.avatar = avatarUrl;
                    // 强制更新视图
                    this.$forceUpdate();
                    
                    uni.showToast({
                      title: '头像上传成功',
                      icon: 'success',
                      duration: 2000
                    });
                  } else {
                    uni.showToast({
                      title: result.message || '上传失败',
                      icon: 'none',
                      duration: 2000
                    });
                  }
                } catch (e) {
                  console.error('解析上传结果失败:', e);
                  uni.showToast({
                    title: '上传失败',
                    icon: 'none',
                    duration: 2000
                  });
                }
              },
              fail: (err) => {
                uni.hideLoading();
                console.error('上传失败:', err);
                uni.showToast({
                  title: '上传失败，请重试',
                  icon: 'none',
                  duration: 2000
                });
              }
            });
          },
          fail: (err) => {
            console.error('选择图片失败:', err);
            uni.showToast({
              title: '选择图片失败',
              icon: 'none',
              duration: 2000
            });
          }
        });
      },
      
      // 选择人脸图片来源
      chooseFaceImageSource() {
        uni.showActionSheet({
          itemList: ['拍照', '从相册选择'],
          success: (res) => {
            if (res.tapIndex === 0) {
              // 拍照
              this.uploadFaceImage(['camera']);
            } else if (res.tapIndex === 1) {
              // 从相册选择
              this.uploadFaceImage(['album']);
            }
          }
        });
      },
      
      // 上传人脸图片
      uploadFaceImage(sourceType) {
        uni.chooseImage({
          count: 1, // 只能选择1张图片
          sourceType: sourceType, // ['camera'] 拍照 或 ['album'] 相册
          sizeType: ['compressed'], // 使用压缩图
          success: (res) => {
            const tempFilePath = res.tempFilePaths[0];
            
            // 显示加载提示
            uni.showLoading({
              title: '上传中...',
              mask: true
            });
            
            // 构建上传URL
            const baseUrl = this.$baseUrl; 
            const userId = uni.getStorageSync('userId');
            const uploadUrl = baseUrl + '/user/userInfoCtl/uploadFace?userId=' + userId;
            
            console.log('人脸图片上传URL:', uploadUrl);
            
            // 上传图片到后端
            uni.uploadFile({
              url: uploadUrl,
              filePath: tempFilePath,
              name: 'file', // 后端接收的文件参数名
              header: {
                'token': uni.getStorageSync('token')
              },
              success: (uploadRes) => {
                uni.hideLoading();
                
                try {
                  const result = JSON.parse(uploadRes.data);
                  console.log('人脸图片上传结果:', result);
                  
                  if (result.code === 200) {
                    // 上传成功，更新人脸图片
                    const faceImageUrl = result.data;
                    this.userInfo.faceImage = faceImageUrl;
                    // 强制更新视图
                    this.$forceUpdate();
                    
                    uni.showToast({
                      title: '人脸上传成功',
                      icon: 'success',
                      duration: 2000
                    });
                  } else {
                    uni.showToast({
                      title: result.message || '上传失败',
                      icon: 'none',
                      duration: 2000
                    });
                  }
                } catch (e) {
                  console.error('解析人脸图片上传结果失败:', e);
                  uni.showToast({
                    title: '上传失败',
                    icon: 'none',
                    duration: 2000
                  });
                }
              },
              fail: (err) => {
                uni.hideLoading();
                console.error('人脸图片上传失败:', err);
                uni.showToast({
                  title: '上传失败，请重试',
                  icon: 'none',
                  duration: 2000
                });
              }
            });
          },
          fail: (err) => {
            console.error('选择人脸图片失败:', err);
            uni.showToast({
              title: '选择图片失败',
              icon: 'none',
              duration: 2000
            });
          }
        });
      }
    }
  }
</script>

<style>
  /* 绿境项目浅色系风格 - 用户信息页面 */
  .container {
    padding-bottom: 30rpx;
    background: #ffffff;
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  /* 顶部导航栏 */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 30rpx;
    background: #ffffff;
    box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.05);
    border-bottom: 2rpx solid #e0e0e0;
  }
  
  .back-button {
    font-size: 36rpx;
    color: #303133;
  }
  
  .header-title {
    font-size: 40rpx;
    font-weight: 600;
    color: #303133;
  }
  
  .edit-button {
    font-size: 30rpx;
    color: #409eff;
    font-weight: 500;
  }

  /* 用户信息卡片 */
  .info-card {
    background: #ffffff;
    padding: 40rpx 30rpx;
    margin: 20rpx;
    border-radius: 12rpx;
    box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.05);
    border: 2rpx solid #e0e0e0;
  }

  /* 头像区域 */
  .avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 40rpx;
    position: relative;
    cursor: pointer;
  }
  
  .avatar-section:active {
    opacity: 0.8;
  }
  
  .user-avatar {
    width: 180rpx;
    height: 180rpx;
    border-radius: 50%;
    margin-bottom: 15rpx;
    border: 4rpx solid #1890ff;
    box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.2);
    transition: all 0.3s ease;
    display: block;
    overflow: hidden;
  }
  
  .avatar-section:active .user-avatar {
    transform: scale(0.95);
  }
  
  .upload-tip {
    font-size: 26rpx;
    color: #1890ff;
    font-weight: 500;
    background: rgba(24, 144, 255, 0.1);
    padding: 8rpx 20rpx;
    border-radius: 30rpx;
  }

  /* 人脸图片区域 */
  .face-image-section {
    margin-bottom: 40rpx;
    border-top: 2rpx solid #e0e0e0;
    padding-top: 40rpx;
  }
  
  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #303133;
    display: block;
    margin-bottom: 20rpx;
    text-align: center;
  }
  
  .face-image-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .face-image-wrapper {
    width: 240rpx;
    height: 320rpx;
    border-radius: 12rpx;
    overflow: hidden;
    border: 3rpx solid #1890ff;
    box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.15);
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
  }
  
  .face-image-wrapper:active {
    transform: scale(0.95);
    opacity: 0.8;
  }
  
  .face-image {
    width: 100%;
    height: 100%;
    display: block;
  }
  
  .face-image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(24, 144, 255, 0.05);
    border: 2rpx dashed #1890ff;
    border-radius: 8rpx;
  }
  
  .placeholder-icon {
    font-size: 60rpx;
    margin-bottom: 10rpx;
    opacity: 0.6;
  }
  
  .placeholder-text {
    font-size: 24rpx;
    color: #1890ff;
    text-align: center;
    font-weight: 500;
  }
  
  .face-image-tip {
    font-size: 24rpx;
    color: #909399;
    margin-top: 15rpx;
    text-align: center;
    line-height: 1.4;
  }

  /* 基本信息表单 */
  .info-form {
    width: 100%;
  }
  
  .form-item {
    display: flex;
    align-items: center;
    padding: 24rpx 0;
    border-bottom: 2rpx solid #e0e0e0;
  }
  
  .form-item:last-child {
    border-bottom: none;
  }
  
  .form-label {
    width: 200rpx;
    font-size: 30rpx;
    color: #303133;
    font-weight: 500;
  }
  
  .form-value {
    flex: 1;
    font-size: 30rpx;
    color: #606266;
  }
  
  .form-input-wrapper {
    flex: 1;
  }
  
  .form-input {
    width: 100%;
    font-size: 30rpx;
    color: #303133;
    padding: 12rpx 16rpx;
    border: 2rpx solid #c0c4cc;
    border-radius: 8rpx;
    background: #f5f7fa;
    font-weight: 500;
    box-sizing: border-box;
  }
  
  .form-input:focus {
    background: #ffffff;
    border-color: #409eff;
  }
  
  .form-radio-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
  }
  
  .radio-label {
    display: flex;
    align-items: center;
    margin-right: 40rpx;
    font-size: 30rpx;
    color: #606266;
    font-weight: 500;
    line-height: 1;
  }
  
  .radio-label radio {
    margin-right: 12rpx;
    transform: translateY(-2rpx);
  }

  /* 按钮区域 */
  .button-section {
    display: flex;
    justify-content: space-between;
    margin-top: 40rpx;
    gap: 20rpx;
  }
  
  .cancel-button {
    flex: 1;
    height: 88rpx;
    line-height: 88rpx;
    font-size: 32rpx;
    font-weight: 500;
    color: #000000d9;
    background: #ffffff;
    border: 2rpx solid #d9d9d9;
    border-radius: 8rpx;
    transition: all 0.2s ease;
  }
  
  .cancel-button:hover {
    border-color: #40a9ff;
    color: #40a9ff;
    transform: translateY(-1rpx);
  }
  
  .save-button {
    flex: 1;
    height: 88rpx;
    line-height: 88rpx;
    font-size: 32rpx;
    font-weight: 500;
    background: #1890ff;
    color: #ffffff;
    border-radius: 8rpx;
    transition: all 0.2s ease;
  }
  
  .save-button:hover {
    background: #40a9ff;
    transform: translateY(-1rpx);
  }

  /* 注意事项 */
  .notice-section {
    background: #ffffff;
    padding: 40rpx 30rpx;
    margin: 0 20rpx;
    border-radius: 12rpx;
    box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.05);
    border: 2rpx solid #e0e0e0;
  }
  
  .notice-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #303133;
    display: block;
    margin-bottom: 20rpx;
  }
  
  .notice-content {
    font-size: 28rpx;
    color: #606266;
    line-height: 44rpx;
    white-space: pre-line;
  }

  /* ========== 全局统一主题覆盖（用户信息页） ========== */
  .container {
    background:
      radial-gradient(circle at 15% 8%, rgba(122, 163, 255, 0.28) 0%, rgba(122, 163, 255, 0) 36%),
      linear-gradient(145deg, #e8efff 0%, #dce8ff 100%) !important;
  }

  .header,
  .info-card,
  .notice-section,
  .form-input-wrapper,
  .face-image-wrapper {
    background: #edf3ff !important;
    border-color: rgba(255,255,255,0.78) !important;
    box-shadow: 10rpx 10rpx 22rpx rgba(128,151,199,0.22), -10rpx -10rpx 22rpx rgba(255,255,255,0.95) !important;
  }

  .header-title,
  .section-title,
  .form-label,
  .form-value,
  .notice-title {
    color: #334f7c !important;
  }

  .edit-button,
  .notice-content,
  .face-image-tip {
    color: #7890b4 !important;
  }

  .form-input {
    height: 78rpx !important;
    line-height: 78rpx !important;
    padding: 0 22rpx !important;
    border-radius: 18rpx !important;
    background: #edf3ff !important;
    color: #334f7c !important;
    box-shadow: inset 8rpx 8rpx 16rpx rgba(159,179,220,0.2), inset -8rpx -8rpx 16rpx rgba(255,255,255,0.94) !important;
  }

  .save-button,
  .cancel-button {
    min-height: 76rpx !important;
    border-radius: 999rpx !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
  }
</style>
