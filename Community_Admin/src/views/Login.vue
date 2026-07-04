<template>
  <div class="login-page">
    <div class="bg-overlay"></div>
    <div class="bg-particles">
      <span v-for="i in 12" :key="i" class="particle" :style="getParticleStyle(i)"></span>
		          </div>

    <!-- 左侧装饰区 -->
    <div class="login-left">
      <div class="left-content">
        <div class="brand-logo">
          <div class="logo-icon"><i class="el-icon-office-building"></i></div>
          <span class="brand-name">智慧社区</span>
			  </div>
        <h1 class="left-title">智能管理<br/>便民服务</h1>
        <p class="left-desc">整合社区资源，提升居民生活品质<br/>让社区管理更高效、更智能</p>
        <div class="feature-list">
          <div class="feature-item" v-for="(f, i) in features" :key="i" :style="{ animationDelay: (i * 0.12 + 0.4) + 's' }">
            <div class="feature-icon"><i :class="f.icon"></i></div>
            <span>{{ f.text }}</span>
			  </div>
		     </div>
	</div>
      <div class="deco-circle deco-1"></div>
      <div class="deco-circle deco-2"></div>
    </div>

    <!-- 右侧登录区 -->
    <div class="login-right">
      <div class="login-card"> 
        <!-- 动画角色：4个卡通角色 -->
        <div class="character-wrap">
          <!-- 紫色高矩形角色（后层） -->
          <div class="char char-purple" :style="purpleStyle">
            <div class="char-eyes" :style="purpleEyePos">
              <div class="eyeball-wrap">
                <div class="pupil" :style="eyeballStyle"></div>
                <div class="eyelid" :class="{blink: isPurpleBlink}"></div>
              </div>
              <div class="eyeball-wrap">
                <div class="pupil" :style="eyeballStyle"></div>
                <div class="eyelid" :class="{blink: isPurpleBlink}"></div>
              </div>
            </div>
          </div>
          <!-- 黑色矩形角色（中层） -->
          <div class="char char-black" :style="blackStyle">
            <div class="char-eyes" :style="blackEyePos">
              <div class="eyeball-wrap sm">
                <div class="pupil sm" :style="eyeballStyle"></div>
                <div class="eyelid" :class="{blink: isBlackBlink}"></div>
              </div>
              <div class="eyeball-wrap sm">
                <div class="pupil sm" :style="eyeballStyle"></div>
                <div class="eyelid" :class="{blink: isBlackBlink}"></div>
              </div>
            </div>
          </div>
          <!-- 橙色半圆角色（前左） -->
          <div class="char char-orange" :style="orangeStyle">
            <div class="char-eyes" :style="orangeEyePos">
              <div class="pupil-only" :style="pupilOnlyStyle"></div>
              <div class="pupil-only" :style="pupilOnlyStyle"></div>
            </div>
          </div>
          <!-- 黄色圆角矩形角色（前右） -->
          <div class="char char-yellow" :style="yellowStyle">
            <div class="char-eyes" :style="yellowEyePos">
              <div class="pupil-only" :style="pupilOnlyStyle"></div>
              <div class="pupil-only" :style="pupilOnlyStyle"></div>
            </div>
            <div class="char-mouth" :style="yellowMouthPos"></div>
          </div>
        </div>

        <!-- 标题 -->
        <div class="card-header">
          <h2 class="card-title">欢迎回来</h2>
          <p class="card-subtitle">请登录您的管理员账号</p>
        </div>

        <!-- 表单 -->
        <div class="form-wrap">
          <div class="input-group" :class="{ focused: isAccountFocus, filled: form.account }">
            <div class="input-icon"><i class="el-icon-user"></i></div>
            <input
              class="form-input"
              type="text"
              v-model="form.account"
              placeholder="请输入用户名"
              @focus="isAccountFocus = true; isError = false; errorMsg = ''"
              @blur="isAccountFocus = false"
            />
            <div class="input-line"></div>
          </div>

          <div class="input-group" :class="{ focused: isPasswordFocus, filled: form.password }">
            <div class="input-icon"><i class="el-icon-lock"></i></div>
            <input
              class="form-input"
              :type="showPassword ? 'text' : 'password'"
              v-model="form.password"
              placeholder="请输入密码"
              @focus="isPasswordFocus = true; isError = false; errorMsg = ''"
              @blur="isPasswordFocus = false"
            />
            <div class="input-line"></div>
            <div class="pwd-toggle" @click="showPassword = !showPassword">
              <i :class="showPassword ? 'el-icon-view' : 'el-icon-minus'"></i>
            </div>
          </div>

          <div class="error-tip" v-show="errorMsg">
            <i class="el-icon-warning-outline"></i> {{ errorMsg }}
          </div>

          <button class="login-btn" :class="{ loading: isLoading }" @click="login" :disabled="isLoading">
            <span v-if="!isLoading">登 录</span>
            <span v-else><i class="el-icon-loading"></i> 登录中...</span>
          </button>
        </div>

        <div class="card-footer">智慧社区管理平台 &copy; 2026</div>
			  </div>
		     </div>
	</div>
</template>

<script>
export default {
  data() {
    return {
      form: { account: '', password: '' },
      showPassword: false,
      isAccountFocus: false,
      isPasswordFocus: false,
      isSmile: false,
      isError: false,
      isPurpleBlink: false,
      isBlackBlink: false,
      isLoading: false,
      errorMsg: '',
      mouseX: 0,
      mouseY: 0,
      purpleTimer: null,
      blackTimer: null,
      features: [
        { icon: 'el-icon-s-order',       text: '订单全流程管理' },
        { icon: 'el-icon-data-analysis', text: '社区数据可视化' },
        { icon: 'el-icon-bell',          text: '实时消息通知'   },
        { icon: 'el-icon-s-custom',      text: '多角色权限控制' },
      ]
    }
  },
  computed: {
    // 以各角色DOM为基准计算眼球偏移
    eyeballStyle() {
      const el = document.querySelector('.char-purple')
      if (!el) return {}
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 3
      const dx = this.mouseX - cx
      const dy = this.mouseY - cy
      const dist = Math.sqrt(dx*dx + dy*dy) || 1
      const max = 5
      const ratio = Math.min(dist, 150) / 150
      return { transform: 'translate(' + (dx/dist*max*ratio) + 'px,' + (dy/dist*max*ratio) + 'px)' }
    },
    pupilOnlyStyle() {
      const el = document.querySelector('.char-orange')
      if (!el) return {}
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 2
      const dx = this.mouseX - cx
      const dy = this.mouseY - cy
      const dist = Math.sqrt(dx*dx + dy*dy) || 1
      const max = 5
      const ratio = Math.min(dist, 150) / 150
      return { transform: 'translate(' + (dx/dist*max*ratio) + 'px,' + (dy/dist*max*ratio) + 'px)' }
    },
    // 各角色body倾斜
    purpleStyle() {
      if (this.isPasswordFocus) return { transform: 'skewX(-12deg) translateX(30px)', height: '220px' }
      const sk = this.calcSkew('.char-purple')
      return { transform: 'skewX('+sk+'deg)' }
    },
    blackStyle() {
      if (this.isPasswordFocus) return { transform: 'skewX(10deg) translateX(15px)' }
      const sk = this.calcSkew('.char-black')
      return { transform: 'skewX('+sk+'deg)' }
    },
    orangeStyle() {
      const sk = this.calcSkew('.char-orange')
      return { transform: 'skewX('+sk+'deg)' }
    },
    yellowStyle() {
      const sk = this.calcSkew('.char-yellow')
      return { transform: 'skewX('+sk+'deg)' }
    },
    // 眼睛位置偏移
    purpleEyePos() {
      if (this.isPasswordFocus) return { left: '35px', top: '30px', opacity: '0', pointerEvents: 'none' }
      const p = this.calcFacePos('.char-purple')
      return { left: (40+p.x)+'px', top: (30+p.y)+'px', opacity: '1' }
    },
    blackEyePos() {
      if (this.isPasswordFocus) return { left: '20px', top: '28px', opacity: '0', pointerEvents: 'none' }
      const p = this.calcFacePos('.char-black')
      return { left: (20+p.x)+'px', top: (28+p.y)+'px', opacity: '1' }
    },
    orangeEyePos() {
      const p = this.calcFacePos('.char-orange')
      return { left: (60+p.x)+'px', top: (70+p.y)+'px' }
    },
    yellowEyePos() {
      const p = this.calcFacePos('.char-yellow')
      return { left: (42+p.x)+'px', top: (36+p.y)+'px' }
    },
    yellowMouthPos() {
      const p = this.calcFacePos('.char-yellow')
      return { left: (28+p.x)+'px', top: (80+p.y)+'px' }
    }
  },
  mounted() {
    this.startBlink()
    window.addEventListener('mousemove', this.trackMouse)
  },
  beforeDestroy() {
    clearTimeout(this.purpleTimer)
    clearTimeout(this.blackTimer)
    window.removeEventListener('mousemove', this.trackMouse)
  },
  methods: {
    calcSkew(sel) {
      const el = document.querySelector(sel)
      if (!el) return 0
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const dx = this.mouseX - cx
      return Math.max(-6, Math.min(6, -dx / 100))
    },
    calcFacePos(sel) {
      const el = document.querySelector(sel)
      if (!el) return { x: 0, y: 0 }
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 3
      return {
        x: Math.max(-12, Math.min(12, (this.mouseX - cx) / 20)),
        y: Math.max(-8,  Math.min(8,  (this.mouseY - cy) / 30))
      }
    },
    startBlink() {
      const schedulePurple = () => {
        this.purpleTimer = setTimeout(() => {
          this.isPurpleBlink = true
          setTimeout(() => { this.isPurpleBlink = false; schedulePurple() }, 150)
        }, Math.random() * 4000 + 3000)
      }
      const scheduleBlack = () => {
        this.blackTimer = setTimeout(() => {
          this.isBlackBlink = true
          setTimeout(() => { this.isBlackBlink = false; scheduleBlack() }, 150)
        }, Math.random() * 4000 + 2000)
      }
      schedulePurple()
      scheduleBlack()
    },
    trackMouse(e) {
      this.mouseX = e.clientX
      this.mouseY = e.clientY
    },
    getParticleStyle(i) {
      const sizes     = [3,5,4,6,3,5,4,7,3,5,4,6]
      const delays    = [0,2,4,1,3,5,0.5,2.5,4.5,1.5,3.5,5.5]
      const durations = [12,15,18,14,16,20,13,17,19,11,16,14]
      const idx = i - 1
      return {
        width:  sizes[idx] + 'px',
        height: sizes[idx] + 'px',
        left:   (idx * 8.5) + '%',
        animationDuration: durations[idx] + 's',
        animationDelay:    delays[idx] + 's',
      }
    },
    login() {
      this.errorMsg = ''
      this.isError  = false
      this.isSmile  = false
      if (!this.form.account)  { this.errorMsg = '用户名不能为空'; this.isError = true; return }
      if (!this.form.password) { this.errorMsg = '密码不能为空';   this.isError = true; return }
      this.isLoading = true
      this.$http.post('api/loginCtl/login', this.form)
        .then((resp) => {
          this.isLoading = false
          if (resp.data.code == 201) {
            this.errorMsg = '账号或密码错误，请重新输入'
            this.isError  = true
          } else if (resp.data.code == 200) {
            this.isSmile = true
            sessionStorage.setItem('account', resp.data.data.account)
            sessionStorage.setItem('token',   resp.data.data.token)
            setTimeout(() => { this.$router.push('/main') }, 600)
          }
        })
        .catch(() => {
          this.isLoading = false
          this.errorMsg  = '服务器异常，请稍后重试'
          this.isError   = true
        })
		}
	}
 }
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.login-page {
	display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #0c1929 0%, #1a3a5c 50%, #0d2137 100%);
}

.bg-overlay {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.12) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(99,102,241,0.08) 0%, transparent 50%);
}

.bg-particles { position: fixed; inset: 0; pointer-events: none; z-index: 0; }

.particle {
	position: absolute;
  bottom: -10px;
	border-radius: 50%;
  background: rgba(96,165,250,0.45);
  animation: rise linear infinite;
}

@keyframes rise {
  0%   { bottom: -10px; opacity: 0; }
  10%  { opacity: 0.8; }
  90%  { opacity: 0.3; }
  100% { bottom: 110vh; opacity: 0; }
}

/* 左侧 */
.login-left {
	flex: 1;
  position: relative;
	display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  overflow: hidden;
}

.left-content { padding: 60px; animation: fadeInLeft 0.7s ease-out both; }

@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to   { opacity: 1; transform: translateX(0); }
}

.brand-logo { display: flex; align-items: center; gap: 12px; margin-bottom: 52px; }

.logo-icon {
  width: 46px; height: 46px;
  background: rgba(96,165,250,0.15);
  border: 1px solid rgba(96,165,250,0.35);
	border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; color: #60a5fa;
}

.brand-name { font-size: 20px; font-weight: 700; color: #e2e8f0; letter-spacing: 3px; }

.left-title {
  font-size: 50px; font-weight: 800; line-height: 1.25; margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #93c5fd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.left-desc { font-size: 15px; color: rgba(148,163,184,0.85); line-height: 1.9; margin-bottom: 44px; }

.feature-list { display: flex; flex-direction: column; gap: 14px; }

.feature-item {
  display: flex; align-items: center; gap: 14px;
  font-size: 14px; color: rgba(203,213,225,0.85);
  animation: fadeInLeft 0.6s ease-out both;
}

.feature-icon {
  width: 34px; height: 34px; border-radius: 9px; flex-shrink: 0;
  background: rgba(59,130,246,0.12);
  border: 1px solid rgba(59,130,246,0.25);
  display: flex; align-items: center; justify-content: center;
  color: #60a5fa; font-size: 15px;
}

.deco-circle { position: absolute; border-radius: 50%; border: 1px solid rgba(96,165,250,0.1); pointer-events: none; }
.deco-1 { width: 460px; height: 460px; bottom: -130px; left: -90px; }
.deco-2 { width: 220px; height: 220px; top: 80px; right: 60px; background: rgba(59,130,246,0.03); }

/* 右侧 */
.login-right {
  width: 460px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  z-index: 1; padding: 32px 28px;
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-left: 1px solid rgba(255,255,255,0.07);
  animation: fadeInRight 0.7s ease-out both;
}

@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(30px); }
  to   { opacity: 1; transform: translateX(0); }
}

.login-card { width: 100%; display: flex; flex-direction: column; align-items: center; }

/* ===== 4个卡通角色 ===== */
.character-wrap {
  width: 340px;
  height: 220px;
  position: relative;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.char {
  position: absolute;
  bottom: 0;
  transition: transform 0.6s cubic-bezier(0.34,1.56,0.64,1), height 0.5s ease;
  transform-origin: bottom center;
}

.char-purple {
  left: 36px;
  width: 108px;
  height: 195px;
  background: #6C3FF5;
  border-radius: 8px 8px 0 0;
  z-index: 1;
}

.char-black {
  left: 142px;
  width: 74px;
  height: 165px;
  background: #2D2D2D;
  border-radius: 6px 6px 0 0;
  z-index: 2;
}

.char-orange {
  left: 0px;
  width: 148px;
  height: 115px;
  background: #FF9B6B;
  border-radius: 74px 74px 0 0;
  z-index: 3;
}

.char-yellow {
  left: 210px;
  width: 108px;
  height: 145px;
  background: #E8D754;
  border-radius: 54px 54px 0 0;
  z-index: 4;
}

.char-eyes {
	position: absolute;
	display: flex;
	gap: 12px;
  transition: left 0.3s ease, top 0.3s ease, opacity 0.3s ease;
}

.eyeball-wrap {
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
	display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.15);
}

.eyeball-wrap.sm {
  width: 14px;
  height: 14px;
}

.pupil {
  width: 9px;
  height: 9px;
  background: #2D2D2D;
  border-radius: 50%;
  transition: transform 0.08s ease-out;
}

.pupil.sm {
  width: 7px;
  height: 7px;
}

.pupil-only {
  width: 11px;
  height: 11px;
  background: #2D2D2D;
  border-radius: 50%;
  transition: transform 0.08s ease-out;
}

.eyelid {
	position: absolute;
  top: 0; left: 0;
  width: 100%; height: 0;
  border-radius: 50% 50% 0 0;
  transition: height 0.12s ease;
  z-index: 2;
  pointer-events: none;
}

.char-purple .eyelid { background: #6C3FF5; }
.char-black  .eyelid { background: #2D2D2D; }
.eyelid.blink { height: 100%; }

.char-mouth {
	position: absolute;
  width: 48px;
  height: 4px;
  background: #2D2D2D;
  border-radius: 2px;
  transition: left 0.3s ease, top 0.3s ease;
}

/* 卡片标题 */
.card-header { text-align: center; margin-bottom: 28px; width: 100%; }
.card-title { font-size: 26px; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; letter-spacing: 1px; }
.card-subtitle { font-size: 14px; color: rgba(148,163,184,0.8); }

/* 表单 */
.form-wrap { width: 100%; display: flex; flex-direction: column; }

.input-group {
  position: relative;
  display: flex; align-items: center;
  margin-bottom: 20px;
  border-radius: 10px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.2s ease;
  overflow: hidden;
}

.input-group.focused {
  background: rgba(255,255,255,0.09);
  border-color: rgba(96,165,250,0.5);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.12);
}

.input-icon {
  padding: 0 14px;
  font-size: 18px;
  color: rgba(148,163,184,0.7);
  flex-shrink: 0;
  transition: color 0.2s;
}
.input-group.focused .input-icon { color: #60a5fa; }

.form-input {
  flex: 1; height: 50px;
  background: transparent; border: none; outline: none;
  font-size: 15px; color: #f1f5f9;
  padding: 0 12px 0 0;
}
.form-input::placeholder { color: rgba(148,163,184,0.5); }

.input-line {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 2px; background: #60a5fa;
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: left;
}
.input-group.focused .input-line { transform: scaleX(1); }

.pwd-toggle {
  padding: 0 14px; font-size: 18px;
  color: rgba(148,163,184,0.6);
  cursor: pointer; transition: color 0.2s;
}
.pwd-toggle:hover { color: #60a5fa; }

/* 错误提示 */
.error-tip {
  font-size: 13px; color: #f87171;
  margin-bottom: 14px;
  display: flex; align-items: center; gap: 6px;
  animation: shake 0.4s ease;
}

@keyframes shake {
  0%,100% { transform: translateX(0); }
  20%     { transform: translateX(-6px); }
  40%     { transform: translateX(6px); }
  60%     { transform: translateX(-4px); }
  80%     { transform: translateX(4px); }
}

/* 登录按钮 */
.login-btn {
  width: 100%; height: 50px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff; border: none; border-radius: 10px;
  font-size: 16px; font-weight: 600; letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(59,130,246,0.4);
  position: relative; overflow: hidden;
  margin-bottom: 8px;
}
.login-btn::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 60%);
  opacity: 0; transition: opacity 0.2s;
}
.login-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(59,130,246,0.5); }
.login-btn:hover:not(:disabled)::before { opacity: 1; }
.login-btn:active:not(:disabled) { transform: translateY(0); }
.login-btn:disabled { opacity: 0.7; cursor: not-allowed; }

/* 底部 */
.card-footer {
  margin-top: 24px; font-size: 12px;
  color: rgba(148,163,184,0.45); text-align: center;
}

/* 响应式 */
@media (max-width: 900px) {
  .login-left { display: none; }
  .login-right { width: 100%; border-left: none; }
}
</style>
</style>