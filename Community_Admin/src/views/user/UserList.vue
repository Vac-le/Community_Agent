<template>
	<div class="app-page-container">
		<div class="page-header-actions">
			<div class="search-group">
				<el-input 
					placeholder="搜索用户名称" 
					v-model="form.name" 
					class="modern-input" 
					@keyup.enter.native="searchUser">
				</el-input>
				<el-input 
					placeholder="手机号查询" 
					v-model="form.phone" 
					class="modern-input" 
					@keyup.enter.native="searchUser">
				</el-input>
				<el-button type="primary" icon="el-icon-search" class="modern-btn search-btn" @click="searchUser">查询</el-button>
			</div>
			<div class="action-group">
				<el-button type="success" icon="el-icon-download" class="modern-btn ghost" @click="exportExcel">导出数据</el-button>
				<el-button type="primary" icon="el-icon-refresh" class="modern-btn circle-btn" circle @click="searchUser"></el-button>
			</div>
		</div>
		
		<el-card class="modern-card table-card" shadow="never">
			<el-table :data="users" class="glass-table" :header-cell-style="headerStyle" border>
				<el-table-column prop="name" label="姓名" min-width="120">
				  <template slot-scope="scope">
						<div class="user-cell">
							<div class="user-avatar-mini">{{ scope.row.name ? scope.row.name.charAt(0) : 'U' }}</div>
							<span>{{ scope.row.name }}</span>
						</div>
				  </template>
			  </el-table-column>
				<el-table-column prop="gender" label="性别" width="80" align="center">
		        <template slot-scope="scope">
						<el-tag :type="scope.row.gender === '男' ? 'primary' : 'danger'" size="mini" effect="dark" class="gender-tag">
							{{ scope.row.gender }}
						</el-tag>
		        </template>
		      </el-table-column>
				<el-table-column prop="age" label="年龄" width="80" align="center"></el-table-column>
				<el-table-column prop="phone" label="手机号" min-width="140"></el-table-column>
				<el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip></el-table-column>
				<el-table-column label="所属社区" min-width="150">
					<template slot-scope="scope">
						<div class="community-tag">
							<i class="el-icon-office-building"></i>
							<span>{{ scope.row.community ? scope.row.community.name : '未绑定' }}</span>
	</div>
				  </template>
			  </el-table-column>
				<el-table-column label="操作" width="220" align="center" fixed="right">
		        <template slot-scope="scope">
						<div class="table-ops">
							<el-button size="mini" type="text" class="op-btn primary" icon="el-icon-view" @click="viewDetail(scope.row.id)">详情</el-button>
							<el-button size="mini" type="text" class="op-btn warning" icon="el-icon-key" @click="resetPassword(scope.row.id)">重置</el-button>
							<el-button size="mini" type="text" class="op-btn danger" icon="el-icon-delete" @click="deleteUser(scope.row.id)">删除</el-button>
						</div>
		        </template>
		      </el-table-column>
	    </el-table>
			
			<div class="pagination-container">
		<el-pagination
		      @size-change="handleSizeChange"
		      @current-change="handleCurrentChange"
		      :current-page="form.pageNo"
					:page-sizes="[10, 20, 50, 100]"
		      :page-size="form.pageSize"
		      layout="total, sizes, prev, pager, next, jumper"
		      :total="total"
		      background>
		</el-pagination>
			</div>
	</el-card>

	<Detail ref="detail"></Detail>
	</div>
</template>

<script>
import Detail from "./Detail.vue"
import { exportRowsToExcel } from "../../utils/excel"

export default {
	components: { Detail },
	data() {
		return {
			form: {
				name: "",
				phone: "",
				pageNo: 1,
				pageSize: 10
			},
			users: [],
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
		searchUser() {
			this.$http.post("/api/userCtl/userList", this.form).then(resp => {
				if (resp.data.code === 200) {
				this.users = resp.data.data.list;
				this.total = resp.data.data.total;
				}
			});
		},
		handleSizeChange(val) {
			this.form.pageSize = val;
			this.searchUser();
		},
		handleCurrentChange(val) {
			this.form.pageNo = val;
			this.searchUser();
		},
		viewDetail(id) {
			this.$refs.detail.dialogVisible = true;
			this.$refs.detail.loadUserDetail(id);
		},
		resetPassword(id) {
			this.$confirm('确定重置该用户密码吗？', '安全提示', {
				type: 'warning',
				customClass: 'dark-message-box'
			}).then(() => {
				this.$http.post("/api/userCtl/reset", "id=" + id).then(() => {
					this.$message.success('密码已成功重置');
				});          
			});	
		},
		deleteUser(id) {
			this.$confirm('删除后数据不可恢复，是否继续？', '极其危险的操作', {
				confirmButtonText: '狠心删除',
				cancelButtonText: '再想想',
				type: 'error',
				customClass: 'dark-message-box'
			}).then(() => {
				this.$http.get("/api/userCtl/deleteUser?id=" + id).then(() => {
					this.$message.success('用户已删除');
					this.searchUser();
					});
				});
		},
		exportExcel() {
			if (!this.users.length) return this.$message.warning('暂无可导出的数据');
			const rows = [['姓名', '性别', '年龄', '手机号', '地址', '所属社区']];
			this.users.forEach(u => rows.push([
				u.name, u.gender, u.age, u.phone, u.address, u.community ? u.community.name : '-'
			]));
			exportRowsToExcel('社区用户列表', rows);
		}
	},
	mounted() {
		this.searchUser();
	}
}
</script>

<style scoped>
.app-page-container {
		padding: 0;
	animation: fadeIn 0.4s ease-out;
}

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
	flex: 1;
	max-width: 800px;
}

.modern-input {
	width: 220px;
}

.modern-input >>> .el-input__inner {
	background: rgba(15, 23, 42, 0.6) !important;
	border: 1px solid rgba(255, 255, 255, 0.08) !important;
	color: #f8fafc !important;
	border-radius: 12px;
	height: 42px;
	transition: all 0.3s ease;
}

.modern-input >>> .el-input__inner:focus {
	border-color: #3b82f6 !important;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.modern-btn {
	border-radius: 12px;
	height: 42px;
	padding: 0 20px;
	font-weight: 500;
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modern-btn.ghost {
	background: rgba(56, 189, 248, 0.1);
	border: 1px solid rgba(56, 189, 248, 0.2);
	color: #7dd3fc;
}

.modern-btn.ghost:hover {
	background: rgba(56, 189, 248, 0.2);
	transform: translateY(-2px);
}

.modern-card {
	background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(10, 18, 34, 0.9)) !important;
	border: 1px solid rgba(255, 255, 255, 0.06) !important;
	border-radius: 20px;
	backdrop-filter: blur(20px);
	overflow: hidden;
}

.glass-table {
	background: transparent !important;
}

.glass-table >>> tr {
	background-color: transparent !important;
}

.glass-table >>> .el-table__row {
	transition: all 0.3s ease;
}

.glass-table >>> .el-table__row:hover td {
	background-color: rgba(255, 255, 255, 0.03) !important;
}

.glass-table >>> td {
	border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
	padding: 14px 0;
	color: #cbd5e1;
}

.user-cell {
		display: flex;
		align-items: center;
	gap: 12px;
}

.user-avatar-mini {
	width: 32px;
	height: 32px;
	border-radius: 10px;
	background: linear-gradient(135deg, #3b82f6, #0ea5e9);
	color: white;
		display: flex;
	align-items: center;
	justify-content: center;
	font-weight: bold;
		font-size: 14px;
	box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
}

.community-tag {
	display: inline-flex;
		align-items: center;
	gap: 6px;
	color: #94a3b8;
	font-size: 13px;
	}
	
.table-ops {
		display: flex;
	justify-content: center;
		gap: 8px;
	}
	
.op-btn {
	font-weight: 600 !important;
	padding: 4px 8px !important;
	transition: all 0.2s;
}

.op-btn:hover {
	filter: brightness(1.2);
	transform: scale(1.05);
}

.op-btn.primary { color: #60a5fa !important; }
.op-btn.warning { color: #fbbf24 !important; }
.op-btn.danger { color: #f87171 !important; }

.pagination-container {
	padding: 24px;
		display: flex;
		justify-content: flex-end;
}

.pagination-container >>> .el-pagination.is-background .el-pager li:not(.disabled).active {
	background-color: #3b82f6;
}

.pagination-container >>> .el-pagination.is-background .btn-next,
.pagination-container >>> .el-pagination.is-background .btn-prev,
.pagination-container >>> .el-pagination.is-background .el-pager li {
	background-color: rgba(255, 255, 255, 0.05);
	color: #94a3b8;
	border: 1px solid rgba(255, 255, 255, 0.05);
}

@keyframes fadeIn {
	from { opacity: 0; transform: translateY(10px); }
	to { opacity: 1; transform: translateY(0); }
	}
</style>