<template>
	<div class="app-page-container">
		<div class="page-header-actions">
			<div class="search-group">
				<el-input 
					placeholder="订单编号" 
					v-model="form.id" 
					class="modern-input">
				</el-input>
				<el-select v-model="form.orderStatus" placeholder="订单状态" class="modern-input" clearable>
					<el-option label="全部状态" :value="-1"></el-option>
					<el-option label="待接单" :value="0"></el-option>
					<el-option label="进行中" :value="1"></el-option>
					<el-option label="已完成" :value="2"></el-option>
				</el-select>
				<el-button type="primary" icon="el-icon-search" class="modern-btn search-btn" @click="searchOrders">查询</el-button>
			</div>
			<div class="action-group">
				<el-button type="success" icon="el-icon-download" class="modern-btn ghost" @click="exportExcel">导出数据</el-button>
				<el-button type="primary" icon="el-icon-refresh" class="modern-btn circle-btn" circle @click="searchOrders"></el-button>
			</div>
		</div>

		<el-card class="modern-card table-card" shadow="never">
			<el-table :data="orders" class="glass-table" :header-cell-style="headerStyle" border>
				<el-table-column prop="id" label="单号" width="85" align="center"></el-table-column>
				<el-table-column label="下单用户" width="120">
					<template slot-scope="scope">
						<div class="user-info-cell">
							<i class="el-icon-user"></i>
							<span>{{ scope.row.user ? scope.row.user.name : '-' }}</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="deliveryAddress" label="服务地址" min-width="220" show-overflow-tooltip></el-table-column>
				<el-table-column prop="deliveryPhone" label="联系方式" width="130" align="center"></el-table-column>
				<el-table-column prop="amount" label="金额" width="100" align="center">
					<template slot-scope="scope">
						<span class="price-text">¥{{ scope.row.amount }}</span>
					</template>
				</el-table-column>
				<el-table-column label="状态" width="100" align="center">
					<template slot-scope="scope">
						<el-tag :type="statusType(scope.row.orderStatus)" size="mini" effect="dark" class="status-tag">
							{{ statusLabel(scope.row.orderStatus) }}
						</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="startTime" label="下单时间" width="180" align="center">
					<template slot-scope="scope">
						<div class="time-cell">
							<i class="el-icon-time"></i>
							<span>{{ formatTime(scope.row.startTime) }}</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="orderDate" label="预约日期" width="140" align="center">
					<template slot-scope="scope">
						<span class="date-text">{{ formatDate(scope.row.orderDate) }}</span>
					</template>
				</el-table-column>
				<el-table-column label="操作" width="120" align="center" fixed="right">
					<template slot-scope="scope">
						<el-button size="mini" type="text" class="op-btn primary" icon="el-icon-view" @click="viewDetail(scope.row.id)">详情</el-button>
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
		
		<Detail ref="detail"></Detail>
	</div>
</template>

<script>
import Detail from "./Detail.vue"

export default {
	components: { Detail },
	data() {
		return {
			form: { id: "", orderStatus: -1, pageNo: 1, pageSize: 10 },
			orders: [],
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
		formatTime(time) {
			if (!time) return '-';
			const date = new Date(time);
			const pad = (n) => String(n).padStart(2, '0');
			return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
		},
		formatDate(time) {
			if (!time) return '-';
			const date = new Date(time);
			const pad = (n) => String(n).padStart(2, '0');
			return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}`;
		},
		statusType(s) {
			if (s === 0) return 'info';
			if (s === 1) return 'warning';
			if (s === 2) return 'success';
			return '';
		},
		statusLabel(s) {
			if (s === 0) return '待接单';
			if (s === 1) return '已接单';
			if (s === 2) return '已完成';
			return '未知';
		},
		searchOrders() {
			this.$http.post("/api/orderCtl/homeList", this.form).then(resp => {
				if (resp.data.code === 200) {
					this.orders = resp.data.data.list;
					this.total = resp.data.data.total;
				}
			});
		},
		exportExcel() {
			if (!this.orders.length) return this.$message.warning('暂无可导出的数据');
			const rows = [['单号', '用户', '地址', '金额', '状态', '下单时间', '预约日期']];
			this.orders.forEach(o => rows.push([
				o.id, o.user ? o.user.name : '-', o.deliveryAddress, o.amount, this.statusLabel(o.orderStatus), this.formatTime(o.startTime), this.formatDate(o.orderDate)
			]));
			this.downloadExcel('家政订单', rows);
		},
		downloadExcel(name, rows) {
			let table = '<table border="1"><tr>' + rows[0].map(h => `<th>${h}</th>`).join('') + '</tr>';
			rows.slice(1).forEach(r => table += '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>');
			table += '</table>';
			const blob = new Blob(['\ufeff' + table], { type: 'application/vnd.ms-excel' });
			const link = document.createElement('a');
			link.href = URL.createObjectURL(blob);
			link.download = name + '.xls';
			link.click();
		},
		handleSizeChange(val) { this.form.pageSize = val; this.searchOrders(); },
		handleCurrentChange(val) { this.form.pageNo = val; this.searchOrders(); },
		viewDetail(id) { this.$refs.detail.dialogVisible = true; this.$refs.detail.loadOrderDetail(id); }
	},
	mounted() { this.searchOrders(); }
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
	padding: 16px 0;
}

.user-info-cell {
	display: flex; align-items: center; gap: 8px; color: #f8fafc;
}

.price-text { color: #f87171; font-weight: 700; }
.date-text { color: #38bdf8; font-size: 13px; }

.time-cell {
	display: flex; align-items: center; justify-content: center; gap: 8px; color: #94a3b8; font-size: 13px;
}

.op-btn { font-weight: 600 !important; }
.op-btn.primary { color: #60a5fa !important; }

.pagination-container { padding: 24px; display: flex; justify-content: flex-end; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>