<template>
  <el-dialog 
    title="订单详情" 
    :visible.sync="dialogVisible" 
    width="900px"
    :close-on-click-modal="false"
    :lock-scroll="true"
    :append-to-body="true"
    class="order-detail-dialog">
    
    <div v-if="loading" style="text-align: center; padding: 40px;">
      <i class="el-icon-loading" style="font-size: 32px; color: #409eff;"></i>
      <p style="margin-top: 16px; color: #909399;">加载中...</p>
    </div>

    <div v-else class="detail-container">
      <!-- 订单基本信息 -->
      <div class="info-card">
        <div class="card-header">
          <i class="el-icon-document"></i>
          <span>订单信息</span>
        </div>
        <div class="card-body">
          <el-row :gutter="20">
            <el-col :span="12">
          <div class="info-row">
            <span class="label">订单编号：</span>
            <span class="value">{{ orderInfo.id }}</span>
          </div>
            </el-col>
            <el-col :span="12">
          <div class="info-row">
            <span class="label">订单状态：</span>
            <el-tag v-if="orderInfo.orderStatus === 0" type="info" size="small">未接单</el-tag>
            <el-tag v-else-if="orderInfo.orderStatus === 1" type="warning" size="small">已接单</el-tag>
            <el-tag v-else-if="orderInfo.orderStatus === 2" type="success" size="small">已送达</el-tag>
          </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
          <div class="info-row">
            <span class="label">订单金额：</span>
            <span class="value price">¥{{ orderInfo.amount }}</span>
          </div>
            </el-col>
            <el-col :span="12">
          <div class="info-row">
            <span class="label">下单时间：</span>
            <span class="value">{{ formatTime(orderInfo.startTime) }}</span>
          </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
          <div class="info-row">
            <span class="label">配送地址：</span>
            <span class="value">{{ orderInfo.deliveryAddress || '-' }}</span>
          </div>
            </el-col>
            <el-col :span="12">
          <div class="info-row">
            <span class="label">联系电话：</span>
            <span class="value">{{ orderInfo.deliveryPhone || '-' }}</span>
          </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" v-if="orderInfo.remark">
            <el-col :span="24">
              <div class="info-row">
            <span class="label">备注信息：</span>
            <span class="value">{{ orderInfo.remark }}</span>
          </div>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 用户信息和配送员信息 -->
      <el-row :gutter="16">
      <!-- 用户信息 -->
        <el-col :span="12">
      <div class="info-card">
        <div class="card-header">
          <i class="el-icon-user"></i>
          <span>下单用户</span>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">用户姓名：</span>
            <span class="value">{{ orderInfo.user ? orderInfo.user.name : '-' }}</span>
          </div>
        </div>
      </div>
        </el-col>

      <!-- 配送员信息 -->
        <el-col :span="12">
      <div class="info-card" v-if="orderInfo.send && orderInfo.orderStatus >= 1">
        <div class="card-header">
          <i class="el-icon-truck"></i>
          <span>配送员信息</span>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">配送员：</span>
            <span class="value">{{ orderInfo.send.name || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">联系电话：</span>
            <span class="value">{{ orderInfo.send.phone || '-' }}</span>
          </div>
        </div>
      </div>
          <div class="info-card" v-else>
            <div class="card-header">
              <i class="el-icon-truck"></i>
              <span>配送员信息</span>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="value" style="color: #909399;">暂无配送员</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 商品列表 -->
      <div class="info-card">
        <div class="card-header">
          <i class="el-icon-shopping-cart-2"></i>
          <span>商品清单</span>
        </div>
        <div class="card-body" style="padding: 0;">
          <el-table :data="orderInfo.purchasesItems" border size="medium" style="width: 100%">
            <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
            <el-table-column prop="name" label="商品名称" min-width="200"></el-table-column>
            <el-table-column prop="price" label="单价" width="120" align="right">
              <template slot-scope="scope">
                <span style="color: #606266;">¥{{ scope.row.price.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100" align="center">
              <template slot-scope="scope">
                <el-tag type="primary" size="small">{{ scope.row.quantity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="小计" width="120" align="right">
              <template slot-scope="scope">
                <span style="color: #f56c6c; font-weight: 600; font-size: 15px;">¥{{ (scope.row.price * scope.row.quantity).toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 总计 -->
          <div class="total-row">
            <span class="total-label">订单总计：</span>
            <span class="total-value">¥{{ orderInfo.amount }}</span>
          </div>
        </div>
      </div>
    </div>

    <span slot="footer" class="dialog-footer">
      <el-button type="primary" @click="dialogVisible = false" size="medium">关 闭</el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialogVisible: false,
      loading: false,
      orderInfo: {
        id: '',
        startTime: '',
        amount: 0,
        deliveryAddress: '',
        deliveryPhone: '',
        remark: '',
        orderStatus: 0,
        user: {
          id: '',
          name: ''
        },
        send: {
          id: '',
          name: '',
          phone: ''
        },
        purchasesItems: []
      }
    };
  },
  methods: {
    // 格式化时间
    formatTime(time) {
      if (!time) return '-';
      const date = new Date(time);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
    },
    // 加载订单详情
    loadOrderDetail(id) {
      this.loading = true;
      this.$http.get("/api/orderCtl/findOrderById?id=" + id)
        .then((resp) => {
          this.loading = false;
          console.log('订单详情响应:', resp.data);
          if (resp.data && resp.data.data) {
            this.orderInfo = resp.data.data;
            // 确保 purchasesItems 是数组
            if (!this.orderInfo.purchasesItems) {
              this.orderInfo.purchasesItems = [];
            }
            console.log('订单详情:', this.orderInfo);
          } else {
            this.$message({
              type: 'error',
              message: '获取订单详情失败',
              duration: 2000
            });
          }
        })
        .catch((error) => {
          this.loading = false;
          console.error('加载订单详情失败:', error);
          let errorMsg = '加载订单详情失败';
          if (error.response && error.response.data && error.response.data.msg) {
            errorMsg = error.response.data.msg;
          }
          this.$message({
            type: 'error',
            message: errorMsg,
            duration: 2000
          });
        });
    }
  }
};
</script>

<style scoped>
/* 对话框固定定位 */
.order-detail-dialog >>> .el-dialog__wrapper {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  overflow: auto;
}

.order-detail-dialog >>> .el-dialog {
  margin: 5vh auto !important;
  position: relative;
}

.order-detail-dialog >>> .el-dialog__body {
  padding: 20px;
  overflow-x: hidden;
}

.detail-container {
  max-height: 65vh;
  overflow-y: auto;
  overflow-x: hidden;
}

.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>

.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>


.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>

.info-card {
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: transparent;
}

.info-card:last-child {
  margin-bottom: 0;
}

.card-header {
  padding: 10px 16px;
  background: transparent;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  font-size: 16px;
  color: #409eff;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  min-width: 90px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  word-break: break-all;
}

.info-row .value.price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 18px;
}

/* 总计行 */
.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 16px 20px;
  background: transparent;
  border-top: 2px solid #ebeef5;
}

.total-label {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-right: 12px;
}

.total-value {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 700;
}

/* 滚动条样式 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 表格优化 */
.order-detail-dialog >>> .el-table {
  font-size: 14px;
  width: 100% !important;
}

.order-detail-dialog >>> .el-table th {
  background: transparent;
  color: #606266;
  font-weight: 600;
}

.order-detail-dialog >>> .el-table__body-wrapper {
  overflow-x: hidden !important;
}

/* 确保所有内容不出现横向滚动条 */
.order-detail-dialog >>> * {
  box-sizing: border-box;
}
</style>

