<template>
	<div class="app-page-container">
		<div class="page-header-actions">
			<div class="search-group">
				<el-input 
					placeholder="搜索管理员账号" 
					v-model="form.account" 
					class="modern-input" 
					@keyup.enter.native="searchAdmin">
				</el-input>
				<el-button type="primary" icon="el-icon-search" class="modern-btn search-btn" @click="searchAdmin">查询</el-button>
				<el-button type="info" icon="el-icon-refresh" class="modern-btn ghost" @click="resetForm">重置</el-button>
			</div>
			<div class="action-group">
				<el-button type="primary" icon="el-icon-plus" class="modern-btn highlight" @click="addAdmin">新增管理</el-button>
				<el-button type="success" icon="el-icon-download" class="modern-btn ghost" @click="exportExcel">导出</el-button>
			</div>
		</div>

		<el-card class="modern-card table-card" shadow="never">
			<el-table :data="admins" class="glass-table" :header-cell-style="headerStyle" border>
				<el-table-column prop="account" label="账号" min-width="140">
					<template slot-scope="scope">
						<div class="admin-account-cell">
							<div class="admin-tag">{{ scope.row.type == 0 ? '超管' : '管理' }}</div>
							<span>{{ scope.row.account }}</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="gender" label="性别" width="80" align="center"></el-table-column>
				<el-table-column prop="phone" label="电话" min-width="140"></el-table-column>
				<el-table-column prop="admin.account" label="最后操作人" width="120" align="center">
					<template slot-scope="scope">
						<span class="operator-text">{{ scope.row.admin ? scope.row.admin.account : '-' }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="reg_time" label="创建/操作时间" width="180" align="center">
					<template slot-scope="scope">
						<div class="time-cell">
							<i class="el-icon-time"></i>
							<span>{{ scope.row.reg_time }}</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column label="操作" width="280" align="center" fixed="right">
					<template slot-scope="scope">
						<div class="table-ops">
							<el-button size="mini" type="text" class="op-btn primary" icon="el-icon-unlock" @click="lookMenu(scope.row.id)">权限</el-button>
							<el-button size="mini" type="text" class="op-btn warning" icon="el-icon-refresh-left" @click="reset(scope.row.id)">重置</el-button>
							<el-button size="mini" type="text" class="op-btn highlight" icon="el-icon-edit-outline" @click="updateAdmin(scope.row.id)">编辑</el-button>
							<el-button size="mini" type="text" class="op-btn danger" icon="el-icon-delete" @click="deleteAdmin(scope.row.id)">移除</el-button>
						</div>
					</template>
				</el-table-column>
			</el-table>
			
			<div class="pagination-container">
				<el-pagination
					@size-change="handleSizeChange"
					@current-change="handleCurrentChange"
					:current-page="form.pageNo"
					:page-sizes="[5, 10, 20]"
					:page-size="form.pageSize"
					layout="total, sizes, prev, pager, next, jumper"
					:total="total"
					background>
				</el-pagination>
			</div>
		</el-card>
		
		<Add ref="add" @refresh="searchAdmin"></Add>
		<Update ref="update" @refresh="searchAdmin"></Update>
		<Look ref="look"></Look>
	</div>
</template>

<script>
import Add from "./Add.vue"
import Update from "./Update.vue"
import Look from "./LookMenu.vue"
import { exportRowsToExcel } from "../../utils/excel"

export default {
	components: { Add, Update, Look },
	data() {
		return {
			form: { account: "", pageNo: 1, pageSize: 10 },
			admins: [],
			total: 0,
			headerStyle: {
				backgroundColor: 'rgba(15, 23, 42, 0.45)',
				color: '#94a3b8',
				fontWeight: '600',
				borderBottom: '1px solid rgba(255,255,255,0.08)',
				padding: '16px 0'
			}
		}
	},
	methods: {
		searchAdmin() {
			this.$http.post("/api/adminCtl/admins", this.form).then(resp => {
				if (resp.data.code === 200) {
					this.admins = resp.data.data.list;
					this.total = resp.data.data.total;
				}
			});
		},
		resetForm() {
			this.form = { account: "", pageNo: 1, pageSize: 10 };
			this.searchAdmin();
		},
		reset(id) {
			this.$confirm('确定重置该管理员密码吗？', '安全提示', {
				type: 'warning',
				customClass: 'dark-message-box'
			}).then(() => {
				this.$http.post("/api/adminCtl/reset", "id=" + id).then(() => {
					this.$message.success('密码已成功重置');
				});
			});
		},
		addAdmin() { this.$refs.add.dialogVisible = true; },
		lookMenu(id) { this.$refs.look.open(id); },
		updateAdmin(id) { this.$refs.update.open(id); },
		deleteAdmin(id) {
			this.$confirm('确定永久删除该管理员吗？', '极其危险', {
				type: 'error',
				customClass: 'dark-message-box'
			}).then(() => {
				this.$http.post("/api/adminCtl/deleteAdmin", "id=" + id).then(() => {
					this.$message.success('已成功移除');
					this.searchAdmin();
				});
			});
		},
		exportExcel() {
			if (!this.admins.length) return this.$message.warning('暂无可导出的数据');
			const rows = [['账号', '类型', '性别', '电话', '注册时间']];
			this.admins.forEach(item => rows.push([
				item.account, item.type == 0 ? '超级管理员' : '管理员', item.gender, item.phone, item.reg_time
			]));
			exportRowsToExcel('管理员名单', rows);
		},
		handleSizeChange(val) { this.form.pageSize = val; this.searchAdmin(); },
		handleCurrentChange(val) { this.form.pageNo = val; this.searchAdmin(); }
	},
	mounted() { this.searchAdmin(); }
}
</script>

<style scoped>
.app-page-container { animation: fadeIn 0.4s ease-out; }

.page-header-actions {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24px;
	gap: 20px;
}

.search-group {
	display: flex;
	gap: 12px;
}

.modern-input >>> .el-input__inner {
	background: rgba(15, 23, 42, 0.6) !important;
	border: 1px solid rgba(255, 255, 255, 0.08) !important;
	color: #f8fafc !important;
	border-radius: 12px;
	height: 42px;
}

.modern-btn {
	border-radius: 12px;
	height: 42px;
	padding: 0 20px;
	font-weight: 500;
	transition: all 0.3s ease;
}

.modern-btn.ghost {
	background: rgba(255, 255, 255, 0.04);
	border: 1px solid rgba(255, 255, 255, 0.08);
	color: #cbd5e1;
}

.modern-btn.highlight {
	background: linear-gradient(135deg, #3b82f6, #0ea5e9);
	border: none;
	box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.modern-card {
	background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(10, 18, 34, 0.9)) !important;
	border: 1px solid rgba(255, 255, 255, 0.06) !important;
	border-radius: 20px;
	backdrop-filter: blur(20px);
}

.glass-table {
	background: transparent !important;
}

.glass-table >>> tr { background-color: transparent !important; }

.glass-table >>> td {
	border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
	color: #cbd5e1;
	padding: 14px 0;
}

.admin-account-cell {
	display: flex;
	align-items: center;
	gap: 12px;
}

.admin-tag {
	padding: 2px 8px;
	background: rgba(59, 130, 246, 0.15);
	border: 1px solid rgba(59, 130, 246, 0.3);
	color: #60a5fa;
	border-radius: 6px;
	font-size: 11px;
	font-weight: 600;
}

.operator-text { color: rgba(148, 163, 184, 0.8); font-size: 13px; }

.time-cell {
	display: flex; align-items: center; justify-content: center; gap: 8px; color: #94a3b8; font-size: 13px;
}

.table-ops {
	display: flex; justify-content: center; gap: 8px;
}

.op-btn { font-weight: 600 !important; }
.op-btn.primary { color: #60a5fa !important; }
.op-btn.warning { color: #fbbf24 !important; }
.op-btn.highlight { color: #38bdf8 !important; }
.op-btn.danger { color: #f87171 !important; }

.pagination-container { padding: 24px; display: flex; justify-content: flex-end; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>