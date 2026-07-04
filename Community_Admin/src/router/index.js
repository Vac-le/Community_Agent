import Vue from 'vue';/* 导入Vue */
import router from 'vue-router'; /* 导入路由 */

// 导入我们自己创建的组件
import Login from "../views/Login.vue"
import Main from "../views/Main.vue"
import AdminList from'../views/admin/AdminList.vue';
import CommunityInfo from '../views/community/CommunityInfo.vue';
import UserList from '../views/user/UserList.vue';
import SendList from '../views/send/SendList.vue';
import PurchaseList from '../views/purchaseOrder/PurchaseList.vue';
import EatList from '../views/eatOrder/EatList.vue';
import HomeList from '../views/homeOrder/HomeList.vue';
import CommunityData from '../views/community/CommunityData.vue';
import OperLogList from '../views/log/OperLogList.vue';
import Community from '../views/community/Community.vue';
import FoodList from '../views/food/FoodList.vue';
import PurchaseProductList from '../views/purchase/PurchaseProductList.vue';
import HomeProductList from '../views/home/homeProductList.vue';
import ActivityList from '../views/activity/ActivityList.vue';
import NoticeList from '../views/notice/NoticeList.vue';
import AiChat from '../views/ai/AiChat.vue';
import ai from '../views/ai/AiChat.vue';
Vue.use(router);
/* 定义组件路由  创建vue-router对象*/
let rout = new router({
	routes: [
			{
				path: '/',//默认地址,自动访问指定组件
				component: Login//指定组件
			},
			{
				path: '/login',//为组件定义访问地址
				component: Login//指定组件
			},
			{
				path: '/main',//为组件定义访问地址
				component: Main,//指定组件
				children:[
					{
						path:'/adminList',
						component: AdminList//指定组件
					},
					{
						path:'/communityInfo',
						component:CommunityInfo
					},
					{
						path:'/userList',
						component:UserList
					},
					{
						path:'/sendList',
						component:SendList
					},
					{
						path:'/purchaseList',
						component:PurchaseList
					},
					{
						path:'/eatList',
						component:EatList
					},
					{
						path:'/homeList',
						component:HomeList
					},
					{
						path:'/communitydata',
						component:CommunityData
					},
					{
						path:'/community',
						component:Community
					},
					{
						path:'/operLogList',
						component:OperLogList
					},
					{
						path:'/foodList',
						component:FoodList
					},
					{
						path:'/homeProductList',
						component:HomeProductList
					},
					{
						path:'/purchaseProductList',
						component:PurchaseProductList
					},
					{
						path:'/activityList',
						component:ActivityList
					},
					{
						path:'/noticeList',
						component:NoticeList
					},
					{
						path:'/aiChat',
						component:AiChat
					},
					{
						path:'/ai',
						component:ai
					}
				]
			},
		]
	});
//导出路由对象
export default rout;

// 每次进行组件路由跳转时,都会触发下面代码的执行
rout.beforeEach((to,from,next)=>{
	//to.path获取的是我们本次要跳转的路由地址
	if(to.path=='/login'){//如果用户访问的登录页，直接放行
		return next();
	}else{//登录之外的组件路由,都要检查用户有没有登录
		//访问用户个人中心页面,或者访问后台
		// let userToken = localStorage.getItem("userToken");
		let account = sessionStorage.getItem("account");
		//访问用户个人中心,放行
		// if(to.path=="/userInfo")
		//  {
		// 	 if(userToken!=null)
		// 	 {
		// 		return next();
		// 	 }
		// 	 else{
		// 		return next("/userLogin");
		// 	 }
		//  }
		// else{//访问后台
			if(account==null){
				return next("/login");
			}else{
				return next();
			}
		// }
	}
})