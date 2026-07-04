<template>
  <view class="chat-shell">
    <view class="chat-background">
      <view class="orb orb-a"></view>
      <view class="orb orb-b"></view>
      <view class="grid-mask"></view>
    </view>

    <view class="chat-container">
      <view class="hero-card" v-if="messages.length === 0">
        <view class="hero-badge">社区智能中枢</view>
        <view class="hero-icon-wrap">
          <view class="hero-icon">✦</view>
        </view>
        <text class="hero-title">AI 社区助手</text>
        <text class="hero-desc">支持社区问答、服务指引、流程咨询，为居民提供更快更清晰的回应。</text>

        <view class="feature-board">
          <view class="feature-card feature-primary">
            <text class="feature-label">即时响应</text>
            <text class="feature-value">流式对话</text>
          </view>
          <view class="feature-card">
            <text class="feature-label">服务覆盖</text>
            <text class="feature-value">社区业务问答</text>
          </view>
          <view class="feature-card">
            <text class="feature-label">建议提问</text>
            <text class="feature-value">数据分析/帮我订餐/社区信息</text>
          </view>
        </view>
      </view>

      <scroll-view
        scroll-y
        class="messages-scroll"
        :scroll-into-view="scrollIntoView"
        scroll-with-animation
      >
        <view
          v-for="(msg, index) in messages"
          :key="index"
          :id="`msg-${index}`"
          class="message-row"
          :class="msg.role === 'assistant' ? 'assistant-row' : 'user-row'"
        >
          <view v-if="msg.role === 'assistant'" class="avatar assistant-avatar">
            <text class="avatar-text">AI</text>
          </view>

          <view class="message-column" :class="msg.role === 'assistant' ? 'assistant-column' : 'user-column'">
            <text class="speaker-tag">{{ msg.role === 'assistant' ? (msg.intent || '社区助手') : '我' }}</text>
            <view class="message-bubble" :class="msg.role === 'assistant' ? 'assistant-bubble' : 'user-bubble'">
              <text v-if="msg.content" class="message-text">{{ msg.content }}</text>
              <view v-if="msg.charts && msg.charts.length" class="chart-list">
                <view v-for="(chart, chartIndex) in msg.charts" :key="chartIndex" class="chart-card">
                  <image
                    class="chart-image"
                    :src="chart.imageUrl"
                    mode="widthFix"
                    :show-menu-by-longpress="true"
                    @click="previewChart(chart.imageUrl)"
                  />
                  <text class="chart-title">{{ chart.title || 'AI 生成图表' }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view v-if="isLoading" class="thinking-row">
          <view class="avatar assistant-avatar">
            <text class="avatar-text">AI</text>
          </view>
          <view class="thinking-card">
            <text class="thinking-label">{{ statusText || '正在生成回复' }}</text>
            <view class="thinking-dots">
              <view class="dot"></view>
              <view class="dot"></view>
              <view class="dot"></view>
            </view>
          </view>
        </view>
      </scroll-view>

      <view class="composer-shell">
        <view class="composer-card">
          <view class="composer-topline">
            <text class="composer-hint">请描述你的问题，例如：帮我按上次口味订一份午餐</text>
          </view>
          <view class="input-box">
            <input
              v-model="input"
              placeholder="输入社区相关问题..."
              class="input-field"
              :disabled="isLoading"
              maxlength="-1"
              confirm-type="send"
              @confirm="sendMessage"
            />
            <button
              @click="sendMessage"
              class="send-btn"
              :disabled="!input.trim() || isLoading"
            >
              <text class="send-icon">➜</text>
            </button>
          </view>
        </view>
      </view>
    </view>

    <view v-if="showOrderCard" class="modal-mask" @click="hideOrderCard">
      <view class="order-modal" @click.stop>
        <view class="modal-top">
          <view>
            <text class="modal-title">确认点单内容</text>
            <text class="modal-subtitle">AI 已根据你的意图整理推荐菜品，确认后才会生成草稿并继续下单</text>
          </view>
          <view class="modal-close" @click="hideOrderCard">×</view>
        </view>

        <view class="order-overview">
          <view class="overview-card">
            <text class="overview-label">菜品件数</text>
            <text class="overview-value">{{ aiOrderItems.length }}件</text>
          </view>
          <view class="overview-card total-card">
            <text class="overview-label">订单金额</text>
            <text class="overview-value price">¥{{ aiOrderTotal.toFixed(2) }}</text>
          </view>
        </view>

        <view v-if="recommendSummary" class="summary-banner">
          <text class="summary-label">推荐说明</text>
          <text class="summary-text">{{ recommendSummary }}</text>
        </view>

        <view class="modal-section">
          <text class="section-caption">菜品清单</text>
          <view class="modal-list">
            <view v-for="(item, index) in aiOrderItems" :key="item.id || index" class="modal-item">
              <view class="modal-item-main">
                <text class="modal-item-name">{{ item.name }}</text>
                <text class="modal-item-desc">单价 ¥{{ Number(item.price || 0).toFixed(2) }}</text>
              </view>
              <view class="modal-item-right">
                <text class="modal-item-count">x{{ item.quantity }}</text>
                <text class="modal-item-price">¥{{ (Number(item.price || 0) * Number(item.quantity || 0)).toFixed(2) }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="modal-section">
          <text class="section-caption">配送信息</text>
          <view class="field-card compact-field-card">
            <text class="field-label">配送地址</text>
            <textarea
              class="field-area address-field compact-textarea"
              v-model="deliveryAddress"
              placeholder="请输入配送地址"
              maxlength="100"
              :show-confirm-bar="false"
              auto-height="false"
            ></textarea>
          </view>
          <view class="field-card">
            <text class="field-label">联系电话</text>
            <input
              class="field-input"
              type="number"
              v-model="deliveryPhone"
              placeholder="请输入联系电话"
              maxlength="11"
            />
          </view>
        </view>

        <view class="modal-section">
          <text class="section-caption">订单备注</text>
          <view class="field-card compact-field-card">
            <textarea
              class="field-area compact-textarea"
              v-model="orderRemark"
              placeholder="请输入口味偏好、少辣少盐等备注（选填）"
              maxlength="100"
              :show-confirm-bar="false"
              auto-height="false"
            ></textarea>
            <text class="remark-count">{{ orderRemark.length }}/100</text>
          </view>
        </view>

        <view class="modal-actions">
          <view class="modal-btn light" @click="hideOrderCard">取消</view>
          <view class="modal-btn strong" @click="confirmFoodOrder">
            确认生成草稿并下单
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { callAgentStream } from '@/utils/aiService';

export default {
  data() {
    return {
      input: '',
      messages: [],
      scrollIntoView: '',
      isLoading: false,
      statusText: '',
      streamBuffer: '',
      currentAssistantIndex: -1,
      typingQueue: [],
      typingTimer: null,
      streamCompleted: false,
      renderBuffer: '',
      renderTimer: null,
      showOrderCard: false,
      aiOrderSessionId: '',
      aiOrderItems: [],
      aiOrderAmount: 0,
      deliveryAddress: '',
      deliveryPhone: '',
      orderRemark: '',
      recommendSummary: '',
      previewFromHistory: false,
      foodCatalog: [],
      agentSessionId: ''
    }
  },

  computed: {
    aiOrderTotal() {
      if (Number(this.aiOrderAmount || 0) > 0) {
        return Number(this.aiOrderAmount || 0);
      }
      return this.aiOrderItems.reduce((sum, item) => {
        return sum + Number(item.price || 0) * Number(item.quantity || 0);
      }, 0);
    }
  },

  onLoad() {
    this.agentSessionId = uni.getStorageSync('agentSessionId') || '';
    this.loadUserInfo();
    this.loadFoodCatalog();
  },

  methods: {
    loadUserInfo() {
      this.deliveryAddress = uni.getStorageSync('userAddress') || '';
      this.deliveryPhone = uni.getStorageSync('userPhone') || '';
    },

    async loadFoodCatalog() {
      try {
        const res = await this.$myRequest({
          url: '/user/ordersCtl/foodList',
          method: 'GET'
        });
        this.foodCatalog = Array.isArray(res?.data?.data) ? res.data.data : [];
        console.log('AI页面餐饮列表:', this.foodCatalog);
      } catch (error) {
        console.error('获取餐饮列表失败:', error);
        this.foodCatalog = [];
      }
    },

    async sendMessage() {
      if (this.isLoading) return;

      const userInput = (this.input || '').trim();
      if (userInput === '') return;

      this.resetStreamState();
      this.input = '';

      this.messages.push({
        role: 'user',
        content: userInput
      });
      this.isLoading = true;

      this.$nextTick(() => {
        this.scrollIntoView = `msg-${this.messages.length - 1}`;
      });

      try {
        const sseHandler = await callAgentStream(userInput, this.agentSessionId);

        sseHandler.onHeadersReceived((headers) => {
          console.log('响应头:', headers);
        });

        sseHandler.onChunkReceived((chunk) => {
          this.parseData(chunk);
        });
      } catch (error) {
        console.error('调用Agent流式接口失败:', error);
        this.resetStreamState();
        this.messages.push({
          role: 'assistant',
          content: '抱歉，AI服务暂时不可用，请稍后重试。'
        });
        this.isLoading = false;

        uni.showToast({
          title: '服务异常',
          icon: 'none',
          duration: 2000
        });
      }
    },

    resetStreamState() {
      this.statusText = '';
      this.streamBuffer = '';
      this.currentAssistantIndex = -1;
      this.typingQueue = [];
      this.streamCompleted = false;
      this.renderBuffer = '';
      if (this.typingTimer) {
        clearInterval(this.typingTimer);
        this.typingTimer = null;
      }
      if (this.renderTimer) {
        clearTimeout(this.renderTimer);
        this.renderTimer = null;
      }
    },

    appendToTypingQueue(text) {
      if (!text) {
        return;
      }
      this.renderBuffer += text;
      if (this.renderTimer) {
        return;
      }

      const flush = () => {
        if (!this.renderBuffer) {
          this.renderTimer = null;
          return;
        }

        const nextSlice = this.renderBuffer.slice(0, 1);
        this.renderBuffer = this.renderBuffer.slice(1);
        this.typingQueue.push(nextSlice);
        this.startTyping();
        this.renderTimer = setTimeout(flush, 16);
      };

      flush();
    },

    startTyping() {
      if (this.typingTimer) {
        return;
      }

      this.typingTimer = setInterval(() => {
        if (this.currentAssistantIndex === -1) {
          if (this.typingQueue.length === 0 && this.streamCompleted && !this.renderBuffer) {
            clearInterval(this.typingTimer);
            this.typingTimer = null;
            this.isLoading = false;
            this.streamCompleted = false;
          }
          return;
        }

        if (this.typingQueue.length > 0) {
          const nextChar = this.typingQueue.shift();
          this.messages[this.currentAssistantIndex].content += nextChar;
          this.$nextTick(() => {
            this.scrollIntoView = `msg-${this.messages.length - 1}`;
          });
          return;
        }

        if (this.streamCompleted && !this.renderBuffer) {
          clearInterval(this.typingTimer);
          this.typingTimer = null;
          this.isLoading = false;
          this.streamCompleted = false;
          this.currentAssistantIndex = -1;
        }
      }, 20);
    },

    arrayBufferToString(buffer) {
      if (typeof buffer === 'string') {
        return buffer;
      }

      try {
        const uint8Array = new Uint8Array(buffer);
        let result = '';
        for (let i = 0; i < uint8Array.length; i++) {
          result += String.fromCharCode(uint8Array[i]);
        }
        return decodeURIComponent(escape(result));
      } catch (e) {
        console.error('ArrayBuffer转换失败:', e);
        return '';
      }
    },

    parseData(data) {
      try {
        const rawString = this.arrayBufferToString(data);
        if (!rawString) {
          return;
        }

        this.streamBuffer += rawString;
        const events = this.streamBuffer.split('\n\n');
        this.streamBuffer = events.pop() || '';

        events.forEach(event => {
          const lines = event.split('\n');
          let eventData = null;

          lines.forEach(line => {
            if (line.startsWith('data:')) {
              const jsonString = line.substring(5).trim();
              try {
                eventData = JSON.parse(jsonString);
              } catch (e) {
                console.error('JSON解析失败:', jsonString);
              }
            }
          });

          if (!eventData) {
            return;
          }

          const type = eventData.type;
          const intent = eventData.intent || '';
          if (eventData.sessionId && eventData.sessionId !== this.agentSessionId) {
            this.agentSessionId = eventData.sessionId;
            uni.setStorageSync('agentSessionId', this.agentSessionId);
          }
          if (type === 'status') {
            this.statusText = eventData.message || '处理中...';
            return;
          }

          const payload = eventData.content || eventData.data || null;
          const hasStructuredOrder = payload && typeof payload === 'object' && !Array.isArray(payload);

          if (type === 'food_order_card' && intent === 'FOOD_CONFIRM' && hasStructuredOrder) {
            console.log('收到订餐卡片数据:', payload);
            this.openFoodOrderCard(payload);
            return;
          }

          if (type === 'chart' && hasStructuredOrder && payload.imageUrl) {
            console.log('收到图表图片数据:', payload);
            this.appendChartMessage(payload, intent);
            return;
          }

          if (type === 'final') {
            const text = eventData.content || '';
            if (!text) {
              return;
            }

            if (this.currentAssistantIndex === -1) {
              this.messages.push({
                role: 'assistant',
                intent,
                content: '',
                charts: []
              });
              this.currentAssistantIndex = this.messages.length - 1;
            } else if (intent) {
              this.messages[this.currentAssistantIndex].intent = intent;
            }

            this.messages[this.currentAssistantIndex].content = text;
            this.$nextTick(() => {
              this.scrollIntoView = `msg-${this.messages.length - 1}`;
            });
            return;
          }

          if (type === 'done') {
            this.streamCompleted = true;
            this.isLoading = false;
            this.statusText = '';
            this.currentAssistantIndex = -1;
            return;
          }

          if (type === 'error') {
            const errorMessage = eventData.message || '抱歉，AI服务暂时不可用，请稍后重试。';
            if (this.currentAssistantIndex === -1) {
              this.messages.push({
                role: 'assistant',
                intent: eventData.intent || 'ERROR',
                content: errorMessage
              });
            } else {
              this.messages[this.currentAssistantIndex].content = errorMessage;
              this.messages[this.currentAssistantIndex].intent = eventData.intent || 'ERROR';
            }
            this.streamCompleted = true;
            this.isLoading = false;
            this.statusText = '';
            this.currentAssistantIndex = -1;
          }
        });
      } catch (error) {
        console.error('解析数据失败:', error);
        this.isLoading = false;
        this.resetStreamState();
      }
    },

    appendChartMessage(chart, intent = 'CHART') {
      if (!chart || !chart.imageUrl) {
        return;
      }

      const chartPayload = {
        imageUrl: chart.imageUrl,
        title: chart.title || 'AI 生成图表',
        toolName: chart.toolName || ''
      };

      if (this.currentAssistantIndex !== -1) {
        const currentMessage = this.messages[this.currentAssistantIndex];
        if (currentMessage && currentMessage.role === 'assistant') {
          const charts = Array.isArray(currentMessage.charts) ? currentMessage.charts : [];
          charts.push(chartPayload);
          this.messages.splice(this.currentAssistantIndex, 1, Object.assign({}, currentMessage, {
            intent: intent || currentMessage.intent,
            charts: charts
          }));
          this.$nextTick(() => {
            this.scrollIntoView = `msg-${this.messages.length - 1}`;
          });
          return;
        }
      }

      this.messages.push({
        role: 'assistant',
        intent: intent || 'CHART',
        content: '已生成图表，点击图片可预览。',
        charts: [chartPayload]
      });
      this.$nextTick(() => {
        this.scrollIntoView = `msg-${this.messages.length - 1}`;
      });
    },

    previewChart(imageUrl) {
      if (!imageUrl) {
        return;
      }
      uni.previewImage({
        urls: [imageUrl],
        current: imageUrl
      });
    },

    openFoodOrderCard(order) {
      const items = Array.isArray(order.items)
        ? order.items
        : Array.isArray(order.orderItems)
          ? order.orderItems
          : [];

      console.log('收到订餐卡片原始数据:', order);
      console.log('当前餐饮列表:', this.foodCatalog);

      this.aiOrderSessionId = order.sessionId || '';
      this.aiOrderAmount = Number(order.amount || 0);
      this.aiOrderItems = items.map((item, index) => {
        const matchedFood = this.foodCatalog.find(food => Number(food.id) === Number(item.foodId || item.id));
        console.log('匹配菜品:', { item, matchedFood });
        return {
          id: item.id || item.foodId || matchedFood?.id || index,
          foodId: item.foodId || item.id || matchedFood?.id || index,
          name: item.name || matchedFood?.name || `菜品${index + 1}`,
          price: Number(item.price ?? matchedFood?.price ?? 0),
          quantity: Number(item.quantity || 1),
          image: item.image || matchedFood?.img || '',
          description: item.description || matchedFood?.description || ''
        };
      });
      console.log('订餐卡片最终渲染数据:', this.aiOrderItems);

      this.deliveryAddress = order.deliveryAddress || uni.getStorageSync('userAddress') || '';
      this.deliveryPhone = order.deliveryPhone || uni.getStorageSync('userPhone') || '';
      this.orderRemark = order.remark || '';
      this.recommendSummary = order.recommendSummary || '';
      this.previewFromHistory = !!order.fromHistory;
      this.showOrderCard = this.aiOrderItems.length > 0;

      if (!this.showOrderCard) {
        uni.showToast({
          title: 'AI 未返回可确认餐品',
          icon: 'none'
        });
      }
    },

    hideOrderCard() {
      this.showOrderCard = false;
      this.aiOrderAmount = 0;
      this.recommendSummary = '';
      this.previewFromHistory = false;
    },

    async confirmFoodOrder() {
      try {
        uni.showLoading({
          title: '下单中...'
        });

        if (!this.aiOrderSessionId) {
          uni.hideLoading();
          uni.showToast({
            title: '订单会话失效，请重新生成',
            icon: 'none'
          });
          return;
        }

        const res = await this.$myRequest({
          url: '/user/agent/internal/confirm-food-order',
          method: 'POST',
          data: {
            sessionId: this.aiOrderSessionId
          }
        });

        uni.hideLoading();

        if (res.data.code === 200 && res.data.data) {
          uni.showToast({
            title: '下单成功',
            icon: 'success'
          });
          this.messages.push({
            role: 'assistant',
            content: '餐饮订单已提交成功，食堂会尽快为您制作并配送。'
          });
          this.aiOrderItems = [];
          this.aiOrderSessionId = '';
          this.hideOrderCard();
          this.$nextTick(() => {
            this.scrollIntoView = `msg-${this.messages.length - 1}`;
          });
        } else {
          uni.showToast({
            title: res.data.message || '下单失败',
            icon: 'none'
          });
        }
      } catch (error) {
        uni.hideLoading();
        console.error('AI订餐失败:', error);
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    }
  }
}
</script>

<style scoped>
.chat-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(95, 134, 255, 0.22), transparent 34%),
    radial-gradient(circle at 88% 12%, rgba(135, 196, 255, 0.28), transparent 24%),
    linear-gradient(180deg, #f5f8ff 0%, #eef4ff 48%, #e7f0ff 100%);
  position: relative;
  overflow: hidden;
}

.chat-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(24rpx);
  opacity: 0.9;
}

.orb-a {
  width: 340rpx;
  height: 340rpx;
  top: 70rpx;
  left: -110rpx;
  background: radial-gradient(circle, rgba(95, 134, 255, 0.28) 0%, rgba(95, 134, 255, 0) 72%);
}

.orb-b {
  width: 300rpx;
  height: 300rpx;
  right: -90rpx;
  top: 220rpx;
  background: radial-gradient(circle, rgba(112, 189, 255, 0.24) 0%, rgba(112, 189, 255, 0) 72%);
}

.grid-mask {
  position: absolute;
  inset: 0;
  opacity: 0.07;
  background-image:
    linear-gradient(rgba(95, 134, 255, 0.28) 1rpx, transparent 1rpx),
    linear-gradient(90deg, rgba(95, 134, 255, 0.28) 1rpx, transparent 1rpx);
  background-size: 44rpx 44rpx;
}

.chat-container {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 28rpx 24rpx calc(env(safe-area-inset-bottom) + 26rpx);
  box-sizing: border-box;
}

.hero-card {
  margin: 16rpx 6rpx 24rpx;
  padding: 38rpx 32rpx;
  border-radius: 32rpx;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.94) 0%, rgba(244, 248, 255, 0.98) 100%);
  border: 1rpx solid rgba(95, 134, 255, 0.12);
  box-shadow: 0 18rpx 46rpx rgba(95, 134, 255, 0.14);
  animation: cardEnter 0.8s ease;
}

.hero-badge {
  display: inline-flex;
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: rgba(95, 134, 255, 0.1);
  color: #5f86ff;
  font-size: 22rpx;
  letter-spacing: 2rpx;
  margin-bottom: 26rpx;
}

.hero-icon-wrap {
  width: 112rpx;
  height: 112rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #5f86ff 0%, #83b6ff 100%);
  box-shadow: 0 16rpx 32rpx rgba(95, 134, 255, 0.22);
  margin-bottom: 26rpx;
}

.hero-icon {
  color: #ffffff;
  font-size: 48rpx;
  font-weight: 700;
}

.hero-title {
  display: block;
  font-size: 46rpx;
  font-weight: 700;
  color: #29406f;
  letter-spacing: 1rpx;
}

.hero-desc {
  display: block;
  margin-top: 18rpx;
  color: #6f84a8;
  font-size: 27rpx;
  line-height: 1.7;
}

.feature-board {
  margin-top: 34rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.feature-card {
  padding: 24rpx 24rpx;
  border-radius: 24rpx;
  background: rgba(95, 134, 255, 0.04);
  border: 1rpx solid rgba(95, 134, 255, 0.08);
}

.feature-primary {
  background: linear-gradient(135deg, rgba(95, 134, 255, 0.14) 0%, rgba(131, 182, 255, 0.14) 100%);
}

.feature-label {
  display: block;
  color: #7d95bb;
  font-size: 22rpx;
  margin-bottom: 8rpx;
}

.feature-value {
  display: block;
  color: #355387;
  font-size: 28rpx;
  font-weight: 600;
}

.messages-scroll {
  flex: 1;
  min-height: 0;
  padding: 8rpx 6rpx 24rpx;
  box-sizing: border-box;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 16rpx;
  margin-bottom: 24rpx;
  animation: messageRise 0.35s ease;
}

.assistant-row {
  justify-content: flex-start;
}

.user-row {
  justify-content: flex-end;
}

.avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 12rpx 26rpx rgba(41, 64, 111, 0.12);
}

.assistant-avatar {
  background: linear-gradient(135deg, #5f86ff 0%, #83b6ff 100%);
}

.avatar-text {
  color: #ffffff;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
}

.message-column {
  display: flex;
  flex-direction: column;
  max-width: 78%;
}

.assistant-column {
  align-items: flex-start;
}

.user-column {
  align-items: flex-end;
}

.speaker-tag {
  font-size: 20rpx;
  color: #7a8fb3;
  margin: 0 10rpx 8rpx;
}

.message-bubble {
  padding: 22rpx 24rpx;
  border-radius: 26rpx;
  font-size: 28rpx;
  line-height: 1.7;
  word-break: break-all;
  box-shadow: 0 14rpx 34rpx rgba(41, 64, 111, 0.08);
}

.assistant-bubble {
  background: rgba(255, 255, 255, 0.92);
  color: #355387;
  border-top-left-radius: 10rpx;
}

.user-bubble {
  background: linear-gradient(135deg, #5f86ff 0%, #81afff 100%);
  color: #ffffff;
  border-top-right-radius: 10rpx;
}

.message-text {
  white-space: pre-wrap;
}

.chart-list {
  margin-top: 18rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.chart-card {
  width: 100%;
  padding: 14rpx;
  box-sizing: border-box;
  border-radius: 22rpx;
  background: rgba(95, 134, 255, 0.06);
  border: 1rpx solid rgba(95, 134, 255, 0.1);
}

.chart-image {
  width: 100%;
  border-radius: 18rpx;
  background: #ffffff;
  display: block;
}

.chart-title {
  display: block;
  margin-top: 12rpx;
  color: #60769d;
  font-size: 22rpx;
  line-height: 1.5;
  text-align: center;
}

.thinking-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin: 10rpx 0 24rpx;
}

.thinking-card {
  padding: 20rpx 24rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.86);
  border: 1rpx solid rgba(95, 134, 255, 0.1);
  box-shadow: 0 12rpx 28rpx rgba(95, 134, 255, 0.08);
}

.thinking-label {
  display: block;
  color: #5f6f8f;
  font-size: 24rpx;
  margin-bottom: 10rpx;
}

.thinking-dots {
  display: flex;
  gap: 8rpx;
}

.dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background: #6f94ff;
  animation: blink 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

.composer-shell {
  padding-top: 12rpx;
}

.composer-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 30rpx;
  padding: 22rpx;
  box-shadow: 0 18rpx 36rpx rgba(41, 64, 111, 0.1);
  border: 1rpx solid rgba(95, 134, 255, 0.1);
}

.composer-topline {
  margin-bottom: 16rpx;
}

.composer-hint {
  color: #7d92b8;
  font-size: 22rpx;
}

.input-box {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.input-field {
  flex: 1;
  height: 88rpx;
  background: rgba(95, 134, 255, 0.05);
  border-radius: 22rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #2b406d;
}

.send-btn {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  border: none;
  background: linear-gradient(135deg, #5f86ff 0%, #7bb0ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 14rpx 28rpx rgba(95, 134, 255, 0.24);
}

.send-btn::after {
  border: none;
}

.send-btn[disabled] {
  opacity: 0.55;
  box-shadow: none;
}

.send-icon {
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 700;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(9, 20, 42, 0.48);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 24rpx;
  z-index: 99;
}

.order-modal {
  width: 100%;
  max-height: 88vh;
  overflow-y: auto;
  border-radius: 34rpx;
  background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%);
  box-shadow: 0 -10rpx 40rpx rgba(34, 58, 120, 0.18);
  padding: 30rpx 28rpx 34rpx;
}

.modal-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.modal-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #28406d;
}

.modal-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #7d92b8;
}

.modal-close {
  width: 56rpx;
  height: 56rpx;
  border-radius: 18rpx;
  background: rgba(95, 134, 255, 0.08);
  color: #5f86ff;
  font-size: 38rpx;
  line-height: 56rpx;
  text-align: center;
  flex-shrink: 0;
}

.order-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18rpx;
  margin-bottom: 24rpx;
}

.overview-card {
  padding: 24rpx;
  border-radius: 24rpx;
  background: rgba(95, 134, 255, 0.06);
  border: 1rpx solid rgba(95, 134, 255, 0.08);
}

.total-card {
  background: linear-gradient(135deg, rgba(95, 134, 255, 0.14), rgba(123, 176, 255, 0.12));
}

.summary-banner {
  padding: 20rpx 22rpx;
  margin-bottom: 24rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, rgba(95, 134, 255, 0.08), rgba(123, 176, 255, 0.12));
  border: 1rpx solid rgba(95, 134, 255, 0.08);
}

.summary-label {
  display: block;
  font-size: 22rpx;
  color: #6d88b9;
  margin-bottom: 10rpx;
}

.summary-text {
  display: block;
  font-size: 26rpx;
  line-height: 1.7;
  color: #355387;
}

.overview-label {
  display: block;
  font-size: 22rpx;
  color: #7a8fb3;
}

.overview-value {
  display: block;
  margin-top: 12rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #29406f;
}

.overview-value.price {
  color: #2d64ff;
}

.modal-section {
  margin-bottom: 24rpx;
}

.section-caption {
  display: block;
  margin-bottom: 14rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #355387;
}

.modal-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.modal-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
  padding: 20rpx 22rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.88);
  border: 1rpx solid rgba(95, 134, 255, 0.08);
}

.modal-item-main {
  flex: 1;
  min-width: 0;
}

.modal-item-name {
  display: block;
  font-size: 28rpx;
  color: #29406f;
  font-weight: 600;
}

.modal-item-desc {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #8aa0c1;
}

.modal-item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6rpx;
}

.modal-item-count {
  font-size: 22rpx;
  color: #7d92b8;
}

.modal-item-price {
  font-size: 26rpx;
  font-weight: 700;
  color: #2d64ff;
}

.field-card {
  position: relative;
  padding: 10rpx 12rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.9);
  border: 1rpx solid rgba(95, 134, 255, 0.08);
  margin-bottom: 10rpx;
}

.compact-field-card {
  padding-bottom: 20rpx;
}

.field-label {
  display: block;
  margin-bottom: 4rpx;
  font-size: 22rpx;
  color: #7a8fb3;
}

.field-input,
.field-area {
  width: 100%;
  font-size: 28rpx;
  color: #29406f;
  line-height: 1.2;
}

.compact-textarea {
  height: 48rpx;
  min-height: 48rpx;
}

.address-field {
  height: 48rpx;
  min-height: 48rpx;
}

.field-area {
  min-height: 14rpx;
}

.remark-count {
  position: absolute;
  right: 14rpx;
  bottom: 10rpx;
  font-size: 20rpx;
  color: #95a9c8;
}

.modal-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18rpx;
  margin-top: 10rpx;
}

.modal-btn {
  height: 88rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 600;
}

.modal-btn.light {
  background: rgba(95, 134, 255, 0.08);
  color: #5f86ff;
}

.modal-btn.strong {
  background: linear-gradient(135deg, #5f86ff 0%, #7bb0ff 100%);
  color: #ffffff;
  box-shadow: 0 14rpx 30rpx rgba(95, 134, 255, 0.22);
}

@keyframes blink {
  0%,
  80%,
  100% {
    transform: scale(0.7);
    opacity: 0.45;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes messageRise {
  from {
    opacity: 0;
    transform: translateY(18rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(24rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
