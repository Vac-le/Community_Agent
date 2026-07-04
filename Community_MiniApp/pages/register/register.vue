<template>
  <view class="register-container">
    <view class="logo-section">
      <text class="app-title">用户注册</text>
      <text class="app-subtitle">欢迎加入社区便民小程序</text>
    </view>

    <view class="form-section">
      <view class="input-group">
        <text class="input-label">账号</text>
        <input 
          class="input-field" 
          type="text" 
          placeholder="请输入账号（手机号）" 
          v-model="formData.account"
          maxlength="11"
        />
      </view>

      <view class="input-group">
        <text class="input-label">所属社区</text>
        <picker 
          mode="selector" 
          :range="communityList" 
          range-key="name"
          @change="onCommunityChange"
        >
          <view class="picker-input">
            <text :class="formData.communityName ? 'selected-text' : 'placeholder-text'">
              {{ formData.communityName || '请选择所属社区' }}
            </text>
            <text class="arrow-icon">›</text>
          </view>
        </picker>
      </view>

      <view class="input-group">
        <text class="input-label">密码</text>
        <input 
          class="input-field" 
          type="password"
          password
          placeholder="请输入密码（6-20位）" 
          v-model="formData.password"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="input-label">确认密码</text>
        <input 
          class="input-field" 
          type="password"
          password
          placeholder="请再次输入密码" 
          v-model="formData.confirmPassword"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="input-label">验证码</text>
        <view class="captcha-container">
          <input 
            class="captcha-input" 
            type="text" 
            placeholder="请输入验证码" 
            v-model="formData.code"
            maxlength="5"
          />
          <image 
            class="captcha-image" 
            :src="imgCode" 
            mode="aspectFit"
            @tap="createYzm"
          />
        </view>
      </view>

      <button class="register-button" @click="handleRegister">注册</button>
      
      <!-- 返回登录链接 -->
      <view class="login-link-container">
        <text class="login-link" @click="goToLogin">已有账号？立即登录</text>
      </view>
    </view>

    <!-- 底部文字信息 -->
    <view class="footer-section">
      <text class="footer-text">社区便民小程序</text>
      <text class="footer-version">版本 1.0.0</text>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        formData: {
          account: '',
          communityId: '', // 社区ID
          password: '',
		  confirmPassword:'',
          code:"",
		  verKey:""
        },
        imgCode: '', // 验证码图片base64
        // 社区列表（模拟数据）
        communityList: []
      }
    },
    onLoad() {
      this.getCommunityList();
    },
	onShow(){
		this.createYzm();
	},
    methods: {
	  //从后端获取社区列表
	  async getCommunityList()
	  {
		  const resp = await this.$myRequest({
		    url: '/api/loginCtl/communityList',
		    method: 'GET'
		  });
		  this.communityList = resp.data.data;
	  },
      // 社区选择变化
      onCommunityChange(e) {
        const index = e.detail.value;
        const selectedCommunity = this.communityList[index];
        this.formData.communityId = selectedCommunity.id;
        this.formData.communityName = selectedCommunity.name;
        console.log('选择的社区:', selectedCommunity);
      },
      
      // 生成验证码
      async createYzm() {
        try {
          // 调用后端接口获取验证码
          const resp = await this.$myRequest({
            url: '/api/loginCtl/createYzm',
            method: 'GET'
          });
          if (resp.data.code === 200) {
            this.imgCode = resp.data.data.imgCode;
            this.formData.verKey = resp.data.data.verKey;
          }
        } catch (error) {
          console.error('获取验证码失败:', error);
        }
      },
      
      // 验证手机号格式
      validatePhone(phone) {
        const reg = /^1[3-9]\d{9}$/;
        return reg.test(phone);
      },
      
      // 注册处理
      async handleRegister() {
        // 验证账号
        if (!this.formData.account) {
          uni.showToast({
            title: '请输入账号',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        if (!this.validatePhone(this.formData.account)) {
          uni.showToast({
            title: '请输入正确的手机号',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        // 验证社区
        if (!this.formData.communityId) {
          uni.showToast({
            title: '请选择所属社区',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        // 验证验证码
        if (!this.formData.code) {
          uni.showToast({
            title: '请输入验证码',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        // 验证密码
        if (!this.formData.password) {
          uni.showToast({
            title: '请输入密码',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        if (this.formData.password.length < 6) {
          uni.showToast({
            title: '密码长度不能少于6位',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        // 验证确认密码
        if (!this.formData.confirmPassword) {
          uni.showToast({
            title: '请确认密码',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        
        if (this.formData.password !== this.formData.confirmPassword) {
          uni.showToast({
            title: '两次输入的密码不一致',
            icon: 'none',
            duration: 2000
          });
          return;
        }
        // 显示加载中
        uni.showLoading({
          title: '注册中...',
          mask: true
        });
        try {
          // 调用注册接口
		  const userForm = this.formData;
		  console.log(userForm);
          const resp = await this.$myRequest({
            url: 'api/loginCtl/register',
            method: 'POST',
            data: userForm
          });
          
          uni.hideLoading();
          
          if (resp.data.code === 200) {
            uni.showToast({
              title: '注册成功',
              icon: 'success',
              duration: 2000
            });
            
            // 延迟跳转到登录页
            setTimeout(() => {
              uni.navigateBack();
            }, 2000);
          } else {
			if(resp.data.code==1)
			{
				uni.showToast({
				  title:'验证码错误',
				  icon: 'none',
				  duration: 2000
				});
			}
			if(resp.data.code==2)
			{
				uni.showToast({
				  title:'账号已经注册',
				  icon: 'none',
				  duration: 2000
				});
			}
          }
        } catch (error) {
          uni.hideLoading();
          console.error('注册失败:', error);
          uni.showToast({
            title: '注册失败，请稍后重试',
            icon: 'none',
            duration: 2000
          });
          // 刷新验证码
          this.createYzm();
        }
      },
      
      // 返回登录页面
      goToLogin() {
        uni.navigateBack();
      }
    }
  }
</script>

<style scoped>
  /* 注册页面样式 */
  .register-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    height: 100vh;
    padding: 60rpx 40rpx 40rpx;
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    box-sizing: border-box;
    overflow: hidden;
  }

  /* 顶部标题区域 */
  .logo-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20rpx;
    flex-shrink: 0;
  }
  
  .app-title {
    font-size: 44rpx;
    font-weight: 600;
    color: #303133;
    text-align: center;
    letter-spacing: 1rpx;
    margin-bottom: 15rpx;
  }
  
  .app-subtitle {
    font-size: 28rpx;
    color: #909399;
    text-align: center;
  }

  /* 注册表单区域 */
  .form-section {
    width: 100%;
    max-width: 600rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #ffffff;
    padding: 40rpx;
    border-radius: 12rpx;
    box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.05);
    border: 2rpx solid #e0e0e0;
    flex: 1;
    overflow-y: auto;
    margin: 20rpx 0;
  }
  
  .input-group {
    width: 100%;
    margin-bottom: 30rpx;
  }
  
  .input-label {
    display: block;
    font-size: 28rpx;
    color: #606266;
    margin-bottom: 12rpx;
    font-weight: 500;
  }
  
  .input-field {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    font-size: 30rpx;
    color: #303133;
    background-color: #ffffff;
    border: 2rpx solid #c0c4cc;
    border-radius: 8rpx;
    padding: 0 20rpx;
    box-sizing: border-box;
    transition: all 0.2s ease;
  }
  
  .input-field:focus {
    border-color: #409eff;
    box-shadow: 0 0 0 2rpx rgba(64, 158, 255, 0.1);
    outline: none;
  }
  
  /* 验证码容器 */
  .captcha-container {
    display: flex;
    align-items: center;
    gap: 20rpx;
  }
  
  .captcha-input {
    flex: 1;
    height: 88rpx;
    line-height: 88rpx;
    font-size: 30rpx;
    color: #303133;
    background-color: #ffffff;
    border: 2rpx solid #c0c4cc;
    border-radius: 8rpx;
    padding: 0 20rpx;
    box-sizing: border-box;
    transition: all 0.2s ease;
  }
  
  .captcha-input:focus {
    border-color: #409eff;
    box-shadow: 0 0 0 2rpx rgba(64, 158, 255, 0.1);
    outline: none;
  }
  
  .captcha-image {
    width: 260rpx;
    height: 96rpx;
    border: 2rpx solid #c0c4cc;
    border-radius: 8rpx;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .captcha-image:active {
    opacity: 0.7;
  }
  
  /* 社区选择器 */
  .picker-input {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    font-size: 30rpx;
    background-color: #ffffff;
    border: 2rpx solid #c0c4cc;
    border-radius: 8rpx;
    padding: 0 20rpx;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
  }
  
  .picker-input:active {
    border-color: #409eff;
  }
  
  .placeholder-text {
    color: #c0c4cc;
  }
  
  .selected-text {
    color: #303133;
  }
  
  .arrow-icon {
    font-size: 40rpx;
    color: #c0c4cc;
    font-weight: bold;
    transform: rotate(90deg);
  }
  
  .register-button {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    font-size: 32rpx;
    font-weight: 500;
    color: #ffffff;
    background: #1890ff;
    border: none;
    border-radius: 8rpx;
    margin-top: 20rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: all 0.2s ease;
  }
  
  .register-button:hover {
    background: #40a9ff;
    transform: translateY(-1rpx);
  }
  
  /* 登录链接 */
  .login-link-container {
    width: 100%;
    display: flex;
    justify-content: center;
    margin-top: 30rpx;
  }
  
  .login-link {
    font-size: 28rpx;
    color: #1890ff;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .login-link:hover {
    color: #40a9ff;
    text-decoration: underline;
  }

  /* 底部文字信息 */
  .footer-section {
    text-align: center;
    margin-top: 20rpx;
    flex-shrink: 0;
  }
  
  .footer-text {
    font-size: 28rpx;
    color: #606266;
    display: block;
    margin-bottom: 10rpx;
    font-weight: 500;
  }
  
  .footer-version {
    font-size: 24rpx;
    color: #909399;
    display: block;
    font-weight: 400;
  }

  /* ========== 全局统一主题覆盖（注册页） ========== */
  .register-container {
    background:
      radial-gradient(circle at 16% 10%, rgba(125, 167, 255, 0.3) 0%, rgba(125, 167, 255, 0) 36%),
      linear-gradient(145deg, #e8efff 0%, #dce8ff 100%) !important;
  }

  .form-section,
  .input-field,
  .captcha-input,
  .picker-input {
    background: #edf3ff !important;
    border: 1rpx solid rgba(255,255,255,0.78) !important;
    box-shadow: inset 8rpx 8rpx 16rpx rgba(159,179,220,0.2), inset -8rpx -8rpx 16rpx rgba(255,255,255,0.94) !important;
    border-radius: 18rpx !important;
  }

  .app-title,
  .input-label,
  .selected-text,
  .footer-text {
    color: #334f7c !important;
  }

  .app-subtitle,
  .placeholder-text,
  .footer-version,
  .login-link {
    color: #7890b4 !important;
  }

  .input-field,
  .captcha-input,
  .picker-input {
    height: 82rpx !important;
    line-height: 82rpx !important;
    padding: 0 22rpx !important;
    font-size: 28rpx !important;
  }

  .register-button {
    height: 84rpx !important;
    border-radius: 999rpx !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    background: linear-gradient(145deg, #84a7ff 0%, #5f86ff 100%) !important;
  }
</style>
