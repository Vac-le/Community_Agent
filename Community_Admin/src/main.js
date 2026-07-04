import Vue from 'vue'
import App from './App.vue'
//导入路由组件
import router from './router/index.js'
Vue.use(router);
// 向Vue组件对象中自定义一个属性
Vue.prototype.serveradd = "http://127.0.0.1:8089/"

//导入Element-mui.import 
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
Vue.use(ElementUI);

// global css reset for layout 全局样式的默认配置
import './assets/css/global.css';

//导入并配置axios
import axios from 'axios';
//配置后端服务地址
axios.defaults.baseURL="http://127.0.0.1:8089/";
//将axios对象挂载到vue对象上,并为axios定义一个别名
Vue.prototype.$http = axios;

//导入echarts
import * as echarts from 'echarts'; //导入echarts组件
Vue.prototype.echarts = echarts;//将echarts组件绑定到vue对象

//文本编辑器插件
import mavonEditor from 'mavon-editor';
import 'mavon-editor/dist/css/index.css';
Vue.use(mavonEditor);

//markdown 格式转为 html 组件
import showdown from 'showdown'
Vue.prototype.converter = new showdown.Converter();

//axios请求拦截 当每次使用axios向后端发送get/post请求时,都会自动执行拦截器,让我们可以携带一些数据发送到后端
axios.interceptors.request.use(config =>{
//为请求头对象，添加 Token 验证的 token 字段
	config.headers.token = sessionStorage.getItem('token');
	// config.headers.userToken = localStorage.getItem('userToken');
	return config;
})

// 添加响应拦截器(后端对前端的响应)
axios.interceptors.response.use((resp) =>{//正常响应拦截
	if(resp.data.code==500){//java后端异常
		ElementUI.Message({message:"服务器忙,请稍后再试",type:"error"});
		return;
	}
	if(resp.data.code==401){//token过期
		sessionStorage.clear();
		router.replace("/login");
		ElementUI.Message({message:"登录失效,请重新登录!",type:"error"});
		return;
	}
	if(resp.data.code==501){//token过期
		localStorage.clear();
		router.replace("/userLogin");
		ElementUI.Message({message:"登录失效,请重新登录!",type:"error"});
		return;
	}
	return resp;
});

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
  router,
}).$mount('#app')
