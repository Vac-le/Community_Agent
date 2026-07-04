<template>
	<el-dialog 
		title="新增公告" 
		:visible.sync="dialogVisible" 
		width="50%"
		top="10vh"
		:close-on-click-modal="false"
		:append-to-body="true"
		custom-class="notice-add-dialog"
		@close="closeDialog">
		<el-form :model="form" :rules="rules" ref="form" label-width="100px">
			<el-form-item label="公告标题" prop="title">
				<el-input v-model="form.title" placeholder="请输入公告标题" maxlength="100"></el-input>
			</el-form-item>
			
			<el-form-item label="公告内容" prop="content">
				<el-input 
					type="textarea" 
					v-model="form.content" 
					placeholder="请输入公告内容"
					:rows="10"
					maxlength="500"
					></el-input>
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
			form: {
				title: '',
				content: ''
			},
			rules: {
				title: [
					{ required: true, message: '请输入公告标题', trigger: 'blur' },
					{ min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
				],
				content: [
					{ required: true, message: '请输入公告内容', trigger: 'blur' },
					{ min: 5, max: 500, message: '长度在 5 到 500 个字符', trigger: 'blur' }
				]
			}
		}
	},
	methods: {
		submitForm() {
			this.$refs.form.validate((valid) => {
				if (valid) {
					this.loading = true;
					this.$http.post('api/communityCtl/addNotice', this.form).then((resp) => {
						this.loading = false;
						if (resp.data.code === 200) {
							this.$message.success('新增成功');
							this.closeDialog();
							this.$emit('refresh');
						} else {
							this.$message.error(resp.data.message || '新增失败');
						}
					}).catch(() => {
						this.loading = false;
						this.$message.error('新增失败，请稍后重试');
					});
				}
			});
		},
		closeDialog() {
			this.dialogVisible = false;
			this.$refs.form.resetFields();
			this.form = {
				title: '',
				content: ''
			};
		}
	}
}
</script>

<style scoped>
/* 对话框样式 */
.notice-add-dialog {
	max-height: 80vh !important;
	overflow: hidden !important;
}

.notice-add-dialog >>> .el-dialog {
	margin: 0 auto !important;
	max-height: 80vh !important;
	overflow: hidden !important;
	display: flex !important;
	flex-direction: column !important;
}

.notice-add-dialog >>> .el-dialog__header {
	flex-shrink: 0;
	padding: 15px 20px !important;
}

.notice-add-dialog >>> .el-dialog__body {
	padding: 10px 15px !important;
	overflow-y: auto !important;
	flex: 1;
	max-height: calc(80vh - 100px) !important;
}

.notice-add-dialog >>> .el-dialog__footer {
	flex-shrink: 0;
	padding: 10px 20px !important;
}

.notice-add-dialog >>> .el-textarea__inner {
	font-size: 14px;
	line-height: 1.6;
}
</style>

