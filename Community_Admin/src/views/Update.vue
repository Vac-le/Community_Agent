<template>
	<div>
		<el-dialog title="修改密码":visible.sync="dialogVisible" width="40%">
		  <el-form ref="form" label-width="80px" style="width: 400px;">
				<!-- 学号输入框 -->
				<el-form-item label="账号:">
				  <el-input :disabled="true" v-model="form.account" ></el-input>
				</el-form-item>
				<!-- 姓名输入框 -->
				<el-form-item label="旧密码:">
				  <el-input v-model="form.oldPassword"></el-input>
				</el-form-item>
				<!-- 卡号输入框 -->
				<el-form-item label="新密码:">
				  <el-input v-model="form.newPassword1"></el-input>
				</el-form-item>
				<el-form-item label="确认密码:">
				  <el-input v-model="form.newPassword2"></el-input>
				</el-form-item>
		  </el-form>
		  <span slot="footer" class="dialog-footer">
		    <el-button type="warning" @click="dialogVisible = false">取 消</el-button>
		    <el-button type="primary" @click="updatePassword()">修改</el-button>
		  </span>
		</el-dialog>
	</div>
</template>

<script>
export default{
	data(){
		return{
			dialogVisible:false,
			form:{
				account:"",
				oldPassword:"",
				newPassword1:"",
				newPassword2:"",
			},
		}
	},
	methods:{
			updatePassword(){
				this.$http.post("/api/loginCtl/updatePassword",jsonToString(this.form)).then((resp)=>{
						console.log(resp.data);
						if(this.form.newPassword1.length==0||this.form.newPassword2.length==0){
							this.$message({message: '密码不能为空',type: 'warning',duration:1000});//出现时间
							return;
						}
						if(resp.data.code == 0){
							this.$message({message: '密码错误,请重新输入',type: 'warning',duration:1000});//出现时间
							return;
						}
						if(resp.data.code == 1){
							this.$message({message: '密码输入不一致,请重新输入',type: 'warning',duration:1000});//出现时间
							return;
						}
						if(resp.data.code == 2){
							this.$message({message: '新密码与旧密码一致,请重新输入',type: 'warning',duration:1000});//出现时间
							return;
						}
						this.$message({message: '修改成功,请重新登录',type: 'success',duration:1000,onClose:()=>{
							//关闭窗口
							this.dialogVisible = false;
							//清除浏览器中存储的用户信息
							sessionStorage.clear();//clear清除所有
							//跳转到注册页面
							this.$router.push("/login");
						}});
				})
			},
	},
	mounted() {
		//查询当前登录信息
		this.form.account = sessionStorage.getItem("account");
	}
}
 function jsonToString(form){
    let str = "";
    for(let s in form){
 		str+=s+"="+form[s]+"&";	  
    } 
    return str.substring(0,str.length-1);
 }
</script>

<style scoped>
/* 简约风格 */
.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>
</style>
.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>


.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>
</style>
.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}
</style>.el-form {
	margin: 0 auto;
}

.el-form-item {
	margin-bottom: 18px;
}

.el-form-item__label {
	font-weight: 500;
	color: #606266;
	font-size: 14px;
}

<style>

