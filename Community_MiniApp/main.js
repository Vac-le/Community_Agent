import App from './App'
import interceptor from './utils/interceptor'

//统一配置地址
// 微信开发者工具和真机都不能稳定使用 127.0.0.1 指向你的电脑后端
// 请改成你电脑在当前网络下的 IPv4 地址
export const BASE_URL = 'http://127.0.0.1:8088'
// export const BASE_URL = 'http://127.0.0.1:8088'  // 本地开发
//export const BASE_URL = 'http://172.20.10.2:8088'  // 真机调试，手机热点ip
//47.109.197.113
Vue.prototype.$baseUrl = BASE_URL

//封装request请求,避免每次发起请求时都需要将ip和端口号写一遍
import {myRequest} from './utils/request.js'
Vue.prototype.$myRequest = myRequest

//安装全局的拦截器
interceptor.install();

// #ifndef VUE3
//不是vue3即vue2 配置信息都在这里写
import Vue from 'vue'
import './uni.promisify.adaptor'
Vue.config.productionTip = false
App.mpType = 'app'
const app = new Vue({
  ...App
})
app.$mount()

// #endif

// #ifdef VUE3
import { createSSRApp } from 'vue'
export function createApp() {
  const app = createSSRApp(App)
  return {
    app
  }
}
// #endif