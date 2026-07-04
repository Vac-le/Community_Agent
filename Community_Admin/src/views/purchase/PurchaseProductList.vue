<template>
	<div class="app-page-container">
		<div class="page-header-actions">
			<div class="search-group">
				<el-input 
					placeholder="商品名称" 
					v-model="form.name" 
					class="modern-input">
				</el-input>
				<el-select v-model="form.purchaseTypeId" placeholder="全部类型" class="modern-input" clearable>
					<el-option 
						v-for="type in purchasesTypes" 
						:key="type.id" 
						:label="type.name" 
						:value="type.id">
					</el-option>
				</el-select>
				<el-button type="primary" icon="el-icon-search" class="modern-btn search-btn" @click="searchPurchase">查询</el-button>
			</div>
			<div class="action-group">
				<el-button type="primary" icon="el-icon-plus" class="modern-btn highlight" @click="addPurchase">上架代购品</el-button>
				<el-button type="success" icon="el-icon-download" class="modern-btn ghost" @click="exportExcel">导出 Excel</el-button>
			</div>
		</div>

		<el-card class="modern-card table-card" shadow="never">
			<el-table :data="purchases" class="glass-table" :header-cell-style="headerStyle" border>
				<el-table-column type="index" label="序" width="60" align="center"></el-table-column>
				<el-table-column label="商品图" width="120" align="center">
					<template slot-scope="scope">
						<div class="food-img-wrapper">
							<el-image 
								v-if="scope.row.img"
								:src="scope.row.img" 
								:preview-src-list="[scope.row.img]"
								fit="cover"
								class="food-img">
							</el-image>
							<div v-else class="img-placeholder"><i class="el-icon-shopping-bag-2"></i></div>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="name" label="商品名称" min-width="160">
					<template slot-scope="scope">
						<span class="food-name-text">{{ scope.row.name }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip></el-table-column>
				<el-table-column label="类型" width="120" align="center">
					<template slot-scope="scope">
						<el-tag size="mini" effect="plain" class="type-tag">
							{{ scope.row.purchasesType ? scope.row.purchasesType.name : '未分类' }}
						</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="price" label="单价" width="120" align="center">
					<template slot-scope="scope">
						<span class="price-text">¥{{ scope.row.price }}</span>
					</template>
				</el-table-column>
				<el-table-column label="操作" width="200" align="center" fixed="right">
					<template slot-scope="scope">
						<div class="table-ops">
							<el-button size="mini" type="text" class="op-btn highlight" icon="el-icon-edit" @click="updatePurchase(scope.row.id)">修改</el-button>
							<el-button size="mini" type="text" class="op-btn danger" icon="el-icon-delete" @click="deletePurchase(scope.row.id)">下架</el-button>
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

		<Add ref="add" @refresh="searchPurchase"></Add>
		<Update ref="update" @refresh="searchPurchase"></Update>
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
			form: { name: "", purchaseTypeId: null, pageNo: 1, pageSize: 10 },
			purchases: [],
			purchasesTypes: [],
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
		loadPurchasesTypes() {
			this.$http.get("/api/productCtl/purchaseTypeList").then(resp => {
				if (resp.data.code === 200) this.purchasesTypes = resp.data.data;
			});
		},
		searchPurchase() {
			this.$http.post("/api/productCtl/purchaseList", this.form).then(resp => {
				if (resp.data.code === 200) {
					this.purchases = resp.data.data.list;
					this.total = resp.data.data.total;
				}
			});
		},
		resetQuery() { this.form = { name: "", purchaseTypeId: null, pageNo: 1, pageSize: 10 }; this.searchPurchase(); },
		addPurchase() { this.$refs.add.dialogVisible = true; this.$refs.add.loadPurchasesTypes(); },
		updatePurchase(id) {
			this.$refs.update.dialogVisible = true;
			this.$refs.update.findPurchaseById(id);
			this.$refs.update.loadPurchasesTypes();
		},
		deletePurchase(id) {
			this.$confirm('确定下架该代购商品吗？', '提示', {
				type: 'error',
				customClass: 'dark-message-box'
			}).then(() => {
				this.$http.post("/api/productCtl/deletePurchase", { id }).then(() => {
					this.$message.success('商品已下架');
					this.searchPurchase();
				});
			});
		},
		exportExcel() {
			if (!this.purchases.length) return this.$message.warning('暂无可导出的数据');
			const rows = [['商品名称', '价格', '描述', '类型']];
			this.purchases.forEach(f => rows.push([f.name, f.price, f.description, f.purchasesType ? f.purchasesType.name : '-']));
			exportRowsToExcel('代购商品列表', rows);
		},
		handleSizeChange(val) { this.form.pageSize = val; this.searchPurchase(); },
		handleCurrentChange(val) { this.form.pageNo = val; this.searchPurchase(); }
	},
	mounted() {
		this.searchPurchase();
		this.loadPurchasesTypes();
	}
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
	padding: 16px 0;
}

.food-img-wrapper {
	width: 60px; height: 60px; border-radius: 10px; overflow: hidden; margin: 0 auto; border: 1px solid rgba(255,255,255,0.1);
}

.food-img { width: 100%; height: 100%; }

.img-placeholder {
	width: 100%; height: 100%; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.2); font-size: 24px;
}

.food-name-text { font-weight: 600; color: #f8fafc; }
.price-text { color: #f87171; font-weight: 700; }

.type-tag {
	background: rgba(59, 130, 246, 0.1) !important;
	border-color: rgba(59, 130, 246, 0.2) !important;
	color: #60a5fa !important;
}

.table-ops {
	display: flex; justify-content: center; gap: 10px;
}

.op-btn { font-weight: 600 !important; }
.op-btn.highlight { color: #38bdf8 !important; }
.op-btn.danger { color: #f87171 !important; }

.pagination-container { padding: 24px; display: flex; justify-content: flex-end; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>