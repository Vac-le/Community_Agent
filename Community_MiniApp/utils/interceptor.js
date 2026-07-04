// 请求拦截器
const requestInterceptor = {
    invoke(args) {
        // 添加token到请求头
        const token = uni.getStorageSync('token');
        if (token) {
			args.header = args.header || {};
            args.header.token = token;
        }

        // 流式请求不显示全局加载弹窗，避免遮挡聊天内容输出。
        const isStreamRequest = !!args.enableChunked;
        if (!isStreamRequest && args.showLoading !== false) {
            console.log('显示Loading...');
            uni.showLoading({
                title: '加载中...',
                mask: true
            });
        }
        return args;
    },
    
    success(res) {
        console.log('拦截器-请求成功:', res.data);
        uni.hideLoading();
        
        // 统一处理响应,token过期
        if (res.data && res.data.code === 401) {
            console.log('Token过期，跳转登录页');
            // token过期，清除本地存储并跳转登录
            uni.removeStorageSync('token');
            uni.removeStorageSync('userId');
            uni.redirectTo({
                url: '/pages/login/login'
            });
			return;
        }
		if(res.data && res.data.code === 500) {
            console.log('服务器错误');
			uni.showToast({
			    title: '网络错误，请重试',
			    icon: 'none'
			});
			return;
		}
        
        return res;
    },
    fail(err) {

        uni.hideLoading();
        uni.showToast({
            title: '网络错误，请重试',
            icon: 'none'
        });
        return err;
    }
};

export default {
    // 安装拦截器
    install() {
        // 请求拦截器
        uni.addInterceptor('request', requestInterceptor);
    },
};