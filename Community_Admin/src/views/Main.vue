<template>
	<div class="main-container">
		<el-container class="layout-container">
	  <!-- 左侧菜单 - 浅色风格 -->
	  <el-aside width="220px" class="light-sidebar">
			<div class="sidebar-header">
				<div class="logo-container">
					<div class="logo-mark">
						<span></span>
					</div>
					<div class="logo-copy">
						<p class="logo-kicker">SMART OPS</p>
						<span class="logo-text">智慧社区</span>
					</div>
				</div>
			</div>
		<el-menu 
			:default-openeds="defaultOpeneds" 
			router 
			class="light-menu"
			:background-color="menuTheme.background"
			:text-color="menuTheme.text"
			:active-text-color="menuTheme.activeText"
			:unique-opened="false"
			:collapse-transition="false">
				<!-- 父级菜单 -->
				<template v-for="parentMenu in parentMenus">
				  <!-- 有子菜单的父级菜单 -->
				  <el-submenu 
				    v-if="parentMenu.children && parentMenu.children.length > 0" 
				    :index="String(parentMenu.id)" 
				    :key="'submenu-' + parentMenu.id">
				  <template slot="title">
				      <i :class="getMenuIcon(parentMenu.name)"></i>
				      <span>{{parentMenu.name}}</span>
				  </template>
				    <!-- 子级菜单 -->
				    <el-menu-item 
				      :index="childMenu.url" 
				      class="menu-item" 
				      v-for="childMenu in parentMenu.children" 
				      :key="childMenu.id">
				      <i :class="getMenuIcon(childMenu.name)"></i>
				      <span>{{childMenu.name}}</span>
				    </el-menu-item>
				  </el-submenu>
				  <!-- 没有子菜单的父级菜单（直接显示为菜单项） -->
				  <el-menu-item 
				    v-else 
				    :index="parentMenu.url" 
				    class="menu-item" 
				    :key="'menuitem-' + parentMenu.id">
				    <i :class="getMenuIcon(parentMenu.name)"></i>
				    <span>{{parentMenu.name}}</span>
				  </el-menu-item>
				</template>
			</el-menu>
		</el-aside>
		<el-container class="content-container">
		  <el-header class="top-header" v-if="$route.path !== '/community' && currentMenu !== '社区数据'">
		  	<div class="top-header-content">
		  		<div class="top-header-left">
		  			<div class="page-breadcrumb">
		  				<p class="page-breadcrumb-label">CURRENT MODULE</p>
		  				<h2>{{ currentMenu || '智慧社区管理后台' }}</h2>
		  			</div>
		  		</div>
		  		<div class="top-header-right">
		  			<div class="header-status-pill">
		  				<span class="status-dot"></span>
		  				<span>系统运行正常</span>
		  			</div>
		  			<div class="user-profile header-profile">
		  				<img src="../assets/头像.jpg" alt="用户头像" class="user-avatar">
		  				<div class="user-info">
		  					<div class="user-name">{{account}}</div>
		  					<div class="user-email">{{account}}@example.com</div>
		  				</div>
		  			</div>
		  			<el-button type="text" class="header-action" @click="updatePassword">修改密码</el-button>
		  			<el-button type="primary" size="small" class="header-action header-logout-btn" @click="logout">退出登录</el-button>
		  		</div>
		  	</div>
		  </el-header>
		  <!-- 主内容区 -->
		  <el-main class="modern-main">
			<div class="app-container" :class="{'dashboard-page': $route.path === '/community' || currentMenu === '社区数据'}">
				<router-view></router-view>
			</div>
		  </el-main>
		</el-container>
		</el-container>
		<Update ref="update"></Update>
	</div>
</template>

<script>
import Update from "./Update.vue"
export default{
		components:{
			Update
		},
		data(){
			return{
				account:"",
				menus:[],
				parentMenus:[],
				defaultOpeneds:[],
				currentMenu: "",
			menuTheme: {
				background: "transparent",
				text: "rgba(148,163,184,0.85)",
				activeText: "#60a5fa"
			},
			// SSE连接对象
			eventSource: null
			}
	},
	methods:{
		logout(){
		    this.$confirm('您确定要退出吗?','提示',{
		        confirmButtonText: '确定',
		        cancelButtonText: '取消',
		        type: 'warning'
		    }).then(() => {
			// 关闭SSE连接
			if (this.eventSource) {
				this.eventSource.close();
				this.eventSource = null;
			}
			sessionStorage.clear();
			this.$router.push("/login");
		    })
		},
		updatePassword(){
			this.$refs.update.dialogVisible = true;
		},
		// 构建菜单树形结构
		buildMenuTree(menus) {
			// 找出所有父级菜单（parent_id为0或NULL）
			const parents = menus.filter(menu => !menu.parentId || menu.parentId === 0);
			
			// 为每个父级菜单找到对应的子菜单
			parents.forEach(parent => {
				parent.children = menus.filter(menu => menu.parentId === parent.id);
			});
			
			return parents;
		},
		// 根据菜单名称获取对应图标
		getMenuIcon(name) {
			const iconMap = {
				'管理员管理': 'el-icon-user-solid',
				'社区数据': 'el-icon-data-analysis',
				'社区信息管理': 'el-icon-office-building',
				'用户管理': 'el-icon-user',
				'配送员管理': 'el-icon-s-custom',
				'社区天气': 'el-icon-partly-cloudy',
				'家政订单管理': 'el-icon-s-order',
				'代购订单管理': 'el-icon-shopping-cart-2',
				'餐饮订单管理': 'el-icon-food',
				'家政商品管理': 'el-icon-s-goods',
				'代购商品管理': 'el-icon-goods',
				'餐饮商品管理': 'el-icon-dish',
				'社区从告管理': 'el-icon-bell',
				'社区活动管理': 'el-icon-s-flag',
				'订单管理': 'el-icon-s-order',
				'社区管理': 'el-icon-office-building',
				'商品管理': 'el-icon-s-goods',
				'AI助手': 'el-icon-magic-stick',
				'智能助手': 'el-icon-magic-stick',
				'AI问答': 'el-icon-magic-stick'
			};
			return iconMap[name] || 'el-icon-menu';
		},
		// 初始化订单通知SSE连接
		initOrderNotification() {
			const token = sessionStorage.getItem('token');
			if (!token) {
				return;
			}
			
			// 构建SSE连接URL（EventSource不支持自定义header，所以用URL参数传递token）
			const baseURL = this.$http.defaults.baseURL.replace(/\/$/, ''); // 移除末尾的斜杠
			const url = `${baseURL}/api/notification/order/stream?token=${token}`;
			
			// 建立SSE连接
			this.eventSource = new EventSource(url);
			
			// 监听新订单事件
			this.eventSource.addEventListener('newOrder', (event) => {
				try {
					const result = JSON.parse(event.data);
					if (result.code === 200) {
						const order = result.data;
						console.log('收到新订单：', order);
						
						// 显示Element UI通知
						this.$notify({
							title: '新订单提醒',
							message: `订单号：${order.id}，金额：¥${order.amount}`,
							type: 'success',
							duration: 5000,
							position: 'top-right',
							onClick: () => {
								// 点击通知后跳转到对应订单列表
								this.navigateToOrderList(order);
							}
						});
						
						// 显示浏览器原生通知
						this.showBrowserNotification(order);
						
						// 如果当前在订单列表页面，刷新列表
						this.refreshOrderListIfNeeded();
					}
				} catch (error) {
					console.error('解析订单通知失败：', error);
				}
			});
			
			// 连接打开
			this.eventSource.onopen = () => {
				console.log('订单通知SSE连接已建立');
			};
			
			// 连接错误（会自动重连）
			this.eventSource.onerror = (error) => {
				console.error('订单通知SSE连接错误：', error);
				// 如果连接关闭，尝试重新连接
				if (this.eventSource && this.eventSource.readyState === EventSource.CLOSED) {
					console.log('SSE连接已关闭，5秒后尝试重连...');
					setTimeout(() => {
						if (sessionStorage.getItem('token')) {
							this.initOrderNotification();
						}
					}, 5000);
				}
			};
		},
		// 显示浏览器原生通知
		showBrowserNotification(order) {
			if ('Notification' in window) {
				if (Notification.permission === 'granted') {
					new Notification('新订单提醒', {
						body: `订单号：${order.id}，金额：¥${order.amount}元`,
						icon: '/favicon.ico',
						tag: `order-${order.id}` // 相同tag的通知会被替换
					});
				} else if (Notification.permission !== 'denied') {
					// 请求通知权限
					Notification.requestPermission().then(permission => {
						if (permission === 'granted') {
							new Notification('新订单提醒', {
								body: `订单号：${order.id}，金额：¥${order.amount}元`,
								icon: '/favicon.ico'
							});
						}
					});
				}
			}
		},
		// 根据订单类型跳转到对应订单列表
		navigateToOrderList(order) {
			// 根据订单类型判断跳转到哪个列表
			// 假设order.type.id表示订单类型：1-餐饮，2-代购，3-家政
			if (order.type && order.type.id) {
				const typeId = order.type.id;
				if (typeId === 1) {
					this.$router.push('/eatList');
				} else if (typeId === 2) {
					this.$router.push('/purchaseList');
				} else if (typeId === 3) {
					this.$router.push('/homeList');
				}
			}
		},
		// 如果当前在订单列表页面，刷新列表
		refreshOrderListIfNeeded() {
			const currentPath = this.$route.path;
			if (currentPath === '/eatList' || currentPath === '/purchaseList' || currentPath === '/homeList') {
				// 通过事件总线通知子组件刷新
				this.$nextTick(() => {
					// 触发路由刷新，让子组件重新加载数据
					this.$forceUpdate();
				});
			}
		}
	},
		mounted() {
		this.account = sessionStorage.getItem("account");
		this.currentMenu = this.$route.path === '/main' ? '智慧社区管理后台' : '';
		
		// 建立订单通知SSE连接
		this.initOrderNotification();
		
		//登录成功后,向后端发送请求,查询管理员对应菜单
		this.$http.get("api/menuCtl/menus").then((resp)=>{
				this.menus = resp.data.data;
				console.log("原始菜单数据:", this.menus);
				
				// 构建菜单树（包含所有父级菜单）
				this.parentMenus = this.buildMenuTree(this.menus);
				
				console.log("菜单树结构:", this.parentMenus);
				
				// 设置默认展开的父级菜单（展开所有有子级的父级菜单）
				this.defaultOpeneds = this.parentMenus
					.filter(parent => parent.children && parent.children.length > 0)
					.map(parent => String(parent.id));
				const activeMenu = this.menus.find(m => m.url === this.$route.path);
				this.currentMenu = activeMenu ? activeMenu.name : '智慧社区管理后台';
		});
	},
	// 组件销毁时关闭SSE连接
	beforeDestroy() {
		if (this.eventSource) {
			this.eventSource.close();
			this.eventSource = null;
			console.log('SSE连接已关闭');
		}
	},
	watch: {
		$route(to) {
			// 更新当前菜单名称
			const path = to.path;
			const menu = this.menus.find(m => m.url === path);
			this.currentMenu = menu ? menu.name : '';
		}
	}
}
</script>
<style scoped>
/* ========== 深色毛玻璃主布局 — 高级感统一升级 ========== */
.main-container {
  --sidebar-width: 236px;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  display: flex;
  background: transparent;
}

.layout-container {
  height: 100vh;
  width: 100%;
  display: flex;
  overflow: hidden;
}

.light-sidebar {
  position: relative;
  z-index: 10;
  background: linear-gradient(180deg, rgba(8, 16, 31, 0.94), rgba(10, 23, 42, 0.88));
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 12px 0 40px rgba(2, 8, 23, 0.32);
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width) !important;
  flex: 0 0 var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100vh;
  overflow: hidden;
}

.light-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  border: none;
  background: transparent;
  padding: 12px 8px 18px;
}

.sidebar-header {
  height: 88px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-container {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
}

.logo-mark {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #38bdf8, #2563eb);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.logo-kicker {
  margin: 0;
  font-size: 10px;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.9);
}

.logo-text {
  color: #f8fafc;
  font-weight: 700;
  font-size: 17px;
  line-height: 1.2;
}

.light-menu >>> .el-submenu__title,
.light-menu >>> .el-menu-item {
  height: 44px;
  line-height: 44px;
  border-radius: 10px;
  margin: 4px 6px;
  color: rgba(226, 232, 240, 0.86) !important;
}

.light-menu >>> .el-submenu__title i,
.light-menu >>> .el-menu-item i {
  color: rgba(148, 163, 184, 0.95) !important;
}

.light-menu >>> .el-submenu__title:hover,
.light-menu >>> .el-menu-item:hover {
  background: rgba(59, 130, 246, 0.14) !important;
  color: #e2e8f0 !important;
}

.light-menu >>> .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.35), rgba(56, 189, 248, 0.22)) !important;
  color: #ffffff !important;
}

.light-menu >>> .el-menu-item.is-active i {
  color: #ffffff !important;
}

.content-container {
  height: 100vh;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.top-header {
  height: 74px;
  min-height: 74px;
  background: rgba(10, 18, 34, 0.64);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0 28px;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  box-shadow: 0 10px 30px rgba(2, 8, 23, 0.16);
  flex-shrink: 0;
}

.top-header-content {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.top-header-left {
  display: flex;
  align-items: center;
}

.page-breadcrumb-label {
  margin: 0 0 4px;
  font-size: 10px;
  color: rgba(125, 211, 252, 0.78);
  letter-spacing: 0.26em;
}

.page-breadcrumb h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #f8fbff;
}

.top-header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 9px 14px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.54);
  border: 1px solid rgba(96,165,250,0.14);
  color: #dbeafe;
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 10px rgba(34,197,94,0.8);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  border: 1px solid rgba(96, 165, 250, 0.35);
  object-fit: cover;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.18);
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.user-avatar:hover {
  transform: scale(1.06);
  border-color: #60a5fa;
}

.user-info .user-name {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 90px;
}

.user-info .user-email {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 90px;
}

.header-profile {
  padding-right: 16px;
  border-right: 1px solid rgba(255, 255, 255, 0.10);
}

.header-action {
  color: rgba(191, 204, 222, 0.86) !important;
  font-weight: 500;
  font-size: 13px;
}

.header-action:hover { color: #ffffff !important; }

.header-logout-btn {
  color: #ffffff !important;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  border-color: #2563eb !important;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28);
}

.modern-main {
  background: transparent;
  padding: 28px 32px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;
}

.app-container {
  min-height: 100%;
  background: transparent;
}

.app-container.dashboard-page {
  min-height: max-content;
}


@media (max-width: 900px) {
  .top-header-content {
    align-items: flex-start;
    flex-direction: column;
    justify-content: center;
  }

  .top-header-right {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .light-sidebar { width: 72px !important; flex: 0 0 72px !important; min-width: 72px !important; }
  .logo-copy,
  .light-menu >>> .el-menu-item span,
  .light-menu >>> .el-submenu__title span,
  .user-info,
  .page-breadcrumb-label,
  .header-status-pill { display: none; }
  .modern-main { padding: 16px; }
  .top-header { padding: 0 16px; }
  .page-breadcrumb h2 { font-size: 18px; }
}
</style>