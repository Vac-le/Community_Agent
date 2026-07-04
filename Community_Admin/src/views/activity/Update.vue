<template>
	<el-dialog 
		title="修改活动" 
		:visible.sync="dialogVisible" 
		width="60%"
		top="10vh"
		:close-on-click-modal="false"
		:append-to-body="true"
		custom-class="activity-update-dialog"
		@close="closeDialog">
		<el-form :model="form" :rules="rules" ref="form" label-width="100px">
			<el-form-item label="活动标题" prop="title">
				<el-input v-model="form.title" placeholder="请输入活动标题" maxlength="100" style="width: 80%;"></el-input>
			</el-form-item>
			
			<el-form-item label="封面图片" prop="img">
				<el-upload
					class="avatar-uploader"
					:action="serverAdd"
					:headers="{token:token}"
					:show-file-list="false"
					:on-success="handleAvatarSuccess"
					:before-upload="beforeAvatarUpload"
					accept="image/*">
					<img v-if="imageUrl" :src="imageUrl" class="avatar">
					<i v-else class="el-icon-plus avatar-uploader-icon"></i>
				</el-upload>
				<div class="upload-tip">建议尺寸：750x400像素，支持jpg、png格式，大小不超过2MB</div>
			</el-form-item>
			
			<el-form-item label="活动内容" prop="content" style="width: 90%;">
				<mavon-editor 
					ref="md" 
					v-model="form.content" 
					:toolbars="toolbars"
					@imgAdd="imgAdd" 
					@imgDel="imgDel"
					style="height: 250px !important; min-height: 250px !important; max-height: 250px !important;"/>
			</el-form-item>
			
			<el-form-item label="发布时间">
				<el-input v-model="form.operTime" disabled style="width: 80%;"></el-input>
			</el-form-item>
		</el-form>
		
		<span slot="footer" class="dialog-footer">
			<el-button type="warning" @click="closeDialog">取 消</el-button>
			<el-button type="primary" @click="submitForm" :loading="loading">确 定</el-button>
		</span>
	</el-dialog>
</template>

<script>
export default {
	data() {
		return {
			dialogVisible: false,
			loading: false,
			id: null,
			form: {
				title: '',
				content: '',
				img: '',
				operTime: ''
			},
			serverAdd: "",
			token: sessionStorage.getItem("token"),
			imageUrl: '',
			rules: {
				title: [
					{ required: true, message: '请输入活动标题', trigger: 'blur' },
					{ min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
				],
				content: [
					{ required: true, message: '请输入活动内容', trigger: 'blur' }
				]
			},
			toolbars: {
				bold: true, italic: true, header: true, underline: true,
				strikethrough: true, mark: true, quote: true, ol: true, ul: true,
				link: true, imagelink: true, code: true, table: true,
				fullscreen: true, readmodel: true, htmlcode: true, help: true,
				undo: true, redo: true, trash: true, save: false,
				navigation: true, subfield: true, preview: true
			}
		}
	},
	mounted() {
		this.serverAdd = this.$http.defaults.baseURL + 'api/productCtl/uploadImg';
	},
	methods: {
		// 根据ID获取活动信息
		getActivityById() {
			// 构建查询参数，只有当id有值时才传递
			const params = {
				pageNo: 1,
				pageSize: 10
			};
			if (this.id) {
				params.id = this.id;
			}
			
			this.$http.post('api/communityCtl/activityList', params).then((resp) => {
				if (resp.data.code === 200 && resp.data.data.list && resp.data.data.list.length > 0) {
					// 如果传了id，应该只返回一条匹配的记录
					const activity = resp.data.data.list.find(item => item.id === this.id) || resp.data.data.list[0];
					this.form = activity;
					this.imageUrl = activity.img;
				}
			});
		},
		submitForm() {
			this.$refs.form.validate((valid) => {
				if (valid) {
					this.loading = true;
					this.$http.post('api/communityCtl/updateActivity', {
						id: this.id,
						...this.form
					}).then((resp) => {
						this.loading = false;
						if (resp.data.code === 200) {
							this.$message.success('修改成功');
							this.closeDialog();
							this.$emit('refresh');
						} else {
							this.$message.error(resp.data.message || '修改失败');
						}
					}).catch(() => {
						this.loading = false;
					});
				}
			});
		},
		closeDialog() {
			this.dialogVisible = false;
			this.$refs.form.resetFields();
			this.form = {
				title: '',
				content: '',
				img: '',
				operTime: ''
			};
			this.id = null;
			this.imageUrl = '';
		},
		imgAdd(pos, file) {
			var formdata = new FormData();
			formdata.append('file', file);
			this.$http({
				url: this.serverAdd,
				data: formdata,
				method: "post",
				headers: { 'Content-Type': 'multipart/form-data', 'token': this.token }
			}).then((resp) => {
				this.$refs.md.$img2Url(pos, resp.data.data);
			})
		},
		imgDel(pos) {
			var imgUrl = pos[0];
			this.$http.get("/api/activityCtl/delImg", { params: { imgurl: JSON.stringify(imgUrl) } })
				.then(function (res) {
					// 删除回调
				})
		},
		handleAvatarSuccess(resp, file) {
			this.imageUrl = URL.createObjectURL(file.raw);
			this.form.img = resp.data;
		},
		beforeAvatarUpload(file) {
			const isImage = file.type.startsWith('image/');
			const isLt2M = file.size / 1024 / 1024 < 2;

			if (!isImage) {
				this.$message.error('只能上传图片文件!');
			}
			if (!isLt2M) {
				this.$message.error('上传图片大小不能超过 2MB!');
			}
			return isImage && isLt2M;
		}
	}
}
</script>

<style scoped>
.avatar-uploader {
	border: 1px dashed #d9d9d9;
	border-radius: 8px;
	cursor: pointer;
	position: relative;
	overflow: hidden;
	transition: all 0.3s;
	width: 80px;
	height: 80px;
	display: inline-block;
}

.avatar-uploader:hover {
	border-color: #409EFF;
}

.avatar-uploader-icon {
	font-size: 24px;
	color: #8c939d;
	width: 80px;
	height: 80px;
	line-height: 80px;
	text-align: center;
	display: block;
}

.avatar {
	width: 80px;
	height: 80px;
	display: block;
	object-fit: cover;
}

.upload-tip {
	font-size: 12px;
	color: #909399;
	margin-top: 8px;
	line-height: 1.5;
}

/* 对话框样式 - 完全参照详情页实现 */
.activity-update-dialog {
	max-height: 80vh !important;
	overflow: hidden !important;
}

.activity-update-dialog >>> .el-dialog {
	margin: 0 auto !important;
	max-height: 80vh !important;
	overflow: hidden !important;
	display: flex !important;
	flex-direction: column !important;
}

.activity-update-dialog >>> .el-dialog__header {
	flex-shrink: 0;
	padding: 15px 20px !important;
}

.activity-update-dialog >>> .el-dialog__body {
	padding: 10px 15px !important;
	overflow-y: auto !important;
	flex: 1;
	max-height: calc(80vh - 100px) !important;
}

.activity-update-dialog >>> .el-dialog__footer {
	flex-shrink: 0;
	padding: 10px 20px !important;
}
</style>
