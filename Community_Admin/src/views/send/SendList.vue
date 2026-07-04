<template>
	<div class="content">
	  <!-- 查询条件-->
	  	<el-row :gutter="20">
	  		<el-col :span="6">
	  			<el-input placeholder="用户名称" v-model="form.name"></el-input>
	  		</el-col>
			<el-col :span="6">
				<el-input placeholder="手机号" v-model="form.phone"></el-input>
			</el-col>
	  		<el-col :span="6">
				<el-button type="primary" icon="el-icon-search" @click="searchUser()">查询</el-button>
	  		</el-col>
	  	</el-row>
	  	<br>
	  <el-card class="box-card">
		<!-- 工具栏 -->
		<div class="toolbar">
			<div class="toolbar-right">
				<el-button type="success" icon="el-icon-download" size="small" @click="exportExcel()">导出Excel</el-button>
				<el-button type="warning" icon="el-icon-refresh" size="small" circle @click="searchUser()" title="刷新"></el-button>
			</div>
		</div>
		
	  <!-- 数据表格 -->
	  <el-table :data="users" border class="modern-table">
		  <!-- 设置列 -->
			  <el-table-column  prop="name"    		label="姓名"></el-table-column>
			  <el-table-column  prop="gender"    	label="性别" width="80"></el-table-column>
			  <el-table-column  prop="age"    		label="年龄" width="80"></el-table-column>
			  <el-table-column  prop="phone"    	label="手机号"></el-table-column>
			  <el-table-column  prop="address"    	label="地址"></el-table-column>
			  <el-table-column  label="社区" width="150">
				  <template slot-scope="scope">
					  <span>{{ scope.row.community ? scope.row.community.name : '-' }}</span>
				  </template>
			  </el-table-column>
			  <el-table-column fixed="right" label="操作" width="240px" align="center">
		        <template slot-scope="scope">
					<el-button size="mini" type="text" icon="el-icon-view" @click="viewDetail(scope.row.id)">详情</el-button>
					<el-button size="mini" type="text" icon="el-icon-key" @click="resetPassword(scope.row.id)">重置</el-button>
					<el-button size="mini" type="text" icon="el-icon-delete" @click="deleteUser(scope.row.id)">删除</el-button>
		        </template>
		      </el-table-column>
	    </el-table>
		<!-- 分页组件 -->
		<el-pagination
		      @size-change="handleSizeChange"
		      @current-change="handleCurrentChange"
		      :current-page="form.pageNo"
		      :page-sizes="[5, 10, 15, 20]"
		      :page-size="form.pageSize"
		      layout="total, sizes, prev, pager, next, jumper"
		      :total="total"
		      class="pagination"
		      background>
		</el-pagination>
	</el-card>
	<Detail ref="detail"></Detail>
	</div>
</template>

<script>
import Detail from "./Detail.vue"
import { exportRowsToExcel } from "../../utils/excel"
export default{
	components:{
		Detail
	},
	data(){
		return{
			form:{
				name:"",
				phone:"",
				pageNo:1,
				pageSize:5
			},
			users:[],
			total:0
		}
	},
	methods:{
		handleSizeChange(val){
			this.form.pageSize = val;
			this.form.pageNo = 1;
			this.searchUser();
		},
		handleCurrentChange(val){
			this.form.pageNo = val;
			this.searchUser();
		},
		updateUser(id){
			this.$refs.update.form.id = id;
			this.$refs.update.dialogVisible = true;
			this.$refs.update.findUserById(id);
		},
		viewDetail(id){
			this.$refs.detail.dialogVisible = true;
			this.$refs.detail.loadUserDetail(id);
		},
		resetPassword(id){
			this.$confirm('此操作将重置该用户密码, 是否继续?', '提示', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning'
			}).then(() => {
				this.$http.post("/api/userCtl/reset", "id="+id)
				.then((resp)=>{
					console.log(resp.data);
				});
				this.$message({
					type: 'success',
					message: '重置成功!',
					duration:1000
				});
			}).catch(() => {
				this.$message({
					type: 'info',
					message: '已取消重置',
					duration:1000
				});          
			});	
		},
		searchUser(){
			this.$http.post("/api/userCtl/sendList", this.form)
			.then((resp)=>{
				this.users = resp.data.data.list;
				this.total = resp.data.data.total;
				if(resp.data.data.size == 0){
					this.$message({message: '未查询到该用户!', type: 'warning', duration:1000});
				}
			});
		},
		exportExcel(){
			if(!this.users || this.users.length === 0){
				this.$message.warning('暂无可导出的配送员数据');
				return;
			}
			const rows = [
				['姓名', '性别', '年龄', '手机号', '地址', '社区']
			];
			this.users.forEach(item => {
				rows.push([
					item.name || '',
					item.gender || '',
					item.age || '',
					item.phone || '',
					item.address || '',
					item.community ? item.community.name : '-'
				]);
			});
			exportRowsToExcel('配送员列表', rows);
		},
		deleteUser(id){
			this.$confirm('此操作将永久删除该用户, 是否继续?', '提示', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning'
			}).then(() => {
				this.$http.get("/api/userCtl/deleteUser?id="+id)
				.then((resp)=>{
					console.log(resp.data);
					this.$message({
						type: 'success',
						message: '删除成功!',
						duration:1000
					});
					// 刷新列表
					this.searchUser();
				}).catch((error)=>{
					console.error('删除失败:', error);
					this.$message({
						type: 'error',
						message: '删除失败，请重试',
						duration:2000
					});
				});
			}).catch(() => {
				this.$message({
					type: 'info',
					message: '已取消删除',
					duration:1000
				});          
			});	
		}
	},
	mounted() {
		this.searchUser();
	}
}
</script>

<style scoped>
	.content{
		padding: 0;
	}
	
	.box-card {
		border-radius: 2px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.05);
	}
	
	/* 头部样式 - 若依风格 */
	.box-card >>> .el-card__header {
		padding: 14px 20px;
		background: #f4f4f5;
		border-bottom: 1px solid #e6ebf5;
	}
	
	.clearfix span {
		font-size: 14px;
		font-weight: 500;
		color: #606266;
	}
	
	/* 工具栏 - 若依风格 */
	.toolbar {
		display: flex;
		justify-content: flex-end;
		align-items: center;
		margin-bottom: 16px;
	}
	
	.toolbar-right {
		display: flex;
		gap: 8px;
	}
	
	.modern-table{
		width: 100%;
	}
	
	/* 表格样式 - 若依风格 */
	.modern-table >>> .el-table th {
		background: #f8f8f9 !important;
		color: #606266;
		font-weight: 500;
		font-size: 14px;
		padding: 12px 0;
	}
	
	.modern-table >>> .el-table td {
		padding: 12px 0;
		font-size: 14px;
	}
	
	/* 表格悬停效果 */
	.modern-table >>> .el-table__row:hover {
		background: transparent !important;
	}
	
	/* 操作按钮样式 - 若依风格 */
	.modern-table >>> .el-button--text {
		padding: 0 8px;
		font-size: 14px;
	}
	
	.modern-table >>> .el-button--text:nth-child(1) {
		color: #409eff;
	}
	
	.modern-table >>> .el-button--text:nth-child(2) {
		color: #e6a23c;
	}
	
	.modern-table >>> .el-button--text:nth-child(3) {
		color: #f56c6c;
	}
	
	.modern-table >>> .el-button--text:hover {
		opacity: 1;
	}
	
	/* 分页样式 - 若依风格 */
	.pagination {
		margin-top: 20px;
		text-align: right;
	}
</style>

		padding: 12px 0;
		font-size: 14px;
	}
	
	/* 表格悬停效果 */
	.modern-table >>> .el-table__row:hover {
		background: transparent !important;
	}
	
	/* 操作按钮样式 - 若依风格 */
	.modern-table >>> .el-button--text {
		padding: 0 8px;
		font-size: 14px;
	}
	
	.modern-table >>> .el-button--text:nth-child(1) {
		color: #409eff;
	}
	
	.modern-table >>> .el-button--text:nth-child(2) {
		color: #e6a23c;
	}
	
	.modern-table >>> .el-button--text:nth-child(3) {
		color: #f56c6c;
	}
	
	.modern-table >>> .el-button--text:hover {
		opacity: 1;
	}
	
	/* 分页样式 - 若依风格 */
	.pagination {
		margin-top: 20px;
		text-align: right;
	}
</style>

		border-radius: 8px;
		box-shadow: 0 1px 3px rgba(0,0,0,0.05);
		border: 1px solid #f0f0f0;
		background: #ffffff;
	}
	.add-btn{
		float: right;
		margin-left: auto;
		min-width: 90px;
	}
	.modern-table{
		width: 100% !important;
		border-radius: 6px !important;
		overflow: hidden !important;
	}
	.btn-outline-primary{
		background: transparent !important;
		border: 1px solid #409eff !important;
		color: #409eff !important;
	}
	.btn-outline-primary:hover{
		background: #ecf5ff !important;
		border: 1px solid #409eff !important;
		color: #409eff !important;
	}
	.btn-outline-warning{
		background: transparent !important;
		border: 1px solid #e6a23c !important;
		color: #e6a23c !important;
	}
	.btn-outline-warning:hover{
		background: #fdf6ec !important;
		border: 1px solid #e6a23c !important;
		color: #e6a23c !important;
	}
	.btn-outline-danger{
		background: transparent !important;
		border: 1px solid #f56c6c !important;
		color: #f56c6c !important;
	}
	.btn-outline-danger:hover{
		background: #fef0f0 !important;
		border: 1px solid #f56c6c !important;
		color: #f56c6c !important;
	}
</style>
