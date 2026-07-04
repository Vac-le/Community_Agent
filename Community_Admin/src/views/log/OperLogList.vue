<template>
  <div class="app-page-container">
    <div class="page-header-actions">
      <div class="search-group">
        <el-input
          v-model="queryParams.title"
          placeholder="模块标题"
          class="modern-input"
          @keyup.enter.native="handleQuery"
        />
        <el-input
          v-model="queryParams.operName"
          placeholder="操作人员"
          class="modern-input"
          @keyup.enter.native="handleQuery"
        />
        <el-select
          v-model="queryParams.businessType"
          placeholder="业务类型"
          class="modern-input"
          clearable
        >
          <el-option label="其它" :value="0" />
          <el-option label="新增" :value="1" />
          <el-option label="修改" :value="2" />
          <el-option label="删除" :value="3" />
          <el-option label="查询" :value="4" />
        </el-select>
        <el-button type="primary" icon="el-icon-search" class="modern-btn search-btn" @click="handleQuery">查询</el-button>
        <el-button type="info" icon="el-icon-refresh" class="modern-btn ghost" @click="resetQuery">重置</el-button>
      </div>
      <div class="action-group">
        <el-button type="danger" icon="el-icon-delete" class="modern-btn ghost-danger" :disabled="multiple" @click="handleDelete">批量删除</el-button>
        <el-button type="danger" icon="el-icon-refresh-right" class="modern-btn ghost-danger" @click="handleClean">清空日志</el-button>
        <el-button type="success" icon="el-icon-download" class="modern-btn ghost" @click="exportExcel">导出</el-button>
      </div>
    </div>

    <el-card class="modern-card table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="logList"
        class="glass-table"
        :header-cell-style="headerStyle"
        @selection-change="handleSelectionChange"
        border
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="模块" prop="title" min-width="120" show-overflow-tooltip />
        <el-table-column label="类型" width="90" align="center">
          <template slot-scope="scope">
            <el-tag :type="businessTypeTag(scope.row.businessType)" size="mini" effect="dark">
              {{ businessTypeFormat(scope.row.businessType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作人" prop="operName" width="100" align="center" />
        <el-table-column label="IP地址" prop="operIp" width="130" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 0 ? 'success' : 'danger'" size="mini" effect="dark">
              {{ scope.row.status === 0 ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="90" align="center">
          <template slot-scope="scope">
            <span class="cost-time">{{ scope.row.costTime }}ms</span>
          </template>
        </el-table-column>
        <el-table-column label="操作时间" prop="operTime" width="170" align="center">
          <template slot-scope="scope">
            <div class="time-cell">
              <i class="el-icon-time"></i>
              <span>{{ formatDate(scope.row.operTime) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="table-ops">
              <el-button size="mini" type="text" class="op-btn primary" icon="el-icon-view" @click="handleView(scope.row)">详细</el-button>
              <el-button size="mini" type="text" class="op-btn danger" icon="el-icon-delete" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          @size-change="getList"
          @current-change="getList"
          :current-page.sync="queryParams.pageNum"
          :page-size.sync="queryParams.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <el-dialog title="日志详情" :visible.sync="detailOpen" width="700px" append-to-body custom-class="modern-dark-dialog">
      <div class="log-detail-view" v-if="form.id">
        <div class="detail-section">
          <div class="section-title">基本信息</div>
          <div class="info-grid">
            <div class="info-item"><span class="label">操作模块：</span><span class="val">{{ form.title }}</span></div>
            <div class="info-item"><span class="label">操作人员：</span><span class="val">{{ form.operName }}</span></div>
            <div class="info-item"><span class="label">主机地址：</span><span class="val">{{ form.operIp }}</span></div>
            <div class="info-item"><span class="label">耗时时间：</span><span class="val">{{ form.costTime }}ms</span></div>
          </div>
        </div>
        <div class="detail-section">
          <div class="section-title">请求详情</div>
          <div class="code-label">请求地址</div>
          <div class="code-snippet">{{ form.operUrl }}</div>
          <div class="code-label">请求方法</div>
          <div class="code-snippet">{{ form.method }}</div>
          <div class="code-label">请求参数</div>
          <pre class="code-block">{{ form.operParam }}</pre>
          <div class="code-label">返回结果</div>
          <pre class="code-block">{{ form.jsonResult }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { exportRowsToExcel } from "../../utils/excel"

export default {
  name: 'OperLog',
  data() {
    return {
      loading: true,
      ids: [],
      multiple: true,
      total: 0,
      logList: [],
      detailOpen: false,
      form: {},
      queryParams: { pageNum: 1, pageSize: 10, title: '', operName: '', businessType: undefined, status: undefined },
      headerStyle: {
        backgroundColor: 'rgba(15, 23, 42, 0.45)',
        color: '#94a3b8', padding: '16px 0', fontWeight: '600', borderBottom: '1px solid rgba(255,255,255,0.08)'
      }
    };
  },
  created() { this.getList(); },
  methods: {
    getList() {
      this.loading = true;
      this.$http.get('/api/operLog/list', { params: this.queryParams }).then(res => {
        this.logList = res.data.data || [];
        this.total = res.data.total || 0;
      }).finally(() => { this.loading = false; });
    },
    businessTypeFormat(type) {
      const map = { 0: '其它', 1: '新增', 2: '修改', 3: '删除', 4: '查询', 5: '导出', 6: '导入' };
      return map[type] || '未知';
    },
    businessTypeTag(type) {
      const tagMap = { 0: 'info', 1: 'success', 2: 'warning', 3: 'danger', 4: '', 5: 'success', 6: 'warning' };
      return tagMap[type] || 'info';
    },
    formatDate(v) {
      if (!v) return '';
      const d = new Date(v);
      const pad = (n) => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    },
    handleSelectionChange(selection) {
      this.ids = selection.map(i => i.id);
      this.multiple = !selection.length;
    },
    handleQuery() { this.queryParams.pageNum = 1; this.getList(); },
    resetQuery() { this.queryParams = { pageNum: 1, pageSize: 10, title: '', operName: '' }; this.getList(); },
    handleView(row) { this.form = { ...row }; this.detailOpen = true; },
    handleDelete(row) {
      const ids = row ? [row.id] : this.ids;
      this.$confirm(`确认删除选中的日志数据吗？`, '警告', {
        type: 'error', customClass: 'dark-message-box'
      }).then(() => {
        const api = Array.isArray(ids) ? this.$http.delete('/api/operLog/batch', { data: ids }) : this.$http.delete(`/api/operLog/${ids}`);
        api.then(() => { this.$message.success('删除成功'); this.getList(); });
      });
    },
    handleClean() {
      this.$confirm('确定清空所有日志？', '警告', { type: 'error', customClass: 'dark-message-box' }).then(() => {
        this.$http.delete('/api/operLog/clean').then(() => { this.$message.success('清空成功'); this.getList(); });
      });
    },
    exportExcel() {
      if (!this.logList.length) return this.$message.warning('暂无可导出数据');
      const rows = [['编号', '模块', '类型', '人员', 'IP', '状态', '时间']];
      this.logList.forEach(i => rows.push([i.id, i.title, this.businessTypeFormat(i.businessType), i.operName, i.operIp, i.status === 0 ? '正常' : '异常', this.formatDate(i.operTime)]));
      exportRowsToExcel('操作日志', rows);
    }
  }
};
</script>

<style scoped>
.app-page-container { animation: fadeIn 0.4s ease-out; }
.page-header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; gap: 20px; }
.search-group { display: flex; gap: 12px; flex: 1; }
.modern-input >>> .el-input__inner {
  background: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important;
  color: #f8fafc !important; border-radius: 12px; height: 42px;
}
.modern-btn { border-radius: 12px; height: 42px; padding: 0 20px; font-weight: 500; transition: all 0.3s ease; }
.modern-btn.ghost { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); color: #cbd5e1; }
.modern-btn.ghost-danger { background: rgba(248, 113, 113, 0.05); border: 1px solid rgba(248, 113, 113, 0.2); color: #f87171; }
.modern-card { background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(10, 18, 34, 0.9)) !important; border: 1px solid rgba(255, 255, 255, 0.06) !important; border-radius: 20px; backdrop-filter: blur(20px); }
.glass-table { background: transparent !important; }
.glass-table >>> tr { background-color: transparent !important; }
.glass-table >>> td { border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important; color: #cbd5e1; padding: 14px 0; }
.cost-time { color: #38bdf8; font-family: monospace; }
.time-cell { display: flex; align-items: center; justify-content: center; gap: 8px; color: #94a3b8; font-size: 13px; }
.table-ops { display: flex; justify-content: center; gap: 8px; }
.op-btn { font-weight: 600 !important; }
.op-btn.primary { color: #60a5fa !important; }
.op-btn.danger { color: #f87171 !important; }
.pagination-container { padding: 24px; display: flex; justify-content: flex-end; }

/* 详情样式 */
.detail-section { margin-bottom: 24px; }
.section-title { font-size: 14px; color: #60a5fa; margin-bottom: 16px; font-weight: 600; border-left: 3px solid #3b82f6; padding-left: 10px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.info-item { font-size: 13px; }
.info-item .label { color: #94a3b8; }
.info-item .val { color: #f8fafc; }
.code-label { font-size: 12px; color: #64748b; margin: 12px 0 6px; }
.code-snippet { background: rgba(0,0,0,0.2); padding: 8px 12px; border-radius: 8px; color: #38bdf8; font-size: 13px; }
.code-block { background: rgba(0,0,0,0.3); padding: 16px; border-radius: 12px; color: #cbd5e1; font-size: 12px; line-height: 1.6; max-height: 150px; overflow-y: auto; border: 1px solid rgba(255,255,255,0.05); }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>