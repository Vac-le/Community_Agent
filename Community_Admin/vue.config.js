module.exports = {
  devServer: {
    port: 8080, // 修改为你想要的端口号，例如：8080, 3000, 8081 等
    open: true, // 是否自动打开浏览器
    overlay: {
      warnings: false,
      errors: true
    }
  }
}

