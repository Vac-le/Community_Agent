<template>
	<div class="app-page-container">
		<div class="page-header-actions">
			<div class="search-group">
				<el-input 
					placeholder="搜索公告标题" 
					v-model="form.title" 
					class="modern-input" 
					@keyup.enter.native="searchNotice">
				</el-input>
				<el-button type="primary" icon="el-icon-search" class="modern-btn search-btn" @click="searchNotice">查询</el-button>
				<el-button type="info" icon="el-icon-refresh" class="modern-btn ghost" @click="resetQuery">重置</el-button>
			</div>
			<div class="action-group">
				<el-button type="primary" icon="el-icon-plus" class="modern-btn highlight" @click="addNotice">发布新公告</el-button>
				<el-button type="success" icon="el-icon-download" class="modern-btn ghost" @click="exportExcel">导出 Excel</el-button>
			</div>
		</div>

		<el-card class="modern-card table-card" shadow="never">
			<el-table :data="notices" class="glass-table" :header-cell-style="headerStyle" :cell-style="cellStyle" border>
				<el-table-column type="index" label="序" width="60" align="center"></el-table-column>
				<el-table-column prop="title" label="公告标题" min-width="200" show-overflow-tooltip align="center">
					<template slot-scope="scope">
						<span class="notice-title-text">{{ scope.row.title }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="content" label="公告内容" min-width="300" show-overflow-tooltip align="center">
					<template slot-scope="scope">
						<span class="notice-body-text">{{ scope.row.content }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="operTime" label="发布时间" width="180" align="center">
					<template slot-scope="scope">
						<div class="time-cell">
							<i class="el-icon-time"></i>
							<span>{{ scope.row.operTime }}</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column label="操作" width="220" align="center" fixed="right">
					<template slot-scope="scope">
						<div class="table-ops">
							<el-button size="mini" type="text" class="op-btn primary" icon="el-icon-view" @click="viewNotice(scope.row)">查看</el-button>
							<el-button size="mini" type="text" class="op-btn warning" icon="el-icon-edit" @click="updateNotice(scope.row.id)">编辑</el-button>
							<el-button size="mini" type="text" class="op-btn danger" icon="el-icon-delete" @click="deleteNotice(scope.row.id)">删除</el-button>
						</div>
					</template>
				</el-table-column>
			</el-table>

			<div class="pagination-container">
				<el-pagination
					@size-change="handleSizeChange"
					@current-change="handleCurrentChange"
					:current-page="form.pageNo"
					:page-sizes="[10, 20, 50]"
					:page-size="form.pageSize"
					layout="total, sizes, prev, pager, next, jumper"
					:total="total"
					background>
				</el-pagination>
			</div>
		</el-card>

		<el-dialog 
			title="社区公告详情" 
			:visible.sync="detailVisible" 
			width="600px"
			custom-class="modern-dark-dialog"
			:append-to-body="true">
			<div class="notice-detail-view" v-if="currentNotice">
				<h2 class="detail-title">{{ currentNotice.title }}</h2>
				<div class="detail-meta">
					<i class="el-icon-time"></i> 发布时间：{{ currentNotice.operTime }}
				</div>
				<div class="detail-body">
					{{ currentNotice.content }}
				</div>
			</div>
		</el-dialog>

		<Add ref="add" @refresh="searchNotice"></Add>
		<Update ref="update" @refresh="searchNotice"></Update>
	</div>
</template>

<script>
import Add from "./Add.vue"
import Update from "./Update.vue"
import { exportRowsToExcel } from "../../utils/excel"

export default {
	components: { Add, Update },
	data() {
		return {
			form: { title: "", pageNo: 1, pageSize: 10 },
			notices: [],
			total: 0,
			detailVisible: false,
			currentNotice: null,
			headerStyle: {
				backgroundColor: 'rgba(15, 23, 42, 0.45)',
				color: '#94a3b8',
				fontWeight: '600',
				borderBottom: '1px solid rgba(255,255,255,0.08)',
				padding: '16px 0'
			},
			cellStyle: {
				textAlign: 'center'
			}
		}
	},
	methods: {
		searchNotice() {
			this.$http.post("api/communityCtl/noticeList", this.form).then(resp => {
				if (resp.data.code === 200) {
					this.notices = resp.data.data.list;
					this.total = resp.data.data.total;
				}
			});
		},
		resetQuery() { this.form = { title: "", pageNo: 1, pageSize: 10 }; this.searchNotice(); },
		addNotice() { this.$refs.add.dialogVisible = true; },
		updateNotice(id) {
			this.$refs.update.dialogVisible = true;
			this.$refs.update.id = id;
			this.$refs.update.getNoticeById();
		},
		viewNotice(notice) { this.currentNotice = notice; this.detailVisible = true; },
		deleteNotice(id) {
			this.$confirm('确定删除该公告吗？', '提示', {
				type: 'error',
				customClass: 'dark-message-box'
			}).then(() => {
				this.$http.get(`api/communityCtl/deleteNotice?id=` + id).then(() => {
					this.$message.success('公告已删除');
					this.searchNotice();
				});
			});
		},
		exportExcel() {
			if (!this.notices.length) return this.$message.warning('暂无可导出的数据');
			const rows = [['标题', '内容', '发布时间']];
			this.notices.forEach(n => rows.push([n.title, n.content, n.operTime]));
			exportRowsToExcel('社区公告列表', rows);
		},
		handleSizeChange(val) { this.form.pageSize = val; this.searchNotice(); },
		handleCurrentChange(val) { this.form.pageNo = val; this.searchNotice(); }
	},
	mounted() { this.searchNotice(); }
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
}

.glass-table {
	background: transparent !important;
}

.glass-table >>> tr { background-color: transparent !important; }

.glass-table >>> td {
	border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
	color: #cbd5e1;
	padding: 16px 0;
}

.notice-title-text { font-weight: 600; color: #f8fafc; }
.notice-body-text { color: rgba(203, 213, 225, 0.8); font-size: 13px; }

.time-cell {
	display: flex; align-items: center; justify-content: center; gap: 8px; color: #94a3b8; font-size: 13px;
}

.table-ops {
	display: flex; justify-content: center; gap: 10px;
}

.op-btn { font-weight: 600 !important; }
.op-btn.primary { color: #60a5fa !important; }
.op-btn.warning { color: #fbbf24 !important; }
.op-btn.danger { color: #f87171 !important; }

.pagination-container { padding: 24px; display: flex; justify-content: flex-end; }

.notice-detail-view {
	padding: 10px 5px;
}

.detail-title { margin: 0 0 16px; color: #f8fafc; font-size: 22px; font-weight: 700; }
.detail-meta { color: #94a3b8; font-size: 13px; margin-bottom: 24px; display: flex; align-items: center; gap: 8px; }
.detail-body {
	color: #cbd5e1;
	line-height: 1.8;
	font-size: 15px;
	white-space: pre-wrap;
	background: rgba(255,255,255,0.03);
	padding: 20px;
	border-radius: 12px;
	border: 1px solid rgba(255,255,255,0.06);
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>