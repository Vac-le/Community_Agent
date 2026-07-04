<template>
  <div class="ai-chat-container">
    <!-- 左侧历史会话栏 -->
    <div class="chat-sidebar">
      <div class="sidebar-top">
        <div class="sidebar-title">
          <i class="el-icon-cpu"></i>
          <span>AI 助手</span>
        </div>
        <button class="new-chat-btn" @click="newChat">
          <i class="el-icon-plus"></i>
          新对话
        </button>
      </div>
      <div class="session-list">
        <div
          v-for="(session, idx) in sessions"
          :key="idx"
          class="session-item"
          :class="{ active: currentSession === idx }"
          @click="switchSession(idx)"
        >
          <i class="el-icon-chat-dot-round"></i>
          <span class="session-name">{{ session.name }}</span>
          <i class="el-icon-delete session-del" @click.stop="deleteSession(idx)"></i>
        </div>
      </div>
    </div>

    <!-- 右侧对话区 -->
    <div class="chat-main">
      <!-- 顶部标题栏 -->
      <div class="chat-header">
        <div class="chat-header-left">
          <div class="ai-avatar-header">
            <i class="el-icon-cpu"></i>
          </div>
          <div>
            <div class="chat-title">智慧社区 AI 助手</div>
            <div class="chat-subtitle">基于通义百炼大模型 · 随时为您解答</div>
          </div>
        </div>
        <div class="chat-header-right">
          <span class="status-dot"></span>
          <span class="status-text">在线</span>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageList">
        <!-- 欢迎屏 -->
        <div v-if="currentMessages.length === 0" class="welcome-screen">
          <div class="welcome-icon">
            <i class="el-icon-cpu"></i>
          </div>
          <div class="welcome-title">你好，我是智慧社区 AI 助手</div>
          <div class="welcome-desc">我可以帮你分析社区数据、解答业务问题、生成报表洞察</div>
          <div class="quick-actions">
            <div
              class="quick-item"
              v-for="q in quickQuestions"
              :key="q"
              @click="sendQuick(q)"
            >{{ q }}</div>
          </div>
        </div>

        <!-- 消息气泡 -->
        <template v-for="(msg, idx) in currentMessages">
          <!-- 用户消息 -->
          <div v-if="msg.role === 'user'" :key="'u' + idx" class="msg-row user-row">
            <div class="msg-bubble user-bubble">
              <div class="bubble-text">{{ msg.content }}</div>
            </div>
            <div class="msg-avatar user-avatar-icon">
              <i class="el-icon-user"></i>
            </div>
          </div>
          <!-- AI 消息 -->
          <div v-else :key="'a' + idx" class="msg-row ai-row">
            <div class="msg-avatar ai-avatar-icon">
              <i class="el-icon-cpu"></i>
            </div>
            <div class="msg-bubble ai-bubble">
              <div class="bubble-text" v-html="renderMarkdown(msg.content)"></div>
              <div v-if="msg.typing" class="typing-cursor"></div>
              <div class="bubble-meta">
                <span>{{ msg.time }}</span>
                <span class="copy-btn" @click="copyText(msg.content)"><i class="el-icon-document-copy"></i> 复制</span>
              </div>
            </div>
          </div>
        </template>

        <!-- 加载中 -->
        <div v-if="loading" class="msg-row ai-row">
          <div class="msg-avatar ai-avatar-icon">
            <i class="el-icon-cpu"></i>
          </div>
          <div class="msg-bubble ai-bubble loading-bubble">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <div class="input-box">
          <textarea
            ref="inputRef"
            v-model="inputText"
            class="chat-input"
            placeholder="输入消息，Shift+Enter 换行，Enter 发送…"
            rows="1"
            @keydown.enter.exact.prevent="sendMessage"
            @input="autoResize"
          ></textarea>
          <button
            class="send-btn"
            :class="{ active: inputText.trim() && !loading }"
            :disabled="!inputText.trim() || loading"
            @click="sendMessage"
          >
            <i class="el-icon-s-promotion"></i>
          </button>
        </div>
        <div class="input-hint">Enter 发送 · Shift+Enter 换行</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AiChat',
  data() {
    return {
      inputText: '',
      loading: false,
      sessions: [{ name: '新对话 1', messages: [] }],
      currentSession: 0,
      quickQuestions: [
        '分析一下当前社区的订单趋势',
        '如何提升社区用户的活跃度？',
        '帮我生成一份社区运营日报模板',
        '代购、餐饮、家政哪个订单量更高？'
      ]
    };
  },
  computed: {
    currentMessages() {
      const session = this.sessions[this.currentSession];
      return session ? session.messages : [];
    }
  },
  methods: {
    autoResize() {
      const el = this.$refs.inputRef;
      if (!el) return;
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 160) + 'px';
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.messageList;
        if (el) el.scrollTop = el.scrollHeight;
      });
    },
    newChat() {
      this.sessions.push({ name: `新对话 ${this.sessions.length + 1}`, messages: [] });
      this.currentSession = this.sessions.length - 1;
    },
    switchSession(idx) {
      this.currentSession = idx;
      this.scrollToBottom();
    },
    deleteSession(idx) {
      if (this.sessions.length === 1) {
        this.sessions[0].messages = [];
        this.sessions[0].name = '新对话 1';
        return;
      }
      this.sessions.splice(idx, 1);
      if (this.currentSession >= this.sessions.length) {
        this.currentSession = this.sessions.length - 1;
      }
    },
    sendQuick(q) {
      this.inputText = q;
      this.sendMessage();
    },
    now() {
      const d = new Date();
      return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
    },
    async sendMessage() {
      const text = this.inputText.trim();
      if (!text || this.loading) return;

      // 更新会话名称（取前12字）
      const session = this.sessions[this.currentSession];
      if (session.messages.length === 0) {
        session.name = text.slice(0, 12) + (text.length > 12 ? '…' : '');
      }

      session.messages.push({ role: 'user', content: text, time: this.now() });
      this.inputText = '';
      this.$nextTick(() => {
        if (this.$refs.inputRef) this.$refs.inputRef.style.height = 'auto';
      });
      this.scrollToBottom();
      this.loading = true;

      // 占位 AI 消息（流式填充）
      const aiMsg = { role: 'ai', content: '', time: this.now(), typing: true };
      session.messages.push(aiMsg);
      this.scrollToBottom();

      try {
        const response = await fetch(
          (this.$http.defaults.baseURL || '').replace(/\/$/, '') + '/chatCtl/chat',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text })
          }
        );

        if (!response.ok) throw new Error('请求失败');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          // 按 SSE 格式解析：每块以 \n\n 结尾
          const parts = buffer.split('\n\n');
          buffer = parts.pop(); // 保留未完成的片段

          for (const part of parts) {
            const dataLine = part.split('\n').find(l => l.startsWith('data:'));
            if (!dataLine) continue;
            try {
              const json = JSON.parse(dataLine.replace(/^data:/, '').trim());
              const chunkText = json && json.output && json.output.text ? json.output.text : '';
              aiMsg.content += chunkText;
              this.scrollToBottom();
            } catch (_) { /* 忽略解析错误 */ }
          }
        }
      } catch (e) {
        aiMsg.content = '请求失败，请检查网络或后端服务。';
      } finally {
        aiMsg.typing = false;
        this.loading = false;
        this.scrollToBottom();
      }
    },
    renderMarkdown(text) {
      if (!text) return '';
      // 简易 Markdown 渲染：粗体、代码块、换行
      return text
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/```([\s\S]*?)```/g, '<pre class="code-pre"><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br/>');
    },
    copyText(text) {
      navigator.clipboard.writeText(text).then(() => {
        this.$message({ message: '已复制到剪贴板', type: 'success', duration: 1500 });
      });
    }
  }
};
</script>

<style scoped>
/* ===== 整体布局 ===== */
.ai-chat-container {
  display: flex;
  height: calc(100vh - 64px - 56px);
  min-height: 500px;
  border-radius: 16px;
  overflow: hidden;
  background: rgba(12, 25, 41, 0.55);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 48px rgba(0, 0, 0, 0.45);
}

/* ===== 左侧会话栏 ===== */
.chat-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: rgba(8, 18, 32, 0.70);
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar-top {
  padding: 20px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sidebar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: 1px;
}
.sidebar-title i { font-size: 18px; color: #60a5fa; }
.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 0;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(37,99,235,0.35);
}
.new-chat-btn:hover { background: linear-gradient(135deg, #4f8ff7, #2d6df0); transform: translateY(-1px); }
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 8px;
}
.session-list::-webkit-scrollbar { width: 0; }
.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  color: rgba(148,163,184,0.8);
  font-size: 13px;
  transition: all 0.2s;
  position: relative;
  margin-bottom: 4px;
}
.session-item:hover { background: rgba(59,130,246,0.10); color: #93c5fd; }
.session-item.active { background: rgba(59,130,246,0.18); color: #60a5fa; font-weight: 600; }
.session-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.session-del {
  opacity: 0;
  font-size: 13px;
  transition: opacity 0.2s;
  color: #f87171;
}
.session-item:hover .session-del { opacity: 1; }

/* ===== 右侧主对话区 ===== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* 顶部标题栏 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  background: rgba(255,255,255,0.03);
  flex-shrink: 0;
}
.chat-header-left { display: flex; align-items: center; gap: 14px; }
.ai-avatar-header {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #6d28d9);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; color: #fff;
  box-shadow: 0 4px 14px rgba(59,130,246,0.4);
}
.chat-title { font-size: 15px; font-weight: 700; color: #e2e8f0; }
.chat-subtitle { font-size: 12px; color: rgba(148,163,184,0.6); margin-top: 2px; }
.chat-header-right { display: flex; align-items: center; gap: 7px; }
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 6px rgba(52,211,153,0.7);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%,100% { opacity: 1; }
  50% { opacity: 0.35; }
}
.status-text { color: #a7f3d0; font-size: 12px; }

/* 消息区 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 26px 24px;
  background:
    radial-gradient(circle at top left, rgba(59,130,246,0.12), transparent 28%),
    radial-gradient(circle at bottom right, rgba(109,40,217,0.12), transparent 30%),
    rgba(9, 17, 28, 0.32);
}
.message-list::-webkit-scrollbar { width: 6px; }
.message-list::-webkit-scrollbar-thumb {
  background: rgba(148,163,184,0.25);
  border-radius: 4px;
}

.welcome-screen {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 30px 10px;
}
.welcome-icon {
  width: 88px;
  height: 88px;
  border-radius: 24px;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 40px;
  box-shadow: 0 16px 40px rgba(59,130,246,0.28);
  margin-bottom: 22px;
}
.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #f8fafc;
  margin-bottom: 12px;
}
.welcome-desc {
  color: rgba(148,163,184,0.78);
  font-size: 14px;
  margin-bottom: 28px;
}
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  max-width: 760px;
}
.quick-item {
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  color: #dbeafe;
  cursor: pointer;
  transition: all 0.22s ease;
}
.quick-item:hover {
  transform: translateY(-2px);
  background: rgba(59,130,246,0.14);
  border-color: rgba(96,165,250,0.35);
  box-shadow: 0 8px 20px rgba(37,99,235,0.18);
}

.msg-row {
  display: flex;
  margin-bottom: 22px;
  align-items: flex-start;
  gap: 12px;
}
.user-row {
  justify-content: flex-end;
}
.ai-row {
  justify-content: flex-start;
}
.msg-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}
.ai-avatar-icon {
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  color: #fff;
  box-shadow: 0 8px 18px rgba(59,130,246,0.24);
}
.user-avatar-icon {
  background: linear-gradient(135deg, #0f766e 0%, #059669 100%);
  color: #fff;
  box-shadow: 0 8px 18px rgba(16,185,129,0.2);
}
.msg-bubble {
  max-width: min(72%, 860px);
  border-radius: 18px;
  padding: 14px 16px;
  line-height: 1.75;
  font-size: 14px;
  word-break: break-word;
  box-shadow: 0 10px 28px rgba(0,0,0,0.16);
}
.ai-bubble {
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
  border: 1px solid rgba(255,255,255,0.08);
  border-top-left-radius: 6px;
}
.user-bubble {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #fff;
  border-top-right-radius: 6px;
}
.bubble-text {
  white-space: normal;
}
.bubble-meta {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: rgba(148,163,184,0.72);
}
.copy-btn {
  cursor: pointer;
  transition: color 0.2s ease;
}
.copy-btn:hover {
  color: #93c5fd;
}
.typing-cursor {
  display: inline-block;
  width: 8px;
  height: 16px;
  margin-left: 3px;
  background: #60a5fa;
  border-radius: 2px;
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 74px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #93c5fd;
  animation: wave 1.3s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes wave {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.code-pre {
  margin: 10px 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(2, 6, 23, 0.68);
  border: 1px solid rgba(255,255,255,0.08);
  overflow-x: auto;
}
.inline-code {
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(15,23,42,0.75);
  color: #93c5fd;
}

/* 输入区 */
.input-area {
  padding: 18px 20px 16px;
  border-top: 1px solid rgba(255,255,255,0.07);
  background: rgba(7, 14, 26, 0.74);
  flex-shrink: 0;
}
.input-box {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px;
  border-radius: 18px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}
.chat-input {
  flex: 1;
  resize: none;
  border: none;
  outline: none;
  background: transparent;
  color: #e2e8f0;
  font-size: 14px;
  line-height: 1.7;
  min-height: 24px;
  max-height: 160px;
  font-family: inherit;
}
.chat-input::placeholder {
  color: rgba(148,163,184,0.5);
}
.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: none;
  background: rgba(148,163,184,0.16);
  color: rgba(255,255,255,0.55);
  cursor: not-allowed;
  transition: all 0.2s ease;
}
.send-btn.active {
  cursor: pointer;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
  box-shadow: 0 10px 24px rgba(37,99,235,0.34);
}
.send-btn.active:hover {
  transform: translateY(-1px) scale(1.02);
}
.input-hint {
  margin-top: 8px;
  padding-left: 8px;
  color: rgba(148,163,184,0.55);
  font-size: 12px;
}

@media (max-width: 992px) {
  .chat-sidebar {
    display: none;
  }
  .msg-bubble {
    max-width: 84%;
  }
}

@media (max-width: 768px) {
  .ai-chat-container {
    height: calc(100vh - 64px - 32px);
    border-radius: 12px;
  }
  .chat-header,
  .message-list,
  .input-area {
    padding-left: 14px;
    padding-right: 14px;
  }
  .welcome-title {
    font-size: 22px;
  }
}
</style>