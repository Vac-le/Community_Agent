<template>
  <div>
    <el-dialog
      title="添加家政服务"
      :visible.sync="dialogVisible"
      width="600px"
      class="modern-dialog fixed-dialog"
      :modal="false"
    >
      <el-form
        ref="form"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="modern-form"
      >
        <!-- 服务名称 -->
        <el-form-item label="服务名称:" prop="name" class="field-full">
          <el-input v-model="form.name" placeholder="请输入服务名称"></el-input>
        </el-form-item>

        <!-- 服务类型 -->
        <el-form-item label="服务类型:" prop="homeTypeId" class="field-full">
          <el-select
            v-model="form.homeTypeId"
            placeholder="请选择服务类型"
            style="width: 100%"
          >
            <el-option
              v-for="type in homeTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            ></el-option>
          </el-select>
        </el-form-item>

        <!-- 服务价格 -->
        <el-form-item label="服务价格:" prop="price" class="field-full">
          <el-input-number
            v-model="form.price"
            :min="0"
            :precision="0"
            :step="1"
            placeholder="请输入服务价格（整数）"
            style="width: 100%"
          ></el-input-number>
        </el-form-item>

        <!-- 服务描述 -->
        <el-form-item label="服务描述:" prop="description" class="field-full">
          <el-input
            type="textarea"
            v-model="form.description"
            :rows="4"
            placeholder="请输入服务描述"
            maxlength="200"
           
          ></el-input>
        </el-form-item>

        <!-- 服务图片 -->
        <el-form-item label="服务图片:" class="field-full">
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
            :headers="uploadHeaders"
          >
            <img v-if="imageUrl" :src="imageUrl" class="avatar" />
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
          <div class="upload-tip">支持 jpg、png 格式，大小不超过 2MB</div>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer modern-dialog-footer">
        <el-button type="warning" @click="dialogVisible = false" class="btn-cancel">取 消</el-button>
        <el-button type="primary" @click="addHome" class="btn-submit">保 存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      dialogVisible: false,
      form: {
        name: "",
        homeTypeId: "",
        price: 0,
        description: "",
        img: ""
      },
      homeTypes: [],
      imageUrl: "",
      uploadUrl: this.$http.defaults.baseURL + "api/productCtl/uploadImg",
      uploadHeaders: {
        token: sessionStorage.getItem("token")
      },
      rules: {
        name: [
          { required: true, message: "请输入服务名称", trigger: "blur" },
          { min: 2, max: 50, message: "长度在 2 到 50 个字符", trigger: "blur" }
        ],
        homeTypeId: [
          { required: true, message: "请选择服务类型", trigger: "change" }
        ],
        price: [
          { required: true, message: "请输入服务价格", trigger: "blur" }
        ]
      }
    };
  },
  methods: {
    // 加载家政服务类型列表
    loadHomeTypes() {
      this.$http.get("/api/productCtl/homeTypeList").then(resp => {
        if (resp.data.code === 200) {
          this.homeTypes = resp.data.data;
        }
      });
    },

    // 上传前验证
    beforeUpload(file) {
      const isImage = file.type === "image/jpeg" || file.type === "image/png";
      const isLt2M = file.size / 1024 / 1024 < 2;

      if (!isImage) {
        this.$message.error("只能上传 JPG/PNG 格式的图片!");
      }
      if (!isLt2M) {
        this.$message.error("上传图片大小不能超过 2MB!");
      }
      return isImage && isLt2M;
    },

    // 上传成功回调
    handleUploadSuccess(response) {
      if (response.code === 200) {
        this.imageUrl = response.data;
        this.form.img = response.data;
        this.$message.success("图片上传成功");
      } else {
        this.$message.error("图片上传失败: " + response.msg);
      }
    },

    // 添加家政服务
    addHome() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.$http
            .post("/api/productCtl/addHome", this.form)
            .then(resp => {
              if (resp.data.code === 200) {
                this.$message({
                  message: "添加成功",
                  type: "success",
                  duration: 1000,
                  onClose: () => {
                    this.dialogVisible = false;
                    this.resetForm();
                    this.$emit("refresh");
                  }
                });
              } else {
                this.$message({
                  type: "error",
                  message: resp.data.msg || "添加失败",
                  duration: 2000
                });
              }
            })
            .catch(() => {
              this.$message({
                type: "error",
                message: "添加家政服务失败，请重试",
                duration: 2000
              });
            });
        } else {
          this.$message.error("请填写完整信息");
        }
      });
    },

    // 重置表单
    resetForm() {
      this.form = {
        name: "",
        homeTypeId: "",
        price: 0,
        description: "",
        img: ""
      };
      this.imageUrl = "";
      if (this.$refs.form) {
        this.$refs.form.resetFields();
      }
    }
  },
  watch: {
    dialogVisible(val) {
      if (!val) {
        this.resetForm();
      }
    }
  }
};
</script>

<style scoped>
.modern-form {
  padding: 10px 10px;
}

.modern-form .el-form-item {
  margin-bottom: 16px;
}

.modern-form .el-form-item__label {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.field-full {
  width: 100%;
}

.modern-dialog .el-select {
  width: 100%;
}

.fixed-dialog >>> .el-dialog {
  margin: 5vh auto !important;
  position: relative;
  top: auto;
  left: auto;
  transform: none !important;
}

.fixed-dialog >>> .el-dialog__wrapper {
  overflow: auto !important;
}

.fixed-dialog >>> .el-dialog__body {
  padding: 15px 20px;
  overflow: visible;
  max-height: none;
}

.avatar-uploader >>> .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.avatar-uploader >>> .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 24px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
}

.avatar {
  width: 120px;
  height: 120px;
  display: block;
  object-fit: cover;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.5;
}

.modern-dialog-footer {
  text-align: right;
  padding-top: 10px;
}

.btn-cancel {
  background: #e6a23c;
  border-color: #e6a23c;
  color: #ffffff;
}

.btn-cancel:hover {
  background: #ebb563;
  border-color: #ebb563;
  color: #ffffff;
}

.btn-submit {
  background: #409eff;
  border-color: #409eff;
  color: #ffffff;
}

.btn-submit:hover {
  background: #66b1ff;
  border-color: #66b1ff;
}

.fixed-dialog >>> .el-dialog__body::-webkit-scrollbar {
  width: 6px;
}

.fixed-dialog >>> .el-dialog__body::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.fixed-dialog >>> .el-dialog__body::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.fixed-dialog >>> .el-dialog__body::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>

