<template>
	<div>
		<el-dialog title="用户详情" :visible.sync="dialogVisible" width="600px" v-loading="loading" class="user-detail-dialog">
		  <div class="detail-content">
				<!-- 基本信息卡片 -->
				<div class="info-section">
					<div class="section-title">
						<i class="el-icon-user"></i>
						<span>基本信息</span>
					</div>
					<el-row :gutter="20" class="info-row">
						<el-col :span="12">
							<div class="info-item">
								<span class="label">姓名：</span>
								<span class="value">{{ userInfo.name || '-' }}</span>
							</div>
						</el-col>
						<el-col :span="12">
							<div class="info-item">
								<span class="label">性别：</span>
								<span class="value">{{ userInfo.gender || '-' }}</span>
							</div>
						</el-col>
					</el-row>
					
					<el-row :gutter="20" class="info-row">
						<el-col :span="12">
							<div class="info-item">
								<span class="label">年龄：</span>
								<span class="value">{{ userInfo.age || '-' }}</span>
							</div>
						</el-col>
						<el-col :span="12">
							<div class="info-item">
								<span class="label">手机号：</span>
								<span class="value">{{ userInfo.phone || '-' }}</span>
							</div>
						</el-col>
					</el-row>
					
					<el-row :gutter="20" class="info-row">
						<el-col :span="24">
							<div class="info-item">
								<span class="label">地址：</span>
								<span class="value">{{ userInfo.address || '-' }}</span>
							</div>
						</el-col>
					</el-row>
					
					<el-row :gutter="20" class="info-row">
						<el-col :span="12">
							<div class="info-item">
								<span class="label">所属社区：</span>
								<span class="value">{{ userInfo.community && userInfo.community.name ? userInfo.community.name : '-' }}</span>
							</div>
						</el-col>
						<el-col :span="12">
							<div class="info-item">
								<span class="label">注册时间：</span>
								<span class="value">{{ formatTime(userInfo.regTime) }}</span>
							</div>
						</el-col>
					</el-row>
				</div>
				
				<!-- 图片信息卡片 -->
				<div class="info-section">
					<div class="section-title">
						<i class="el-icon-picture"></i>
						<span>图片信息</span>
					</div>
					<el-row :gutter="20" class="info-row">
						<el-col :span="12">
							<div class="image-item">
								<div class="image-label">用户头像</div>
								<div class="image-container">
									<el-image v-if="userInfo.userFace" class="user-image" :src="userInfo.userFace" fit="cover" :preview-src-list="[userInfo.userFace]"></el-image>
									<div v-else class="no-image">
										<i class="el-icon-user"></i>
										<span>未上传</span>
									</div>
								</div>
							</div>
						</el-col>
						<el-col :span="12">
							<div class="image-item">
								<div class="image-label">人脸照片</div>
								<div class="image-container">
									<el-image v-if="userInfo.img" class="user-image" :src="userInfo.img" fit="cover" :preview-src-list="[userInfo.img]"></el-image>
									<div v-else class="no-image">
										<i class="el-icon-picture"></i>
										<span>未上传</span>
									</div>
								</div>
							</div>
						</el-col>
					</el-row>
				</div>
		  </div>
		  <span slot="footer" class="dialog-footer">
		    
		  </span>
		</el-dialog>
	</div>
</template>

<script>
export default{
	data(){
		return{
			dialogVisible:false,
			userInfo:{},
			loading: false
		}
	},
	methods:{
		// 格式化时间
		formatTime(time){
			if(!time) return '-';
			// 处理 ISO 格式时间: 2025-09-19T16:00:00.000+00:00
			var date = new Date(time);
			var year = date.getFullYear();
			var month = String(date.getMonth() + 1).padStart(2, '0');
			var day = String(date.getDate()).padStart(2, '0');
			var hours = String(date.getHours()).padStart(2, '0');
			var minutes = String(date.getMinutes()).padStart(2, '0');
			var seconds = String(date.getSeconds()).padStart(2, '0');
			return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
		},
		loadUserDetail(id){
			// 清空上一次的数据
			this.userInfo = {};
			this.loading = true;
			
			// 实际API调用
			this.$http.get("api/userCtl/findSendById?id="+id).then((resp)=>{
				console.log('用户详情 - 完整响应:', resp);
				console.log('用户详情 - data:', resp.data);
				
				if(resp.data && resp.data.data){
					this.userInfo = resp.data.data;
					console.log('✅ 用户信息已加载:', JSON.stringify(this.userInfo, null, 2));
				} else {
					console.error('❌ 数据格式错误:', resp.data);
					this.$message({message: '获取用户详情失败', type: 'error', duration: 2000});
				}
			}).catch((error)=>{
				console.error('❌ 加载用户详情失败:', error);
				console.error('❌ 错误详情:', error.response);
				var errorMsg = '加载数据失败';
				if(error.response && error.response.data && error.response.data.msg){
					errorMsg += '：' + error.response.data.msg;
				} else if(error.message){
					errorMsg += '：' + error.message;
				}
				this.$message({message: errorMsg, type: 'error', duration: 2000});
			}).finally(() => {
				this.loading = false;
			});
		}
	}
}
</script>

<style scoped>
/* 对话框样式 */
.user-detail-dialog >>> .el-dialog__header {
	background: transparent;
	padding: 20px;
	border-bottom: 1px solid rgba(255,255,255,0.12);
}

.user-detail-dialog >>> .el-dialog__title {
	font-size: 16px;
	font-weight: 600;
	color: #303133;
}

.user-detail-dialog >>> .el-dialog__body {
	padding: 0;
}

.user-detail-dialog >>> .el-dialog__footer {
	padding: 15px 20px;
	border-top: 1px solid rgba(255,255,255,0.12);
	background: transparent;
	text-align: center;
}

/* 内容区域 */
.detail-content {
	padding: 20px;
	max-height: 500px;
	overflow-y: auto;
}

/* 滚动条美化 */
.detail-content::-webkit-scrollbar {
	width: 6px;
}

.detail-content::-webkit-scrollbar-track {
	background: #f5f5f5;
	border-radius: 3px;
}

.detail-content::-webkit-scrollbar-thumb {
	background: #c0c4cc;
	border-radius: 3px;
}

.detail-content::-webkit-scrollbar-thumb:hover {
	background: #909399;
}

/* 信息区块 */
.info-section {
	background: transparent;
	border-radius: 8px;
	border: 1px solid rgba(255,255,255,0.12);
	margin-bottom: 16px;
	padding: 16px;
}

.info-section:last-child {
	margin-bottom: 0;
}

/* 区块标题 */
.section-title {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 15px;
	font-weight: 600;
	color: #303133;
	margin-bottom: 16px;
	padding-bottom: 12px;
	border-bottom: 2px solid #f0f0f0;
}

.section-title i {
	color: #409eff;
	font-size: 16px;
}

/* 信息行 */
.info-row {
	margin-bottom: 12px;
}

.info-row:last-child {
	margin-bottom: 0;
}

/* 信息项 */
.info-item {
	display: flex;
	align-items: center;
	padding: 8px 0;
}

.info-item .label {
	color: #606266;
	font-size: 14px;
	font-weight: 500;
	min-width: 85px;
	flex-shrink: 0;
}

.info-item .value {
	color: #303133;
	font-size: 14px;
	flex: 1;
	word-break: break-all;
}

/* 图片项 */
.image-item {
	text-align: center;
}

.image-label {
	color: #606266;
	font-size: 14px;
	font-weight: 500;
	margin-bottom: 12px;
}

.image-container {
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 120px;
}

.user-image {
	width: 100px;
	height: 100px;
	border-radius: 8px;
	border: 2px solid #ebeef5;
	cursor: pointer;
	transition: all 0.3s ease;
}

.user-image:hover {
	border-color: #409eff;
	transform: scale(1.05);
	box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.no-image {
	width: 100px;
	height: 100px;
	border-radius: 8px;
	border: 2px dashed rgba(255,255,255,0.18);
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	gap: 8px;
	background: transparent;
	color: #909399;
}

.no-image i {
	font-size: 32px;
}

.no-image span {
	font-size: 12px;
}

/* 底部按钮 */
.dialog-footer .el-button {
	min-width: 100px;
}
</style>

