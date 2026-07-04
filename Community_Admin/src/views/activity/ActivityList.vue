<template>
	<div class="app-page-container">
		<div class="page-header-actions">
			<div class="search-group">
				<el-input 
					placeholder="搜索活动标题" 
					v-model="form.title" 
					class="modern-input" 
					@keyup.enter.native="searchActivity">
				</el-input>
				<el-button type="primary" icon="el-icon-search" class="modern-btn search-btn" @click="searchActivity">查询</el-button>
				<el-button type="info" icon="el-icon-refresh" class="modern-btn ghost" @click="resetQuery">重置</el-button>
			</div>
			<div class="action-group">
				<el-button type="primary" icon="el-icon-plus" class="modern-btn highlight" @click="addActivity">发布新活动</el-button>
				<el-button type="success" icon="el-icon-download" class="modern-btn ghost" @click="exportExcel">导出 Excel</el-button>
			</div>
		</div>

		<el-card class="modern-card table-card" shadow="never">
			<el-table :data="activities" class="glass-table" :header-cell-style="headerStyle" border>
				<el-table-column type="index" label="序" width="60" align="center"></el-table-column>
				<el-table-column label="活动封面" width="120" align="center">
					<template slot-scope="scope">
						<div class="activity-cover-wrapper">
							<el-image 
								v-if="scope.row.img"
								:src="scope.row.img" 
								:preview-src-list="[scope.row.img]"
								fit="cover"
								class="activity-cover">
							</el-image>
							<div v-else class="cover-placeholder"><i class="el-icon-picture-outline"></i></div>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="title" label="活动标题" min-width="200" show-overflow-tooltip>
					<template slot-scope="scope">
						<span class="activity-title-text">{{ scope.row.title }}</span>
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
							<el-button size="mini" type="text" class="op-btn primary" icon="el-icon-view" @click="viewActivity(scope.row)">详情</el-button>
							<el-button size="mini" type="text" class="op-btn warning" icon="el-icon-edit" @click="updateActivity(scope.row.id)">编辑</el-button>
							<el-button size="mini" type="text" class="op-btn danger" icon="el-icon-delete" @click="deleteActivity(scope.row.id)">下架</el-button>
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
			title="社区活动详情" 
			:visible.sync="detailVisible" 
			width="700px"
			custom-class="modern-dark-dialog"
			:append-to-body="true">
			<div class="activity-detail-view" v-if="currentActivity">
				<div class="detail-header-panel">
					<el-image :src="currentActivity.img" fit="cover" class="detail-hero-img" v-if="currentActivity.img"></el-image>
					<div class="detail-hero-info">
						<h2>{{ currentActivity.title }}</h2>
						<p><i class="el-icon-time"></i> 发布于 {{ currentActivity.operTime }}</p>
					</div>
				</div>
				<div class="detail-body-content">
					<div class="content-label">活动详情内容</div>
					<div class="markdown-content-preview">
						<mavon-editor 
							v-model="currentActivity.content"
							:subfield="false"
							:defaultOpen="'preview'"
							:toolbarsFlag="false"
							:editable="false"
							boxShadow="none"
							class="transparent-editor">
						</mavon-editor>
					</div>
				</div>
			</div>
		</el-dialog>

		<Add ref="add" @refresh="searchActivity"></Add>
		<Update ref="update" @refresh="searchActivity"></Update>
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
			activities: [],
			total: 0,
			detailVisible: false,
			currentActivity: null,
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
		searchActivity() {
			this.$http.post("api/communityCtl/activityList", this.form).then(resp => {
				if (resp.data.code === 200) {
					this.activities = resp.data.data.list;
					this.total = resp.data.data.total;
				}
			});
		},
		resetQuery() {
			this.form = { title: "", pageNo: 1, pageSize: 10 };
			this.searchActivity();
		},
		addActivity() { this.$refs.add.dialogVisible = true; },
		updateActivity(id) {
			this.$refs.update.dialogVisible = true;
			this.$refs.update.id = id;
			this.$refs.update.getActivityById();
		},
		viewActivity(activity) {
			this.currentActivity = activity;
			this.detailVisible = true;
		},
		deleteActivity(id) {
			this.$confirm('此操作将永久删除该活动, 是否继续?', '安全警告', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'error',
				customClass: 'dark-message-box'
			}).then(() => {
				this.$http.get(`api/communityCtl/deleteActivity?id=` + id).then(() => {
					this.$message.success('活动已成功删除');
					this.searchActivity();
				});
			});
		},
		handleSizeChange(val) { this.form.pageSize = val; this.searchActivity(); },
		handleCurrentChange(val) { this.form.pageNo = val; this.searchActivity(); },
		exportExcel() {
			if (!this.activities.length) return this.$message.warning('暂无可导出的数据');
			const rows = [['活动标题', '发布时间', '内容']];
			this.activities.forEach(item => rows.push([item.title, item.operTime, item.content]));
			exportRowsToExcel('社区活动列表', rows);
		}
	},
	mounted() { this.searchActivity(); }
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

.activity-cover-wrapper {
	width: 80px;
	height: 50px;
	border-radius: 8px;
	overflow: hidden;
	margin: 0 auto;
	border: 1px solid rgba(255,255,255,0.1);
}

.activity-cover { width: 100%; height: 100%; }

.cover-placeholder {
	width: 100%; height: 100%;
	background: rgba(255,255,255,0.05);
	display: flex; align-items: center; justify-content: center;
	color: rgba(255,255,255,0.2); font-size: 20px;
}

.activity-title-text {
	font-weight: 600; color: #f8fafc;
}

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

.activity-detail-view {
	padding: 0;
}

.detail-header-panel {
	position: relative;
	height: 180px;
	border-radius: 16px;
	overflow: hidden;
	margin-bottom: 24px;
}

.detail-hero-img { width: 100%; height: 100%; }

.detail-hero-info {
	position: absolute; inset: 0;
	background: linear-gradient(to top, rgba(15,23,42,0.95), transparent 80%);
	display: flex; flex-direction: column; justify-content: flex-end;
	padding: 24px; color: white;
}

.detail-hero-info h2 { margin: 0 0 8px; font-size: 24px; }
.detail-hero-info p { margin: 0; opacity: 0.8; font-size: 14px; }

.detail-body-content { padding: 0 10px; }
.content-label { font-size: 13px; color: #64748b; margin-bottom: 12px; letter-spacing: 1px; text-transform: uppercase; }

.markdown-content-preview {
	background: rgba(15,23,42,0.4);
	border-radius: 12px;
	border: 1px solid rgba(255,255,255,0.06);
	overflow: hidden;
}

.transparent-editor {
	background-color: transparent !important;
	border: none !important;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>