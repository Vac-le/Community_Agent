# 智慧社区便民服务平台 · Community_Agent

> 面向社区居民的智慧便民服务平台，以 **Community_Agent** 多 Agent AI 引擎为核心，整合微信小程序、管理后台、Java 业务后端与 Python 智能体服务，提供社区公告、餐饮配送、家政上门、代购服务、订单管理与 AI 智能问答等能力。

---

## 1. 项目简介

本项目是一个围绕社区生活场景构建的智慧便民服务平台，解决社区服务入口分散、业务协同低效、知识问答不准确和智能服务能力不足的问题，通过 **Community_Agent + 小程序 + 管理后台 + 双后端服务** 的组合，形成从居民使用、后台运营到 AI 智能服务的一体化闭环。

---

## 2. 核心功能

### 2.1 Community_Agent 智能体核心能力

#### 1）多 Agent 协同工作流

- **Supervisor 调度中心**：负责识别用户意图、规划执行路径、分发任务到不同子 Agent
- **领域子 Agent**：覆盖知识问答、订餐协助、天气查询、报表分析等场景
- **复杂问题拆解执行**：支持将一个复杂请求拆成多个子任务逐步处理
- **共享状态协同**：子 Agent 可复用中间结果，减少重复调用，提高响应效率

#### 2）三层记忆架构

Community_Agent 采用分层记忆设计，不把所有信息都直接堆入一次提示词，而是按照“当前正在处理什么”“本次会话此前聊过什么”“这个用户长期偏好和稳定事实是什么”进行分层管理，从而在回答质量、上下文长度控制与长期可用性之间取得平衡。

- **第一层：当前上下文窗口**
  - 存放当前轮推理最相关的信息，如用户最新问题、系统提示、当前工具返回结果、最近几轮关键消息
  - 直接参与本轮生成，是模型实时决策的核心输入层
  - 通过滑动窗口机制控制长度，避免上下文无限增长
- **第二层：历史对话记忆**
  - 保存当前会话中的阶段性历史消息，用于维持多轮对话连贯性
  - 当用户连续追问“刚才那个订单”“上一次推荐的服务”“继续刚才的话题”时，可恢复会话状态
  - 对过长历史进行摘要压缩，只保留关键事实、任务进度、待确认项和重要结论
- **第三层：用户长期记忆**
  - 记录跨会话仍有价值的用户画像与稳定偏好，例如常用社区、服务偏好、长期关注主题、历史确认过的事实信息
  - 不依赖单次会话生命周期，可跨天、跨会话复用
  - 用于减少重复询问，让 Agent 更快建立用户背景理解

**三层协同方式：**

- 本轮回答优先依赖**当前上下文窗口**，保证实时性与准确性
- 需要延续多轮语义时，回溯**历史对话记忆**，保证上下文连贯
- 需要补充用户稳定偏好和长期画像时，再按需注入**用户长期记忆**
- 通过“当前窗口优先、历史摘要补充、长期记忆按需加载”的策略，在效果与 Token 成本之间取得平衡

#### 3）长上下文自动降级与重试

- 支持轻量级 Token 估算
- 当上下文达到 **80% 阈值** 时，提前触发压缩
- 支持 **最多 3 级梯度重试**
- 结合滑动窗口与摘要压缩策略，降低上下文过长导致的报错
- 长对话场景失败率降低约 **60%**

#### 4）Reflection 回答自检

- 对最终回答进行一致性校验
- 校验工具调用是否真实成功
- 识别“未调用工具却声称已完成”“结果与用户问题不一致”等问题
- 出现异常时自动重试，降低大模型幻觉风险

#### 5）混合检索与重排序

- 支持 **向量检索 + BM25 关键词检索** 的双路召回
- 使用 **RRF（Reciprocal Rank Fusion）** 做融合排序
- 接入 **Rerank 模型** 做二次精排
- 面向社区知识库场景，召回率约 **92%**

### 2.2 微信小程序端 `Community_MiniApp`

面向社区居民的移动端入口，提供常用便民服务与 AI 助手交互能力。

**已包含页面/功能：**

- 首页入口
- 用户登录、注册
- 人脸识别登录/校验
- 用户信息页
- AI 助手会话页
- 餐饮服务与餐饮配送
- 家政服务与家政上门
- 代购服务与代购配送
- 用户中心
- 餐饮订单、家政订单、代购订单查询

**适用场景：**

- 居民在线浏览社区服务
- 提交餐饮、代购、家政类需求
- 查看个人订单与服务进度
- 通过 AI 助手咨询社区业务、天气、服务流程等问题

### 2.3 管理后台 `Community_Admin`

面向社区运营人员与管理员的 Web 管理端，用于统一管理社区内容、商品、订单、用户与 AI 交互数据。

**已包含模块：**

- 管理员登录
- 首页主控台
- 社区信息管理
- 社区数据统计
- 用户管理
- 公告管理
- 活动管理
- 餐饮商品管理
- 家政服务管理
- 代购商品管理
- 餐饮订单管理
- 家政订单管理
- 代购订单管理
- 配送信息管理
- 操作日志管理
- AI 对话页面

**价值：**

- 统一运营入口，降低多系统切换成本
- 后台可维护社区公告、活动、服务内容
- 可跟踪居民订单与配送情况
- 为 AI 能力提供运营管理与人工兜底支撑

### 2.4 用户业务后端 `CommunityService`

面向小程序提供业务接口，是居民侧服务的主要网关。

**承担职责：**

- 用户登录态与基础用户信息处理
- 对接订单业务与服务流程
- 提供餐饮、家政、代购等业务接口
- 对接 Redis 缓存
- 向 Python Agent 转发 AI 流式请求
- 维护 AI 会话上下文与操作日志

**典型链路：**

- 小程序发起 AI 会话
- `CommunityService` 校验登录状态与业务上下文
- 转发至 `Community_Agent`
- 以 SSE/流式方式返回前端

### 2.5 管理业务后端 `CommunityMange`

面向后台管理系统提供接口，负责管理员端业务与社区运营能力。

**承担职责：**

- 管理员登录与权限处理
- 用户管理、社区信息管理
- 商品与服务管理
- 订单管理
- 天气服务接口
- 邮件/通知相关处理
- 调用 Python Agent 提供后台 AI 能力
- 运营日志与审计能力支撑

### 2.6 平台整体能力总览

| 模块 | 技术栈 | 主要职责 | 默认端口 |
|---|---|---|---|
| `Community_Agent` | FastAPI + LangGraph + LangChain | AI 对话、RAG 检索、多 Agent 编排 | `9000` |
| `CommunityService` | Spring Boot + MyBatis + Redis + MySQL | 小程序业务接口、订单、AI 转发 | `8088` |
| `CommunityMange` | Spring Boot + MyBatis + Redis + MySQL | 管理后台接口、社区运营管理 | `8089` |
| `Community_Admin` | Vue 2 + Element UI + Axios + ECharts | 后台管理界面 | 前端开发端口由 Vue CLI 分配 |
| `Community_MiniApp` | uni-app / Vue | 微信小程序用户端 | 微信开发者工具运行 |

---

## 3. 环境依赖

### 3.1 基础环境

| 类别 | 要求 |
|---|---|
| 操作系统 | Windows / Linux / macOS |
| Python | 3.10 及以上 |
| JDK | 8 及以上 |
| Maven | 3.6 及以上 |
| Node.js | 14 及以上 |
| npm | 6 及以上 |
| MySQL | 5.7 及以上 |
| Redis | 5.0 及以上 |
| 微信开发者工具 | 最新稳定版 |

### 3.2 Python 侧依赖（Community_Agent）

`requirements.txt` 当前包含：

```txt
jieba>=0.42.1
rank-bm25>=0.2.2
langchain>=0.3.0
langgraph>=0.2.0
langchain-openai>=0.2.0
langchain-milvus>=0.1.7
pymilvus[milvus_lite]>=2.6.15
redis>=5.0.0
```

实际运行建议额外安装：

```bash
pip install fastapi uvicorn pydantic pyyaml dashscope langchain-community httpx
```

### 3.3 管理后台依赖（Community_Admin）

主要依赖如下：

- `vue@2.6.10`
- `vue-router@3.5.3`
- `element-ui@2.15.14`
- `axios@1.9.0`
- `echarts@6.0.0`
- `mavon-editor@2.10.4`
- `showdown@2.1.0`

### 3.4 外部服务依赖

| 服务 | 用途 | 配置方式 |
|---|---|---|
| MIMO / OpenAI 兼容接口 | 大模型对话 | 环境变量 |
| DashScope | Embedding / Rerank / 图表相关能力 | 环境变量 |
| MySQL | 业务数据存储 | `application.yml` |
| Redis | 缓存、会话、记忆 | `application.yml` |
| SMTP 邮件服务 | 邮件通知 | `application.yml` |
| 阿里云 OSS | 图片/文件资源存储 | `application.yml` |

---

## 4. 快速安装

> 以下步骤适用于本地开发环境。启动前请先准备好 MySQL、Redis、Python、JDK、Maven、Node.js 和微信开发者工具。

### 4.1 克隆项目

```bash
git clone <your-repo-url>
cd 新社区项目
```

### 4.2 导入数据库

```bash
mysql -u root -p < data.sql
```

如果你使用的是自建数据库，请将 `CommunityService` 与 `CommunityMange` 中的 `application.yml` 修改为你自己的数据库地址、账号和密码。

### 4.3 启动 Redis

```bash
redis-server
```

### 4.4 启动 Community_Agent

```bash
cd Community_Agent
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

Linux / macOS：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
pip install fastapi uvicorn pydantic pyyaml dashscope langchain-community httpx
```

配置环境变量：

```bash
set MIMO_API_KEY=your_mimo_key
set DASHSCOPE_API_KEY=your_dashscope_key
```

Linux / macOS：

```bash
export MIMO_API_KEY=your_mimo_key
export DASHSCOPE_API_KEY=your_dashscope_key
```

启动服务：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 9000
```

### 4.5 启动用户业务后端 CommunityService

```bash
cd ../CommunityService
mvn spring-boot:run
```

### 4.6 启动管理业务后端 CommunityMange

```bash
cd ../CommunityMange
mvn spring-boot:run
```

### 4.7 启动管理后台 Community_Admin

```bash
cd ../Community_Admin
npm install
npm run serve
```

### 4.8 启动微信小程序 Community_MiniApp

```bash
# 使用微信开发者工具打开 Community_MiniApp 目录
```

小程序运行前请确认：

- `main.js` 中接口地址指向 `CommunityService`
- 小程序已配置合法请求域名或本地开发代理
- 微信开发者工具已启用对应项目配置

---

## 5. 使用示例

### 5.1 启动 AI 服务

```bash
cd Community_Agent
uvicorn main:app --reload --host 0.0.0.0 --port 9000
```

### 5.2 健康检查

```bash
curl http://127.0.0.1:9000/health
```

### 5.3 直接调用 Agent 流式对话接口

```bash
curl -N -X POST http://127.0.0.1:9000/agent/chat/stream \
  -H "Content-Type: application/json" \
  -H "token: <用户JWT>" \
  -d '{
    "userId": 1,
    "communityId": 1,
    "sessionId": "session-001",
    "currentMessage": "今天社区餐饮服务有什么可选内容？",
    "chatHistory": []
  }'
```

### 5.4 小程序到 Agent 的调用链路

```text
Community_MiniApp
  -> CommunityService:8088
  -> Community_Agent:9000
  -> 流式返回 AI 回复
```

### 5.5 Java 后端对接示例说明

用户端后端中已包含 Agent 对接相关模型与服务，例如：

- `com.agent.client.AgentClient`
- `com.agent.client.AgentStreamClient`
- `com.agent.service.AgentService`
- `com.agent.controller.AgentController`
- `com.agent.controller.AgentBizController`

管理端后端中已包含：

- `com.service.AgentChatService`
- `com.web.ChatAgentController`
- `com.web.ChatAgentInternalController`

### 5.6 RAG 召回评测

```bash
cd Community_Agent
python retrieval_eval/run_eval.py
```

---

## 6. 配置说明

### 6.1 Community_Agent 环境变量

| 变量名 | 是否必填 | 说明 |
|---|---|---|
| `MIMO_API_KEY` | 是 | 大模型对话 API Key |
| `DASHSCOPE_API_KEY` | 是 | Embedding / Rerank / 图表能力 API Key |
| `OPENAI_BASE_URL_MIMO` | 否 | MIMO/OpenAI 兼容接口地址 |
| `LANGSMITH_API_KEY` | 否 | 链路观测与调试 |

### 6.2 `Community_Agent/config/agent.yml`

| 参数 | 说明 |
|---|---|
| `chat_model_name` | 主对话模型名称 |
| `embedding_model_name` | 向量模型名称 |
| `memory.user_long_memory` | 用户长期记忆配置 |
| `memory.short_history` | 短期上下文配置 |
| `reflection.enabled` | 是否启用回答自检 |
| `reflection.max_retry` | 自检失败最大重试次数 |

### 6.3 Agent 三层记忆说明

Community_Agent 的记忆能力可理解为三个层次协同工作：

| 记忆层 | 作用 | 典型内容 | 特点 |
|---|---|---|---|
| 当前上下文窗口 | 支撑本轮实时推理 | 当前问题、最近几轮消息、工具结果、系统提示 | 响应最快、最实时，但长度受限 |
| 历史对话记忆 | 保持当前会话连续性 | 本次会话中已讨论的主题、任务状态、阶段性结论 | 支持多轮追问，可被摘要压缩 |
| 用户长期记忆 | 保存跨会话稳定信息 | 偏好、画像、习惯、长期关注点、确认过的事实 | 可跨会话复用，减少重复询问 |

**设计目标：**

- 不让模型只依赖短期聊天记录
- 不把全部历史消息都塞进当前 Prompt
- 在长会话中仍保持连贯与可控
- 让 AI 助手具备一定“记住用户”的持续服务能力

### 6.4 `Community_Agent/config/rag.yml`

| 参数 | 说明 |
|---|---|
| `retrieval.top_k` | 初始召回数量 |
| `retrieval.final_k` | 最终返回文档数量 |
| `retrieval.rrf_k` | RRF 融合参数 |
| `rerank.model_name` | 重排模型名称 |
| `retry.trigger_ratio` | 上下文压缩触发阈值，默认 `0.8` |
| `retry.max_retry` | 最大重试次数，默认 `3` |
| `retry.max_context_tokens` | 上下文 Token 上限 |

### 6.5 `Community_Agent/config/vector_store.yml`

| 参数 | 说明 |
|---|---|
| `store.collection_name` | 向量集合名称 |
| `store.data_path` | 知识库文档目录 |
| `chunking.chunk_size` | 文档分块大小 |

### 6.6 `CommunityService/src/main/resources/application.yml`

主要配置项包括：

- 服务端口：`8088`
- MySQL 数据源
- Redis 连接信息
- 邮件服务 SMTP 配置
- OSS 配置
- 后台管理服务地址 `admin.api.url`
- Python Agent 地址 `agent.api.url`
- 流式聊天路径 `agent.api.stream-chat-path`
- 上下文缓存时间 `agent.context.ttl-hours`

### 6.7 `CommunityMange/src/main/resources/application.yml`

主要配置项包括：

- 服务端口：`8089`
- MySQL 数据源
- Redis 连接信息
- 邮件服务配置
- OSS 配置
- Python Agent 地址 `agent.python.base-url`

### 6.8 小程序端配置

建议重点检查以下内容：

- 接口基础地址配置
- 登录态 Token 传递
- AI 流式请求配置
- 微信开发者工具本地调试设置

### 6.9 管理后台配置

`Community_Admin/package.json` 中使用了 Vue CLI，本地启动命令：

```bash
npm run serve
```

当前脚本已兼容部分 Node/OpenSSL 问题：

```bash
set NODE_OPTIONS=--openssl-legacy-provider && vue-cli-service serve
```

---

## 7. 项目目录结构

```text
新社区项目/
├── README.md
├── data.sql                         # 数据库初始化脚本
├── Community_Agent/                 # AI 智能体核心服务
│   ├── main.py                      # FastAPI 入口
│   ├── agent/
│   │   ├── api/                     # 对外接口层
│   │   ├── graph/                   # Supervisor 与多 Agent 编排
│   │   ├── service/                 # 对话服务层
│   │   ├── tools/                   # 业务工具
│   │   └── reflection_service.py    # 回答自检
│   ├── rag/                         # 检索增强模块
│   ├── memory/                      # 用户长期记忆
│   ├── config/                      # agent/rag/vector_store 等配置
│   ├── prompts/                     # 各类 Prompt 模板
│   ├── utils/                       # 上下文压缩、重试、配置等工具
│   ├── models/                      # DTO 与模型工厂
│   ├── retrieval_eval/              # RAG 评测脚本
│   ├── data/                        # 知识库文档
│   └── requirements.txt             # Python 依赖
├── Community_MiniApp/               # 微信小程序端
│   ├── pages/                       # 页面目录
│   ├── utils/                       # 请求封装、流式请求等
│   ├── static/                      # 静态资源
│   ├── pages.json                   # 页面路由配置
│   ├── main.js                      # 小程序入口
│   └── App.vue
├── Community_Admin/                 # Web 管理后台前端
│   ├── src/
│   │   ├── views/                   # 各业务页面
│   │   ├── router/                  # 路由配置
│   │   ├── assets/                  # 样式与静态资源
│   │   └── main.js                  # 前端入口
│   ├── package.json                 # 前端依赖与脚本
│   └── vue.config.js
├── CommunityService/                # 小程序业务后端
│   ├── src/main/java/com/
│   │   ├── agent/                   # Agent 对接能力
│   │   ├── service/                 # 业务服务层
│   │   ├── web/                     # 控制器层
│   │   ├── util/                    # 工具类
│   │   └── model/                   # 数据模型
│   ├── src/main/resources/
│   │   ├── application.yml          # 系统配置
│   │   └── mappers/                 # MyBatis 映射
│   └── pom.xml
└── CommunityMange/                  # 管理后台后端
    ├── src/main/java/com/
    │   ├── web/                     # 管理端控制器
    │   ├── service/                 # 管理业务服务
    │   ├── dao/                     # 数据访问层
    │   ├── config/                  # 跨域、Redis、Knife4j 等配置
    │   ├── interceptor/             # Token 拦截器
    │   ├── aop/                     # 日志切面
    │   ├── util/                    # JWT、天气、上传等工具
    │   └── model/                   # 管理端数据模型
    ├── src/main/resources/
    │   ├── application.yml
    │   └── mappers/
    └── pom.xml
```

---

## 8. 常见问题 FAQ

### Q1：README 里为什么以 Community_Agent 为核心？

A：因为该项目的智能能力、知识问答、对话编排、工具调用、RAG 检索等核心创新点集中在 `Community_Agent`，它是整个系统区别于普通社区管理系统的关键模块。

### Q2：项目是否只包含 AI，对传统业务支持完整吗？

A：不是。项目同时包含小程序端、后台管理端、用户业务后端、管理业务后端、数据库脚本以及完整的订单和社区运营功能，AI 只是核心增强能力之一。

### Q3：小程序端目前支持哪些服务？

A：从现有页面结构看，已包含登录注册、人脸识别、AI 助手、餐饮服务、家政服务、代购服务以及对应订单查询能力。

### Q4：管理后台可以做什么？

A：可用于管理社区信息、公告、活动、用户、餐饮商品、家政服务、代购商品、订单、配送信息、操作日志，并支持 AI 对话页面。

### Q5：为什么我启动后 AI 接口无响应？

A：请依次检查：

1. `Community_Agent` 是否已运行在 `9000` 端口
2. `CommunityService` 或 `CommunityMange` 中的 Agent 地址是否配置正确
3. `MIMO_API_KEY` 与 `DASHSCOPE_API_KEY` 是否已设置
4. Redis 是否正常启动
5. 前端请求是否携带正确 Token

### Q6：知识库问答不准确怎么办？

A：建议检查以下几点：

- `Community_Agent/data/` 中的文档是否完整
- 向量库是否成功构建
- `rag.yml` 中 `top_k`、`final_k`、`rerank` 参数是否合理
- 是否执行过 `retrieval_eval/run_eval.py` 做效果验证

### Q7：长对话报错或回答被截断怎么办？

A：系统已内置 80% 阈值压缩和 3 级重试机制。如果仍有问题，可尝试：

- 缩短历史消息长度
- 调整上下文上限
- 降低短期记忆保留条数
- 暂时关闭部分高消耗工具调用链路

### Q8：管理后台 `npm run serve` 失败怎么办？

A：当前脚本已加入 `NODE_OPTIONS=--openssl-legacy-provider`。如果仍失败，优先确认 Node.js 版本是否兼容，建议使用 Node 14/16 LTS。

### Q9：数据库配置中的旧库名与当前项目名称不一致怎么办？

A：这是历史配置遗留问题，不影响 README 对项目定位的修正。你可以把两个后端 `application.yml` 中的数据库名、连接地址、邮箱、OSS 等配置替换为自己的开发环境配置。

### Q10：项目适合部署到哪里？

A：推荐按以下方式拆分部署：

- `Community_Agent`：Linux 服务器 / 容器
- `CommunityService`、`CommunityMange`：Java 应用服务器
- `MySQL`、`Redis`：独立基础服务
- `Community_Admin`：Nginx 静态部署
- `Community_MiniApp`：微信小程序发布

---

## License

本项目更适合作为学习、课程设计、功能演示与二次开发基础使用；若用于生产或商业环境，请先完成配置清理、安全加固与合规检查。
