<template>
	<div class="content">
		<el-card class="box-card">
			<div slot="header" class="clearfix">
				<span>社区信息管理</span>
				<el-button type="primary" size="small" class="edit-btn" v-if="!isEditing" @click="startEdit()">编辑信息</el-button>
			</div>

			<el-form ref="form" :model="communityForm" label-width="120px" class="community-form">
				<el-row :gutter="20">
					<el-col :span="12">
						<el-form-item label="社区ID:">
							<el-input v-model="communityForm.id" disabled></el-input>
						</el-form-item>
					</el-col>
					<el-col :span="12">
						<el-form-item label="城市ID:">
							<el-input v-model="communityForm.cityId" :disabled="!isEditing"></el-input>
						</el-form-item>
					</el-col>
				</el-row>

				<el-row :gutter="20">
					<el-col :span="24">
						<el-form-item label="社区名称:">
							<el-input v-model="communityForm.name" :disabled="!isEditing" placeholder="请输入社区名称"></el-input>
						</el-form-item>
					</el-col>
				</el-row>

				<el-row :gutter="20">
					<el-col :span="24">
						<el-form-item label="社区地址:">
							<el-input
								v-model="communityForm.address"
								:disabled="!isEditing"
								type="textarea"
								:rows="3"
								placeholder="请输入社区详细地址">
							</el-input>
						</el-form-item>
					</el-col>
				</el-row>

				<el-row :gutter="20">
					<el-col :span="12">
						<el-form-item label="管理员姓名:">
							<el-input v-model="communityForm.adminName" :disabled="!isEditing" placeholder="请输入管理员姓名"></el-input>
						</el-form-item>
					</el-col>
					<el-col :span="12">
						<el-form-item label="联系电话:">
							<el-input v-model="communityForm.adminPhone" :disabled="!isEditing" placeholder="请输入联系电话"></el-input>
						</el-form-item>
					</el-col>
				</el-row>

				<el-row v-if="isEditing">
					<el-col :span="24" style="text-align: center; margin-top: 20px;">
						<el-button @click="cancelEdit()">取消</el-button>
						<el-button type="primary" @click="saveCommunity()">保存修改</el-button>
					</el-col>
				</el-row>
			</el-form>

			<div class="statistics-section" v-if="!isEditing">
				<el-divider content-position="left">社区统计</el-divider>
				<el-row :gutter="20">
					<el-col :span="12">
						<div class="stat-card">
							<div class="stat-icon user-icon">
								<i class="el-icon-user"></i>
							</div>
							<div class="stat-content">
								<div class="stat-label">用户总数</div>
								<div class="stat-value">{{ statistics.users }}</div>
							</div>
						</div>
					</el-col>
					<el-col :span="12">
						<div class="stat-card">
							<div class="stat-icon send-icon">
								<i class="el-icon-truck"></i>
							</div>
							<div class="stat-content">
								<div class="stat-label">配送员总数</div>
								<div class="stat-value">{{ statistics.deliverymen }}</div>
							</div>
						</div>
					</el-col>
				</el-row>
			</div>
		</el-card>
	</div>
</template>

<script>
export default {
	data() {
		return {
			isEditing: false,
			communityForm: {
				id: "",
				name: "",
				address: "",
				adminName: "",
				adminPhone: "",
				cityId: ""
			},
			originalForm: {},
			statistics: {
				users: 0,
				deliverymen: 0
			}
		}
	},
	methods: {
		startEdit() {
			this.isEditing = true;
			this.originalForm = JSON.parse(JSON.stringify(this.communityForm));
		},
		cancelEdit() {
			this.$confirm('确定要取消编辑吗? 未保存的修改将会丢失', '提示', {
				confirmButtonText: '确定',
				cancelButtonText: '继续编辑',
				type: 'warning'
			}).then(() => {
				this.communityForm = JSON.parse(JSON.stringify(this.originalForm));
				this.isEditing = false;
				this.$message({ type: 'info', message: '已取消编辑', duration: 1000 });
			}).catch(() => {});
		},
		saveCommunity() {
			if (!this.communityForm.name) { this.$message({ message: '社区名称不能为空', type: 'warning', duration: 1000 }); return; }
			if (!this.communityForm.address) { this.$message({ message: '社区地址不能为空', type: 'warning', duration: 1000 }); return; }
			if (!this.communityForm.adminName) { this.$message({ message: '管理员姓名不能为空', type: 'warning', duration: 1000 }); return; }
			if (!this.communityForm.adminPhone) { this.$message({ message: '联系电话不能为空', type: 'warning', duration: 1000 }); return; }

			const phoneReg = /^1[3-9]\d{9}$/;
			if (!phoneReg.test(this.communityForm.adminPhone)) {
				this.$message({ message: '请输入正确的手机号码', type: 'warning', duration: 1000 });
				return;
			}

			this.$http.post("api/communityCtl/updateCommunityInfo", this.communityForm).then((resp) => {
				if (resp.data.code === 200 || resp.data.success) {
					this.$message({ message: '保存成功！', type: 'success', duration: 1000 });
					this.isEditing = false;
					this.loadCommunityInfo();
				} else {
					this.$message({ message: resp.data.message || '保存失败', type: 'error', duration: 2000 });
				}
			}).catch(() => {
				this.$message({ message: '保存失败，请重试', type: 'error', duration: 2000 });
			});
		},
		loadCommunityInfo() {
			this.$http.get("api/communityCtl/getCommunityInfo").then((resp) => {
				if (resp.data && resp.data.data) {
					this.communityForm = JSON.parse(JSON.stringify(resp.data.data));
					this.originalForm = JSON.parse(JSON.stringify(resp.data.data));
					this.statistics.deliverymen = resp.data.data.sendCount || 0;
					this.statistics.users = resp.data.data.userCount || 0;
				} else {
					this.$message({ message: '获取社区信息失败', type: 'error', duration: 2000 });
				}
			}).catch(() => {
				this.$message({ message: '加载数据失败，请刷新重试', type: 'error', duration: 2000 });
			});
		}
	},
	mounted() {
		this.loadCommunityInfo();
	}
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.content {
	min-height: 100%;
	background: transparent;
	padding: 20px;
}

.box-card {
	border-radius: 10px;
	box-shadow: 0 10px 28px rgba(0,0,0,0.28);
	border: 1px solid rgba(255,255,255,0.10);
	background: rgba(11, 28, 46, 0.80);
	backdrop-filter: blur(14px);
	-webkit-backdrop-filter: blur(14px);
	max-width: 1200px;
	margin: 0 auto;
}

.box-card >>> .el-card__header {
	background: rgba(255,255,255,0.04);
	border-bottom: 1px solid rgba(255,255,255,0.10);
	padding: 16px 20px;
}

.box-card .clearfix {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 18px;
	font-weight: 700;
	color: #f5f9ff;
}

.edit-btn {
	margin-left: auto;
	min-width: 88px;
	height: 34px;
	border-radius: 6px;
	font-size: 14px;
}

.community-form { padding: 20px; }
.community-form .el-form-item { margin-bottom: 20px; }

.community-form .el-form-item__label {
	font-weight: 600;
	color: #d9e6f7;
	font-size: 14px;
}

.community-form .el-input__inner,
.community-form .el-textarea__inner {
	border: 1px solid rgba(255,255,255,0.20);
	border-radius: 6px;
	font-size: 14px;
	color: #f4f8ff;
	background: rgba(255,255,255,0.05);
}

.community-form .el-input__inner:focus,
.community-form .el-textarea__inner:focus {
	border-color: #60a5fa;
}

.community-form .el-input.is-disabled .el-input__inner,
.community-form .el-textarea.is-disabled .el-textarea__inner {
	background-color: rgba(255,255,255,0.04);
	color: #e6eefb;
	cursor: not-allowed;
}

.statistics-section {
	padding: 20px;
	background: transparent;
	border-top: 1px solid rgba(255,255,255,0.10);
	margin-top: 20px;
	border-radius: 10px;
}

.el-divider { margin: 0 0 20px 0; }
.el-divider__text {
	font-weight: 700;
	color: #f2f7ff;
	font-size: 15px;
}

.stat-card {
	display: flex;
	align-items: center;
	padding: 20px;
	background: rgba(255,255,255,0.06);
	border-radius: 10px;
	border: 1px solid rgba(255,255,255,0.10);
	transition: all 0.25s ease;
}

.stat-card:hover {
	box-shadow: 0 4px 16px rgba(59,130,246,0.18);
	transform: translateY(-2px);
}

.stat-icon {
	width: 50px;
	height: 50px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24px;
	margin-right: 15px;
}

.user-icon {
	background: rgba(59,130,246,0.20);
	color: #78b3ff;
}

.send-icon {
	background: rgba(16,185,129,0.20);
	color: #5ee6b4;
}

.stat-content { flex: 1; }

.stat-label {
	font-size: 13px;
	color: #c8d7eb;
	margin-bottom: 5px;
}

.stat-value {
	font-size: 24px;
	font-weight: 700;
	color: #f8fbff;
}

@media (max-width: 768px) {
	.content { padding: 10px; }
	.stat-card { margin-bottom: 10px; }
}

.content::-webkit-scrollbar { width: 8px; }
.content::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
.content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.18); border-radius: 4px; }
.content::-webkit-scrollbar-thumb:hover { background: rgba(96,165,250,0.45); }
</style>
