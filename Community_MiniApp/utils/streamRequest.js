// 封装流式POST请求（适配后端 Agent SSE 接口）
const streamPost = (url, data) => {
  return new Promise((resolve, reject) => {
    const requestTask = uni.request({
      url: url,
      method: 'POST',
      data: data,
      header: {
        'Content-Type': 'application/json'
      },
      enableChunked: true,
      showLoading: false,
      success: () => {},
      fail: (err) => {
        reject(err);
      }
    });

    resolve({
      onHeadersReceived: (callback) => {
        requestTask.onHeadersReceived((res) => {
          callback(res.header);
        });
      },
      onChunkReceived: (callback) => {
        requestTask.onChunkReceived((res) => {
          callback(res.data);
        });
      },
      abort: () => {
        requestTask.abort();
      }
    });
  });
};

export { streamPost };