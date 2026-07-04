// 真机调试时需要修改为电脑IP地址
// 获取电脑IP方法：Windows命令行输入 ipconfig
import { BASE_URL } from '@/main.js'

export const myRequest = (options) => {
	return new Promise((resolve, reject) => {
		uni.request({
			url: BASE_URL + (options.url.startsWith('/') ? options.url : '/' + options.url),
			method: options.method || 'GET',
			data: options.data || {},
			header: options.header || {},
			success: (res) => {
				// 不在这里处理业务逻辑，交给拦截器统一处理
				resolve(res)
			},
			fail: (err) => {
				// 不在这里显示错误提示，交给拦截器统一处理
				reject(err)
			}
		})
	})
}