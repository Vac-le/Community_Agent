<template>
	  <div id="app" class="fixed-layout">
    <div class="global-bg"></div>
    <div class="global-bg-overlay"></div>
    <canvas id="particle-canvas" class="particle-canvas"></canvas>
		  <router-view></router-view>
	  </div>
	</template>

	<script>
	export default {
	  name: 'app',
  mounted() {
    this.initParticles()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    cancelAnimationFrame(this._rafId)
  },
  methods: {
    handleResize() {
      const c = document.getElementById('particle-canvas')
      if (c) { c.width = window.innerWidth; c.height = window.innerHeight }
    },
    initParticles() {
      const canvas = document.getElementById('particle-canvas')
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      canvas.width  = window.innerWidth
      canvas.height = window.innerHeight
      const N = 60
      const pts = Array.from({ length: N }, () => ({
        x:  Math.random() * canvas.width,
        y:  Math.random() * canvas.height,
        r:  Math.random() * 1.8 + 0.4,
        dx: (Math.random() - 0.5) * 0.3,
        dy: -(Math.random() * 0.4 + 0.1),
        a:  Math.random() * 0.45 + 0.15,
        p:  Math.random() * Math.PI * 2
      }))
      const draw = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        pts.forEach(p => {
          p.p += 0.018
          const a = p.a * (0.7 + 0.3 * Math.sin(p.p))
          ctx.beginPath()
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
          ctx.fillStyle = `rgba(96,165,250,${a})`
          ctx.fill()
          p.x += p.dx; p.y += p.dy
          if (p.y < -6) { p.y = canvas.height + 6; p.x = Math.random() * canvas.width }
          if (p.x < -6) p.x = canvas.width + 6
          if (p.x > canvas.width + 6) p.x = -6
        })
        for (let i = 0; i < N; i++) {
          for (let j = i + 1; j < N; j++) {
            const dx = pts[i].x - pts[j].x
            const dy = pts[i].y - pts[j].y
            const d  = Math.sqrt(dx * dx + dy * dy)
            if (d < 120) {
              ctx.beginPath()
              ctx.strokeStyle = `rgba(96,165,250,${0.12 * (1 - d / 120)})`
              ctx.lineWidth = 0.5
              ctx.moveTo(pts[i].x, pts[i].y)
              ctx.lineTo(pts[j].x, pts[j].y)
              ctx.stroke()
            }
          }
        }
        this._rafId = requestAnimationFrame(draw)
      }
      draw()
    }
  }
	}
	</script>

	<style>
/* ============================================================
   深色全局主题 — 智慧社区管理后台
   基调：#0c1929 → #1a3a5c，与登录页完全统一
============================================================ */

/* ===== CSS 变量 ===== */
:root {
  --primary:        #3b82f6;
  --primary-light:  #60a5fa;
  --primary-dark:   #2563eb;
  --primary-10:     rgba(59,130,246,0.10);
  --primary-20:     rgba(59,130,246,0.20);
  --primary-40:     rgba(59,130,246,0.40);
  --success:  #10b981;
  --warning:  #f59e0b;
  --danger:   #ef4444;
  --info:     #06b6d4;
  --bg-deep:    #07111f;
  --bg-mid:     #0c1a2e;
  --bg-card:    rgba(255,255,255,0.05);
  --bg-card-hv: rgba(255,255,255,0.08);
  --text-1: #f8fbff;
  --text-2: #e2edf8;
  --text-3: #9eb0c5;
  --bd:   rgba(255,255,255,0.10);
  --bd-sm: rgba(255,255,255,0.06);
  --sh-sm: 0 10px 24px rgba(2,8,23,0.22);
  --sh-md: 0 18px 40px rgba(2,8,23,0.28);
  --sh-lg: 0 24px 56px rgba(2,8,23,0.34);
  --sh-xl: 0 32px 72px rgba(2,8,23,0.42);
  --r-sm:  8px;
  --r-md: 12px;
  --r-lg: 18px;
  --r-xl: 24px;
  --t-fast: 150ms ease;
  --t-base: 220ms ease;
  --font: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ===== 基础重置 ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; width: 100%; }
	body {
  font-family: var(--font);
  font-size: 14px;
	  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  color: var(--text-1);
  background: var(--bg-deep);
	}

/* 全局文字提亮兜底（精简版，避免破坏特殊组件） */
.fixed-layout {
  color: var(--text-1);
}

.el-table .cell,
.el-form-item__label {
  color: var(--text-1) !important;
}

#app, .fixed-layout {
	  height: 100vh;
	  display: flex;
	  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* ===== 粒子背景 ===== */
.global-bg {
  position: fixed; inset: 0; z-index: -5; pointer-events: none;
  background:
    radial-gradient(circle at top left, rgba(14,165,233,0.14), transparent 26%),
    radial-gradient(circle at 85% 12%, rgba(99,102,241,0.14), transparent 24%),
    radial-gradient(circle at 50% 100%, rgba(16,185,129,0.08), transparent 30%),
    linear-gradient(135deg, #07111f 0%, #0b1830 44%, #0d2038 100%);
}
.global-bg-overlay {
  position: fixed; inset: 0; z-index: -4; pointer-events: none;
  background:
    linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
    radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.10) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(99,102,241,0.07) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 85%, rgba(6,182,212,0.05)  0%, transparent 45%);
  background-size: 32px 32px, 32px 32px, auto, auto, auto;
  mask-image: linear-gradient(to bottom, rgba(0,0,0,0.65), rgba(0,0,0,0.9));
}
.particle-canvas { position: fixed; inset: 0; z-index: -3; pointer-events: none; }
#app > *:not(.global-bg):not(.global-bg-overlay):not(.particle-canvas) {
  position: relative; z-index: 1;
}

/* ============================================================
   Element UI 深色覆写
============================================================ */

/* ----- 输入框 / 选择器 / 文本域 ----- */
.el-input__inner,
.el-textarea__inner {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 12px !important;
  color: var(--text-1) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
  transition: all var(--t-base);
}
.el-input__inner::placeholder,
.el-textarea__inner::placeholder {
  color: rgba(158,176,197,0.72) !important;
}
.el-input__inner:hover,
.el-textarea__inner:hover {
  border-color: rgba(96,165,250,0.22) !important;
}
.el-input__inner:focus,
.el-textarea__inner:focus {
  border-color: rgba(96,165,250,0.48) !important;
  box-shadow: 0 0 0 4px rgba(59,130,246,0.10) !important;
}
.el-select .el-input.is-focus .el-input__inner,
.el-select .el-input__inner:focus {
  border-color: rgba(96,165,250,0.48) !important;
}

/* ----- 弹窗 / 抽屉 / 下拉 ----- */
.el-dialog,
.el-drawer,
.el-select-dropdown,
.el-dropdown-menu,
.el-picker-panel {
  background: rgba(8, 18, 34, 0.94) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  box-shadow: 0 24px 60px rgba(2,8,23,0.36) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.el-dialog__header,
.el-dialog__footer,
.el-drawer__header {
  border-color: rgba(255,255,255,0.06) !important;
}
.el-dialog__title,
.el-drawer__header span,
.el-select-dropdown__item,
.el-dropdown-menu__item,
.el-picker-panel * {
  color: var(--text-1) !important;
}

/* ----- Tag / Pagination / Divider ----- */
.el-tag {
  border-radius: 999px !important;
  border-color: rgba(255,255,255,0.10) !important;
  backdrop-filter: blur(8px);
}
.el-pagination button,
.el-pagination .el-pager li {
  background: rgba(255,255,255,0.04) !important;
  color: var(--text-2) !important;
  border-radius: 10px !important;
}
.el-pagination .el-pager li.active {
  background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  color: #fff !important;
  box-shadow: 0 6px 16px rgba(37,99,235,0.28);
}
.el-divider {
  background-color: rgba(255,255,255,0.08) !important;
}

/* ----- 滚动条 ----- */
*::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
*::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.03);
}
*::-webkit-scrollbar-thumb {
  background: rgba(148,163,184,0.22);
  border-radius: 999px;
}
*::-webkit-scrollbar-thumb:hover {
  background: rgba(96,165,250,0.34);
}

/* ----- 按钮 ----- */
	.el-button {
  border-radius: var(--r-md);
	  font-weight: 500;
  font-size: 14px;
  height: 36px;
  padding: 0 16px;
  transition: all var(--t-base);
}
.el-button--primary {
  background: var(--primary); border-color: var(--primary); color: #fff;
  box-shadow: 0 2px 10px var(--primary-40);
}
.el-button--primary:hover {
  background: var(--primary-light); border-color: var(--primary-light);
  box-shadow: 0 4px 16px var(--primary-40); transform: translateY(-1px);
}
.el-button--primary:active { transform: none; }
.el-button--success { background: var(--success); border-color: var(--success); color:#fff; }
.el-button--success:hover { background:#059669; border-color:#059669; transform:translateY(-1px); }
.el-button--warning { background: var(--warning); border-color: var(--warning); color:#fff; }
.el-button--warning:hover { background:#d97706; border-color:#d97706; transform:translateY(-1px); }
.el-button--danger  { background: var(--danger);  border-color: var(--danger);  color:#fff; }
.el-button--danger:hover  { background:#dc2626; border-color:#dc2626; transform:translateY(-1px); }
/* plain 按钮 */
.el-button.is-plain {
  border-color: var(--bd); color: var(--text-2); background: var(--bg-card);
}
.el-button.is-plain:hover {
  border-color: var(--primary-light); color: var(--primary-light); background: var(--primary-10);
}
.el-button--primary.is-plain {
  background: var(--primary-10); border-color: var(--primary-40); color: var(--primary-light);
}
.el-button--primary.is-plain:hover {
  background: var(--primary-20); border-color: var(--primary-light); color:#fff;
}
/* text 按钮 */
.el-button--text {
  color: var(--primary-light) !important;
  background: transparent !important;
  border: none !important;
  padding: 0 6px;
  height: auto;
}
.el-button--text:hover { color: #93c5fd !important; }
.el-button--text.el-button--danger  { color: #f87171 !important; }
.el-button--text.el-button--success { color: #34d399 !important; }
.el-button--text.el-button--warning { color: #fbbf24 !important; }

/* ----- 卡片 ----- */
	.el-card {
  border-radius: var(--r-lg) !important;
  background: rgba(11, 28, 46, 0.78) !important;
  border: 1px solid var(--bd-sm) !important;
  box-shadow: var(--sh-sm);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  color: var(--text-1) !important;
  transition: box-shadow var(--t-base), border-color var(--t-base);
}
.el-card:hover { box-shadow: var(--sh-md); border-color: var(--bd) !important; }
.el-card__header {
  background: rgba(255,255,255,0.03) !important;
  border-bottom: 1px solid var(--bd-sm) !important;
  padding: 14px 20px;
  color: var(--text-1) !important;
  font-weight: 600;
  font-size: 15px;
}
.el-card__body { padding: 20px; background: transparent; }

/* ----- 统一去悬浮效果（列表/菜单/下拉） ----- */
.el-table__body tr:hover > td.el-table__cell,
.el-table__body tr.hover-row > td.el-table__cell,
.el-table__body tr.hover-row.el-table__row--striped > td.el-table__cell,
.el-table__fixed-body-wrapper tr.hover-row > td.el-table__cell,
.el-table__fixed-right-body-wrapper tr.hover-row > td.el-table__cell,
.el-table__body--wrapper tr:hover td,
.el-table tr.hover-row td,
.el-menu-item:hover,
.el-submenu__title:hover,
.el-select-dropdown__item:hover,
.el-dropdown-menu__item:hover,
.el-pagination .btn-prev:hover,
.el-pagination .btn-next:hover,
.el-pagination .el-pager li:hover,
	.el-card:hover {
  background: transparent !important;
  background-color: transparent !important;
  transform: none !important;
  box-shadow: none !important;
  color: inherit !important;
}

/* ----- 表格 ----- */
.el-table,
.el-table__body-wrapper,
.el-table__header-wrapper,
.el-table__footer-wrapper,
.el-table__fixed,
.el-table__fixed-right { background: transparent !important; }
	.el-table {
  color: var(--text-1);
  border: 1px solid var(--bd-sm);
  border-radius: var(--r-lg);
	  overflow: hidden;
}
.el-table::before,
.el-table::after { background: var(--bd-sm) !important; height: 1px; }
/* 表头 */
.el-table th.el-table__cell {
  background: rgba(255,255,255,0.04) !important;
  color: var(--text-2) !important;
	  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid var(--bd) !important;
  border-right: 1px solid var(--bd-sm) !important;
}
/* 单元格 */
.el-table td.el-table__cell {
  background: transparent !important;
  color: var(--text-1) !important;
  border-bottom: 1px solid var(--bd-sm) !important;
  border-right: 1px solid var(--bd-sm) !important;
}
.el-table .cell { color: var(--text-1) !important; }
.el-table th .cell { color: var(--text-2) !important; }
/* 行 */
.el-table tr { background: transparent !important; }
/* 斑马纹 */
.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: rgba(255,255,255,0.02) !important;
}
/* hover — 完全不高亮，用多重选择器确保覆盖 Element UI 行内样式 */
.el-table__body tr:hover > td.el-table__cell,
.el-table__body tr.hover-row > td.el-table__cell,
.el-table__body tr.hover-row.el-table__row--striped > td.el-table__cell,
.el-table__fixed-body-wrapper tr.hover-row > td.el-table__cell,
.el-table__fixed-right-body-wrapper tr.hover-row > td.el-table__cell,
.el-table__body--wrapper tr:hover td,
.el-table tr.hover-row td {
  background-color: transparent !important;
  background: transparent !important;
}
/* 固定列背景 */
.el-table__fixed-body-wrapper td.el-table__cell,
.el-table__fixed-right-body-wrapper td.el-table__cell { background: #0d1f34 !important; }
/* border 表格边框 */
.el-table--border { border-color: var(--bd-sm) !important; }
.el-table--border td.el-table__cell,
.el-table--border th.el-table__cell { border-color: var(--bd-sm) !important; }
.el-table--border::before,
.el-table--border::after { background: var(--bd-sm) !important; }
/* 空状态 */
.el-table__empty-text { color: var(--text-3); }

/* ----- 输入框 ----- */
.el-input__inner,
.el-textarea__inner {
  border-radius: var(--r-md);
  border: 1px solid var(--bd);
  background: var(--bg-card) !important;
  color: var(--text-1);
  transition: all var(--t-base);
  font-size: 14px;
}
.el-input__inner::placeholder,
.el-textarea__inner::placeholder { color: var(--text-3); }
.el-input__inner:hover,
.el-textarea__inner:hover { border-color: var(--primary-light); }
.el-input__inner:focus,
.el-textarea__inner:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-10);
  background: var(--bg-card-hv) !important;
  outline: none;
}
.el-input__prefix, .el-input__suffix, .el-input__icon { color: var(--text-3); }
.el-input__count { display: none !important; }

.el-input-number {
  width: 100%;
}
.el-input-number__decrease,
.el-input-number__increase {
  background: rgba(11, 28, 46, 0.88) !important;
  color: var(--text-2) !important;
  border-color: var(--bd-sm) !important;
}
.el-input-number__decrease:hover,
.el-input-number__increase:hover {
  background: var(--primary-10) !important;
  color: var(--primary-light) !important;
}
.el-input-number .el-input__inner {
  background: rgba(255,255,255,0.07) !important;
}

/* ----- 表单 ----- */
.el-form-item__label { color: var(--text-2); font-weight: 500; }
.el-form-item__error { color: #f87171; font-size: 12px; }

/* ----- 下拉选择 ----- */
.el-select-dropdown,
.el-dropdown-menu {
  border-radius: var(--r-md);
  box-shadow: var(--sh-lg);
  border: 1px solid var(--bd);
  background: #0e2135 !important;
  padding: 4px 0;
}
.el-select-dropdown__item,
.el-dropdown-menu__item {
  color: var(--text-2);
  padding: 0 14px;
  line-height: 36px;
  transition: all var(--t-fast);
}
.el-select-dropdown__item:hover,
.el-dropdown-menu__item:hover {
  background: var(--primary-10) !important;
  color: var(--primary-light);
}
.el-select-dropdown__item.selected {
  color: var(--primary-light);
  background: var(--primary-10) !important;
  font-weight: 600;
}

/* ----- 菜单（彻底清除白色） ----- */
.el-menu,
.el-menu--inline,
.el-submenu,
.el-submenu__title,
.el-menu-item,
.el-menu--vertical,
.el-menu--popup,
.el-menu--popup-bottom-start {
  background-color: transparent !important;
  background: transparent !important;
}
.el-menu.el-menu--inline {
  background: rgba(255,255,255,0.02) !important;
}
/* 展开的子菜单容器 */
.el-submenu > .el-menu {
  background: rgba(0,0,0,0.15) !important;
}

/* ----- 对话框 ----- */
.el-dialog__wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}
.el-dialog {
  margin: 0 auto !important;
  max-height: calc(100vh - 40px);
}
.el-dialog {
  border-radius: var(--r-xl);
  overflow: hidden;
  background: #0e2135 !important;
  border: 1px solid var(--bd);
  box-shadow: var(--sh-xl);
}
.el-dialog__header {
  background: rgba(255,255,255,0.03);
  padding: 18px 24px 14px;
  border-bottom: 1px solid var(--bd-sm);
}
.el-dialog__title { color: var(--text-1); font-weight: 700; font-size: 16px; }
.el-dialog__body  { padding: 24px; color: var(--text-2); background: transparent; }
.el-dialog__footer { padding: 14px 24px 18px; border-top: 1px solid var(--bd-sm); background: transparent; }
.el-dialog__close { color: var(--text-3); }
.el-dialog__close:hover { color: var(--text-1); }
.el-dialog .el-form-item__label { color: var(--text-2); }
.el-dialog .el-input__inner,
.el-dialog .el-textarea__inner {
  background: rgba(255,255,255,0.07) !important;
  border-color: var(--bd);
  color: var(--text-1);
}

/* ----- 确认弹窗 ----- */
.el-message-box {
  background: #0e2135 !important;
  border: 1px solid var(--bd);
  border-radius: var(--r-xl);
  box-shadow: var(--sh-xl);
}
.el-message-box__title   { color: var(--text-1); font-weight: 600; }
.el-message-box__content { color: var(--text-2); }
.el-message-box__message p { color: var(--text-2); }
.v-modal {
  background: rgba(0,0,0,0.60) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

/* ----- 对话框 footer 次按钮统一去白底 ----- */
.el-dialog__footer .el-button:not(.el-button--primary):not(.el-button--danger):not(.el-button--success) {
  background: var(--warning) !important;
  border-color: var(--warning) !important;
  color: #fff !important;
}
.el-dialog__footer .el-button:not(.el-button--primary):not(.el-button--danger):not(.el-button--success):hover {
  background: #d97706 !important;
  border-color: #d97706 !important;
  color: #fff !important;
}

/* ----- 确认弹窗取消按钮统一去白底 ----- */
.el-message-box__btns .el-button:not(.el-button--primary) {
  background: var(--warning) !important;
  border-color: var(--warning) !important;
  color: #fff !important;
}
.el-message-box__btns .el-button:not(.el-button--primary):hover {
  background: #d97706 !important;
  border-color: #d97706 !important;
  color: #fff !important;
}

/* ----- 消息提示 ----- */
	.el-message {
  border-radius: var(--r-md);
  background: #0e2135 !important;
  border: 1px solid var(--bd);
  color: var(--text-1);
  box-shadow: var(--sh-lg);
  padding: 12px 16px;
}
.el-message--success { border-color: rgba(16,185,129,0.4); }
.el-message--warning { border-color: rgba(245,158,11,0.4); }
.el-message--error   { border-color: rgba(239,68,68,0.4); }
.el-message--info    { border-color: rgba(6,182,212,0.4); }
.el-message .el-icon-success { color: var(--success); }
.el-message .el-icon-warning { color: var(--warning); }
.el-message .el-icon-error   { color: var(--danger); }
.el-message .el-icon-info    { color: var(--info); }

/* ----- 通知 ----- */
.el-notification {
  border-radius: var(--r-lg);
  background: #0e2135 !important;
  border: 1px solid var(--bd);
  color: var(--text-1);
  box-shadow: var(--sh-xl);
}
.el-notification__title   { color: var(--text-1); font-weight: 600; }
.el-notification__content { color: var(--text-2); font-size: 13px; }

/* ----- 分页 ----- */
.el-pagination { color: var(--text-2); margin-top: 16px; }
.el-pagination button,
.el-pagination .btn-prev,
.el-pagination .btn-next,
.el-pagination .el-pager li,
.el-pagination .el-pagination__sizes .el-input__inner,
.el-pagination .el-pagination__jump .el-input__inner {
  border-radius: var(--r-sm);
  background: rgba(11, 28, 46, 0.88) !important;
  color: var(--text-2) !important;
  border: 1px solid var(--bd-sm) !important;
  min-width: 32px;
  height: 32px;
  line-height: 30px;
}
.el-pagination .btn-prev:hover,
.el-pagination .btn-next:hover,
.el-pagination .el-pager li:hover,
.el-pagination .el-pagination__sizes .el-input__inner:hover,
.el-pagination .el-pagination__jump .el-input__inner:hover {
  color: var(--primary-light) !important;
  border-color: var(--primary-40) !important;
}
.el-pagination .el-pager li.active {
  color: var(--primary-light) !important;
  background: var(--primary-10) !important;
  border-color: var(--primary-40) !important;
  font-weight: 600;
}
.el-pagination__total,
.el-pagination__jump,
.el-pagination__sizes {
  color: var(--text-2) !important;
}
.el-pagination .el-select .caret,
.el-pagination .btn-prev i,
.el-pagination .btn-next i {
  color: var(--text-2) !important;
}
.el-pagination__jump .el-input__inner { height: 28px; line-height: 28px; }

/* ----- 标签 ----- */
.el-tag {
  border-radius: var(--r-sm);
  border: none !important;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 10px;
  background: rgba(59,130,246,0.15) !important;
  background-color: rgba(59,130,246,0.15) !important;
  color: #93c5fd !important;
}
.el-tag--success {
  background: rgba(16,185,129,0.15) !important;
  background-color: rgba(16,185,129,0.15) !important;
  color: #34d399 !important;
}
.el-tag--warning {
  background: rgba(245,158,11,0.15) !important;
  background-color: rgba(245,158,11,0.15) !important;
  color: #fbbf24 !important;
}
.el-tag--danger  {
  background: rgba(239,68,68,0.15) !important;
  background-color: rgba(239,68,68,0.15) !important;
  color: #f87171 !important;
}
.el-tag--info {
  background: rgba(148,163,184,0.15) !important;
  background-color: rgba(148,163,184,0.15) !important;
  color: #cbd5e1 !important;
}

/* ----- 复选框 & 单选框 ----- */
.el-checkbox__inner,
.el-radio__inner {
  border: 1px solid var(--bd);
  background: var(--bg-card);
}
.el-checkbox__input.is-checked .el-checkbox__inner,
.el-radio__input.is-checked .el-radio__inner {
  background: var(--primary); border-color: var(--primary);
}
.el-checkbox__label,
.el-radio__label { color: var(--text-2); }

/* ----- 开关 ----- */
.el-switch__core { border-color: var(--bd); background: var(--bg-card); }
.el-switch.is-checked .el-switch__core { border-color: var(--primary); background: var(--primary); }

/* ----- 白色背景兜底清除 ----- */
.el-collapse-item__header,
.el-collapse-item__wrap,
.el-descriptions,
.el-descriptions__header,
.el-descriptions__body,
.el-empty,
.el-empty__description p {
  color: var(--text-1) !important;
}
.el-card {
  background-color: rgba(11, 28, 46, 0.78);
  border-color: var(--bd-sm);
}

.el-picker-panel {
  background: #0e2135 !important;
  border: 1px solid var(--bd);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-xl);
  color: var(--text-1);
}
.el-date-table th { color: var(--text-3); border-color: var(--bd-sm); }
.el-date-table td { color: var(--text-2); }
.el-date-table td.today span { color: var(--primary-light); font-weight: 600; }
.el-date-table td.current:not(.disabled) span {
  background: var(--primary); color: #fff; border-radius: var(--r-sm);
}
.el-date-table td:hover span { background: var(--primary-10); color: var(--primary-light); }
.el-date-table td.disabled div { background: rgba(255,255,255,0.02); color: var(--text-3); }
.el-picker-panel__icon-btn { color: var(--text-2); }
.el-picker-panel__icon-btn:hover { color: var(--primary-light); }
.el-picker-panel__header { color: var(--text-1); }
.el-year-table td .cell,
.el-month-table td .cell { color: var(--text-2); }
.el-year-table td .cell:hover,
.el-month-table td .cell:hover { color: var(--primary-light); }
.el-year-table td.current .cell,
.el-month-table td.current .cell { color: var(--primary-light); font-weight: 600; }
.el-picker-panel__shortcut { color: var(--text-2); }
.el-picker-panel__shortcut:hover { color: var(--primary-light); }
.el-date-range-picker__time-header { border-color: var(--bd-sm); }
.el-date-range-picker__content { border-color: var(--bd-sm) !important; }

/* ----- 树形 ----- */
.el-tree {
  background: transparent !important;
  color: var(--text-1);
}
.el-tree-node__content { border-radius: var(--r-sm); transition: background var(--t-fast); }
.el-tree-node__content:hover { background: rgba(59,130,246,0.08) !important; }
.el-tree-node.is-current > .el-tree-node__content {
  background: rgba(59,130,246,0.14) !important;
  color: var(--primary-light);
}
.el-tree-node__label { color: var(--text-1); }
.el-tree__empty-text { color: var(--text-3); }

/* ----- 加载遮罩 ----- */
.el-loading-mask { background: rgba(12,25,41,0.75); backdrop-filter: blur(4px); }
.el-loading-spinner .path { stroke: var(--primary-light); }
.el-loading-spinner .el-loading-text { color: var(--primary-light); }

/* ----- 工具提示 ----- */
.el-tooltip__popper {
  border-radius: var(--r-md);
  background: #1a3a5c !important;
  border: 1px solid var(--bd);
  color: var(--text-1);
  box-shadow: var(--sh-lg);
  font-size: 13px;
}
.el-tooltip__popper.is-dark  { background: #1a3a5c !important; }
.el-tooltip__popper.is-light { background: #0e2135 !important; color: var(--text-1); }

/* ----- popover ----- */
.el-popover {
  background: #0e2135 !important;
  border: 1px solid var(--bd);
  color: var(--text-1);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-xl);
}
.el-popover__title { color: var(--text-1); font-weight: 600; }

/* ----- 描述列表 ----- */
.el-descriptions { background: transparent !important; }
.el-descriptions__header .el-descriptions__title { color: var(--text-1); font-weight: 600; }
.el-descriptions__body { background: transparent !important; }
.el-descriptions-item__label {
  color: var(--text-2) !important;
  background: rgba(255,255,255,0.03) !important;
  font-weight: 500;
}
.el-descriptions-item__content {
  color: var(--text-1) !important;
  background: transparent !important;
}
.el-descriptions--border .el-descriptions-item__label,
.el-descriptions--border .el-descriptions-item__content {
  border-color: var(--bd-sm) !important;
}

/* ----- 折叠面板 ----- */
.el-collapse { border: 1px solid var(--bd-sm); border-radius: var(--r-lg); overflow: hidden; }
.el-collapse-item__header {
  background: var(--bg-card);
  color: var(--text-1);
  border-bottom: 1px solid var(--bd-sm);
  font-weight: 500;
}
.el-collapse-item__wrap { background: transparent; border-bottom: 1px solid var(--bd-sm); }
.el-collapse-item__content { color: var(--text-2); padding: 16px 20px; }

/* ----- 上传 ----- */
.el-upload--picture-card {
  background: var(--bg-card);
  border: 1px dashed var(--bd);
  border-radius: var(--r-md);
  color: var(--text-2);
}
.el-upload--picture-card:hover { border-color: var(--primary-light); color: var(--primary-light); }
.el-upload-list--picture-card .el-upload-list__item {
  background: var(--bg-card); border-color: var(--bd); border-radius: var(--r-md);
}

/* ----- 时间线 ----- */
.el-timeline-item__tail { border-left-color: var(--bd); }
.el-timeline-item__timestamp { color: var(--text-3); }
.el-timeline-item__content { color: var(--text-1); }

/* ----- 抽屉 ----- */
.el-drawer { background: #0e2135 !important; border-left: 1px solid var(--bd); }
.el-drawer__header { color: var(--text-1); border-bottom: 1px solid var(--bd-sm); padding: 18px 24px; }
.el-drawer__body { color: var(--text-2); padding: 20px 24px; }

/* ----- 分割线 ----- */
.el-divider { border-color: var(--bd-sm) !important; }
.el-divider__text {
  background: transparent !important;
  background-color: transparent !important;
  color: var(--text-1) !important;
}

/* ----- 面包屑 ----- */
.el-breadcrumb { color: var(--text-3); }
.el-breadcrumb__inner { color: var(--text-2) !important; transition: color var(--t-fast); }
.el-breadcrumb__inner:hover { color: var(--primary-light) !important; }
.el-breadcrumb__item:last-child .el-breadcrumb__inner { color: var(--text-1) !important; font-weight: 600; }
.el-breadcrumb__separator { color: var(--text-3); }

/* ----- 数字输入框 ----- */
.el-input-number__decrease,
.el-input-number__increase {
  background: var(--bg-card); border-color: var(--bd); color: var(--text-2);
}
.el-input-number__decrease:hover,
.el-input-number__increase:hover { color: var(--primary-light); }

/* ----- 步骤条 ----- */
.el-step__head.is-finish  { color: var(--primary); border-color: var(--primary); }
.el-step__head.is-process { color: var(--primary-light); border-color: var(--primary-light); }
.el-step__title { color: var(--text-2); }
.el-step__title.is-finish,
.el-step__title.is-process { color: var(--text-1); }

/* ----- 头部 ----- */
.el-header { background: transparent !important; }

/* ----- 图片预览 ----- */
.el-image-viewer__close { color: #fff; }
.el-image-viewer__mask  { background: rgba(0,0,0,0.88); }

/* ----- 空状态 ----- */
.el-empty__description p { color: var(--text-3); }

/* ============================================================
   滚动条
============================================================ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(96,165,250,0.35); }

/* ----- 详情弹窗统一深色（列表进入详情页） ----- */
.order-detail-dialog .el-dialog,
.user-detail-dialog .el-dialog {
  background: #0e2135 !important;
  border: 1px solid var(--bd) !important;
  box-shadow: var(--sh-xl) !important;
}
.order-detail-dialog .el-dialog__header,
.user-detail-dialog .el-dialog__header {
  background: rgba(255,255,255,0.03) !important;
  border-bottom: 1px solid var(--bd-sm) !important;
}
.order-detail-dialog .el-dialog__body,
.user-detail-dialog .el-dialog__body,
.order-detail-dialog .el-dialog__footer,
.user-detail-dialog .el-dialog__footer {
  background: transparent !important;
  border-color: var(--bd-sm) !important;
}
.order-detail-dialog .info-card,
.user-detail-dialog .info-section {
  background: rgba(11, 28, 46, 0.78) !important;
  border: 1px solid var(--bd-sm) !important;
  border-radius: var(--r-md) !important;
}
.order-detail-dialog .card-header,
.user-detail-dialog .section-title {
  background: rgba(255,255,255,0.03) !important;
  color: var(--text-1) !important;
  border-color: var(--bd-sm) !important;
}
.order-detail-dialog .label,
.order-detail-dialog .service-label,
.user-detail-dialog .label,
.user-detail-dialog .image-label {
  color: var(--text-2) !important;
}
.order-detail-dialog .value,
.order-detail-dialog .service-value,
.order-detail-dialog .service-price,
.order-detail-dialog .subtotal,
.order-detail-dialog .total-value,
.user-detail-dialog .value,
.user-detail-dialog .no-image {
  color: var(--text-1) !important;
}
.order-detail-dialog .info-row,
.user-detail-dialog .info-item,
.user-detail-dialog .section-title {
  border-color: var(--bd-sm) !important;
}
.user-detail-dialog .no-image,
.user-detail-dialog .user-image {
  border-color: var(--bd) !important;
}
.user-detail-dialog .detail-content::-webkit-scrollbar-track,
.order-detail-dialog .detail-container::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.03) !important;
}
.user-detail-dialog .detail-content::-webkit-scrollbar-thumb,
.order-detail-dialog .detail-container::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.16) !important;
}

/* 去掉详情弹窗首次进入模糊感（关闭默认过渡缩放） */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: none !important;
}
.dialog-fade-enter,
.dialog-fade-leave-to {
  opacity: 1 !important;
  transform: none !important;
}

/* ============================================================
   页面通用布局
============================================================ */
/* 根容器背景透明 */
.content,
.community-data-container,
.page-container,
.list-container { background: transparent !important; color: var(--text-1); }

/* 搜索表单区 */
.search-form {
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(12px);
  border: 1px solid var(--bd-sm);
  border-radius: var(--r-lg);
  padding: 14px 20px 4px;
  margin-bottom: 16px;
}
.el-form--inline .el-form-item__label { color: var(--text-2); }

/* 工具栏 */
.toolbar {
  display: flex; align-items: center; justify-content: flex-end;
  margin-bottom: 14px;
}

/* 页面标题 */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title  { font-size: 18px; font-weight: 700; color: var(--text-1); margin: 0; letter-spacing: 0.3px; }

/* 卡片标题 */
.box-card .el-card__header,
.box-card .el-card__header * { color: var(--text-1); }

/* 数字统计 */
.stat-number { color: var(--primary-light); font-weight: 700; }
.stat-label  { color: var(--text-3); font-size: 13px; }

/* ECharts 背景透明 */
.chart-container,
[id*="chart"],
[class*="echarts"] { background: transparent !important; }

/* 工具类 */
.text-1 { color: var(--text-1) !important; }
.text-2 { color: var(--text-2) !important; }
.text-3 { color: var(--text-3) !important; }
.text-success { color: var(--success) !important; }
.text-warning { color: var(--warning) !important; }
.text-danger  { color: var(--danger)  !important; }
.text-info    { color: var(--info)    !important; }
.glass {
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--bd-sm);
  border-radius: var(--r-lg);
}

/* 响应式 */
@media (max-width: 768px) {
  body { font-size: 13px; }
  .el-button { height: 32px; padding: 0 12px; font-size: 13px; }
  .el-card__header, .el-card__body { padding: 12px 16px; }
  .el-dialog { width: 95% !important; margin: 0 auto; }
	}
	</style>