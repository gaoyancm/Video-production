# Video-production

Video-production 是一个帮助用户将文本、图片、视频等素材转化为视频生成提示词，并通过大模型或 ComfyUI 工作流完成视频生成的后端脚手架。

## 目录结构
- `backend/`：FastAPI 后端项目，包含 API、服务、配置与测试
- `docs/`：需求说明与技术文档
- `scripts/`：开发脚本（启动服务、运行测试等）

## 核心能力规划
- 上传多种素材并生成描述性提示词
- 支持调用 ChatGPT、Gemini、通义千问（DashScope）等大模型生成视频文案
- 将生成的 Prompt 推送给 ComfyUI 工作流执行
- 为后续扩展任务状态跟踪、生成结果下载等能力预留接口

## 快速开始
### 环境准备
- Python 3.10 及以上
- （可选）Node.js 18+ 用于未来前端

### 克隆仓库
```powershell
git clone https://github.com/gaoyancm/Video-production.git
cd Video-production
```

### 配置环境变量
1. 复制示例文件：
   ```powershell
   Copy-Item .env.example .env
   ```
2. 在 `.env` 中填写 API Key：
   - `OPENAI_API_KEY` / `DASHSCOPE_API_KEY` / `GEMINI_API_KEY` 分别对应三个大模型
   - `DEFAULT_*_MODEL` 控制未显式指定模型时的默认值
   - `COMFYUI_BASE_URL` 可留空，因为 ComfyUI 每次启动地址都可能变化，建议在请求参数中手动输入
   - `CORS_ORIGINS` 需要使用 JSON 数组字符串，例如：`["http://localhost:3000","http://127.0.0.1:3000"]`

### 安装依赖
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 启动后端
```powershell
./scripts/run-backend.ps1
```
启动成功后，访问 `http://127.0.0.1:8000/api/v1/health` 检查服务，`http://127.0.0.1:8000/docs` 可查看 Swagger 文档。

### 运行测试
```powershell
./scripts/run-tests.ps1
```

## API 概览
- `GET /api/v1/health`：健康检查
- `POST /api/v1/prompts/text`：调用所选大模型生成视频提示词，可选同步推送 ComfyUI
- `POST /api/v1/media/upload`：上传图片/视频素材，可选触发 ComfyUI 工作流

## 重要实现说明
- `backend/app/services/llm.py` 根据请求自动选择 OpenAI / DashScope / Gemini，使用真实 API 请求生成提示词
- `backend/app/services/comfyui.py` 需要在每次请求时传入最新的 ComfyUI 服务器地址（表单或 JSON 字段 `comfyui_endpoint`）
- `.env` 中的密钥不会提交到仓库，请妥善保管

## 下一步建议
1. 扩展服务层，补充更多模型参数与错误处理
2. 构建前端界面，实现素材上传、模型选择与结果展示
3. 引入任务队列或数据库，追踪生成任务和下载链接
4. 加入鉴权、速率限制与日志监控，提升安全与可运维性
