<template>
  <el-dialog
    title="查看权限"
    :visible.sync="dialogVisible"
    width="480px"
    :close-on-click-modal="false"
    :append-to-body="true"
    class="admin-dialog"
  >
    <div class="menu-tree" v-if="parentMenus.length">
      <div class="menu-group" v-for="parent in parentMenus" :key="parent.id">
        <div class="parent-title">
          <i :class="getMenuIcon(parent.name)"></i>
          <span>{{ parent.name }}</span>
        </div>
        <div v-if="parent.children && parent.children.length" class="child-list">
          <span class="child-item" v-for="child in parent.children" :key="child.id">
            <i :class="getMenuIcon(child.name)"></i>
            {{ child.name }}
          </span>
        </div>
        <div v-else class="child-empty">暂无子菜单</div>
      </div>
    </div>
    <div class="empty" v-else>
      <el-empty description="暂无权限数据" :image-size="120"></el-empty>
    </div>

    <span slot="footer" class="dialog-footer">
      <el-button type="warning" @click="dialogVisible = false">关 闭</el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialogVisible: false,
      menus: [],
      parentMenus: []
    };
  },
  methods: {
    open(id) {
      this.dialogVisible = true;
      this.fetchMenus(id);
    },
    fetchMenus(id) {
      if (!id) return;
      this.$http.get(`/api/menuCtl/lookMenu?id=${id}`).then((resp) => {
        if (resp.data && resp.data.data) {
          this.menus = resp.data.data;
          this.parentMenus = this.buildMenuTree(this.menus);
        } else {
          this.menus = [];
          this.parentMenus = [];
        }
      });
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
    }
  }
};
</script>

<style scoped>
.admin-dialog >>> .el-dialog__body {
  padding: 20px;
}

.menu-tree {
  max-height: 360px;
  overflow-y: auto;
  padding-right: 4px;
}

.menu-group + .menu-group {
  margin-top: 16px;
}

.parent-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 4px;
  padding: 8px 12px;
}

.parent-title i {
  color: #409eff;
}

.child-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 4px 0 4px;
}

.child-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 4px;
  color: #606266;
  font-size: 13px;
}

.child-item i {
  color: #67c23a;
}

.child-empty {
  padding: 12px;
  color: #909399;
  font-size: 13px;
}

.empty {
  padding: 40px 0;
}

.dialog-footer {
  text-align: right;
}
</style>

