<template>
	<el-dialog
		title="添加管理员"
		:visible.sync="dialogVisible"
		width="520px"
		:close-on-click-modal="false"
		:append-to-body="true"
		class="admin-dialog"
	>
		<el-form ref="formRef" :model="form" label-width="90px" class="admin-form">
			<el-form-item label="账户" prop="account">
				<el-input v-model.trim="form.account" placeholder="请输入账号"></el-input>
			</el-form-item>

			<el-form-item label="电话" prop="phone">
				<el-input v-model.trim="form.phone" placeholder="请输入联系电话"></el-input>
			</el-form-item>

			<el-form-item label="性别">
				<el-radio-group v-model="form.gender">
					<el-radio label="男">男</el-radio>
					<el-radio label="女">女</el-radio>
				</el-radio-group>
			</el-form-item>

			<el-form-item label="权限菜单">
				<div class="menu-tree">
					<div
						class="menu-group"
						v-for="parent in parentMenus"
						:key="parent.id"
					>
						<div class="parent-item">
							<el-checkbox
								:label="parent.id"
								v-model="parentChecked[parent.id]"
								:indeterminate="isIndeterminate(parent)"
								@change="onParentChange(parent)"
							>
								<i :class="getMenuIcon(parent.name)"></i>
								<span>{{ parent.name }}</span>
							</el-checkbox>
						</div>

						<div v-if="parent.children && parent.children.length" class="child-items">
							<el-checkbox-group
								v-model="form.menuids"
								@change="() => updateParentCheckedStatus(parent)"
							>
								<el-checkbox
									v-for="child in parent.children"
									:key="child.id"
									:label="child.id"
								>
									<i :class="getMenuIcon(child.name)"></i>
									<span>{{ child.name }}</span>
								</el-checkbox>
							</el-checkbox-group>
						</div>
					</div>
				</div>
			</el-form-item>
		</el-form>

		<span slot="footer" class="dialog-footer">
			<el-button type="warning" @click="dialogVisible = false">取 消</el-button>
			<el-button type="primary" @click="handleSubmit">保 存</el-button>
		</span>
	</el-dialog>
</template>

<script>
export default {
	data() {
		return {
			dialogVisible: false,
			form: {
				account: '',
				gender: '男',
				phone: '',
				menuids: []
			},
			menus: [],
			parentMenus: [],
			parentChecked: {}
		};
	},
	watch: {
		dialogVisible(val) {
			if (val) {
				this.resetForm();
				if (!this.menus.length) {
					this.loadMenus();
				} else {
					this.parentMenus = this.buildMenuTree(this.menus);
					this.initParentChecked();
				}
			}
		}
	},
	methods: {
		resetForm() {
			this.form = {
				account: '',
				gender: '男',
				phone: '',
				menuids: []
			};
			this.parentChecked = {};
		},
		loadMenus() {
			this.$http.get('api/menuCtl/searchMenu').then((resp) => {
				if (resp.data && resp.data.data) {
					this.menus = resp.data.data;
					this.parentMenus = this.buildMenuTree(this.menus);
					this.initParentChecked();
				}
			});
		},
		initParentChecked() {
			const checked = {};
			this.parentMenus.forEach((parent) => {
				checked[parent.id] = false;
			});
			this.parentChecked = checked;
		},
		buildMenuTree(menus) {
			const parents = menus.filter((menu) => !menu.parentId || menu.parentId === 0);
			parents.forEach((parent) => {
				parent.children = menus.filter((menu) => menu.parentId === parent.id);
			});
			return parents;
		},
		getMenuIcon(name) {
			const iconMap = {
				管理员管理: 'el-icon-user-solid',
				社区数据: 'el-icon-data-analysis',
				社区信息管理: 'el-icon-office-building',
				用户管理: 'el-icon-user',
				配送员管理: 'el-icon-s-custom',
				社区天气: 'el-icon-partly-cloudy',
				家政订单管理: 'el-icon-s-order',
				代购订单管理: 'el-icon-shopping-cart-2',
				餐饮订单管理: 'el-icon-food',
				家政商品管理: 'el-icon-s-goods',
				代购商品管理: 'el-icon-goods',
				餐饮商品管理: 'el-icon-dish'
			};
			return iconMap[name] || 'el-icon-menu';
		},
		onParentChange(parent) {
			const checked = this.parentChecked[parent.id];
			if (parent.children && parent.children.length) {
				parent.children.forEach((child) => {
					const idx = this.form.menuids.indexOf(child.id);
					if (checked && idx === -1) {
						this.form.menuids.push(child.id);
					} else if (!checked && idx !== -1) {
						this.form.menuids.splice(idx, 1);
					}
				});
			}
			if (checked && !this.form.menuids.includes(parent.id)) {
				this.form.menuids.push(parent.id);
			} else if (!checked) {
				const index = this.form.menuids.indexOf(parent.id);
				if (index !== -1) this.form.menuids.splice(index, 1);
			}
		},
		updateParentCheckedStatus(parent) {
			if (!parent.children || !parent.children.length) return;
			const selectedChildren = parent.children.filter((child) =>
				this.form.menuids.includes(child.id)
			);
			this.$set(
				this.parentChecked,
				parent.id,
				selectedChildren.length === parent.children.length
			);
			if (selectedChildren.length && !this.form.menuids.includes(parent.id)) {
				this.form.menuids.push(parent.id);
			}
			if (!selectedChildren.length) {
				const index = this.form.menuids.indexOf(parent.id);
				if (index !== -1) this.form.menuids.splice(index, 1);
			}
		},
		isIndeterminate(parent) {
			if (!parent.children || !parent.children.length) return false;
			const selectedChildren = parent.children.filter((child) =>
				this.form.menuids.includes(child.id)
			);
			return (
				selectedChildren.length > 0 &&
				selectedChildren.length < parent.children.length
			);
		},
		handleSubmit() {
			const allMenuIds = new Set(this.form.menuids);
			Object.keys(this.parentChecked).forEach((key) => {
				if (this.parentChecked[key]) {
					allMenuIds.add(Number(key));
				}
			});
			const payload = {
				...this.form,
				menuids: Array.from(allMenuIds)
			};
			this.$http.post('api/adminCtl/addAdmin', payload).then(() => {
				this.$message({
					message: '保存成功',
					type: 'success',
					duration: 1000,
					onClose: () => {
						this.dialogVisible = false;
						this.$emit('refresh');
					}
				});
			});
		}
	}
};
</script>

<style scoped>
.admin-dialog >>> .el-dialog__body {
	padding: 20px;
}

.admin-form .el-form-item {
	margin-bottom: 18px;
}

.menu-tree {
	max-height: 240px;
	overflow-y: auto;
	padding: 8px 12px;
	background: transparent;
	border: 1px solid #ebeef5;
	border-radius: 4px;
}

.menu-group + .menu-group {
	margin-top: 12px;
}

.parent-item {
	font-weight: 600;
	margin-bottom: 6px;
}

.child-items {
	padding-left: 24px;
}

.child-items .el-checkbox {
	display: inline-flex;
	align-items: center;
	margin-right: 16px;
	margin-bottom: 8px;
}

.menu-tree i {
	margin-right: 6px;
	color: #409eff;
}

.dialog-footer {
	text-align: right;
}

.dialog-footer .el-button {
	min-width: 90px;
}
</style>

