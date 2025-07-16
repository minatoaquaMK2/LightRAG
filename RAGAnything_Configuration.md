# RAGAnything 独立配置指南

LightRAG Server 现在支持为 RAGAnything 多模态功能配置独立的模型设置，允许您为传统 RAG 操作和多模态处理使用不同的模型提供商和配置。

## 🔧 配置方式

### 环境变量配置

通过 `.env` 文件设置以下环境变量来配置 RAGAnything：

#### RAGAnything 专用配置项

```bash
# RAGAnything LLM 配置（如果未设置，将使用主 LLM 配置）
RAGANYTHING_LLM_BINDING=openai              # 模型提供商: openai, azure_openai, ollama, lollms
RAGANYTHING_LLM_MODEL=gpt-4o                # 模型名称
RAGANYTHING_LLM_BINDING_HOST=https://api.openai.com/v1  # API 端点
RAGANYTHING_LLM_BINDING_API_KEY=your_api_key            # API 密钥
RAGANYTHING_TEMPERATURE=0.7                 # 生成温度

# Azure OpenAI 专用配置（如果使用 azure_openai）
RAGANYTHING_AZURE_OPENAI_API_VERSION=2024-08-01-preview
RAGANYTHING_AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

## 📋 使用场景

### 场景 1: Ollama + OpenAI 混合配置

使用本地 Ollama 处理传统 RAG 任务，使用 OpenAI 处理多模态任务：

```bash
# 主 LLM 配置（传统 RAG）
LLM_BINDING=ollama
LLM_MODEL=mistral-nemo:latest
LLM_BINDING_HOST=http://localhost:11434

# RAGAnything 配置（多模态）
RAGANYTHING_LLM_BINDING=openai
RAGANYTHING_LLM_MODEL=gpt-4o
RAGANYTHING_LLM_BINDING_HOST=https://api.openai.com/v1
RAGANYTHING_LLM_BINDING_API_KEY=sk-your-openai-key
```

### 场景 2: 不同 OpenAI 模型配置

为不同任务使用不同的 OpenAI 模型：

```bash
# 主 LLM 配置（使用较便宜的模型）
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=sk-your-openai-key

# RAGAnything 配置（使用视觉能力更强的模型）
RAGANYTHING_LLM_BINDING=openai
RAGANYTHING_LLM_MODEL=gpt-4o
RAGANYTHING_LLM_BINDING_HOST=https://api.openai.com/v1
RAGANYTHING_LLM_BINDING_API_KEY=sk-your-openai-key
RAGANYTHING_TEMPERATURE=0.3
```

### 场景 3: Azure OpenAI 独立配置

```bash
# 主 LLM 配置
LLM_BINDING=ollama
LLM_MODEL=qwen2:latest
LLM_BINDING_HOST=http://localhost:11434

# RAGAnything 使用 Azure OpenAI
RAGANYTHING_LLM_BINDING=azure_openai
RAGANYTHING_LLM_MODEL=gpt-4o
RAGANYTHING_LLM_BINDING_HOST=https://your-resource.openai.azure.com
RAGANYTHING_LLM_BINDING_API_KEY=your-azure-api-key
RAGANYTHING_AZURE_OPENAI_API_VERSION=2024-08-01-preview
RAGANYTHING_AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

## 🚀 API 使用方式

### 多模态查询

```bash
curl -X POST "http://localhost:9621/raganything/multimodal/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "分析这个图表中的数据趋势",
    "mode": "hybrid"
  }'
```

### 多模态文档处理

```bash
curl -X POST "http://localhost:9621/raganything/multimodal/process-document" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.pdf",
    "output_dir": "./output"
  }'
```

### 文件上传并处理

```bash
curl -X POST "http://localhost:9621/raganything/multimodal/upload-and-process" \
  -F "file=@document.pdf" \
  -F "output_dir=./output"
```

## ⚙️ 配置优先级

1. **RAGAnything 专用配置** (`RAGANYTHING_*`) - 最高优先级
2. **主 LLM 配置** (`LLM_*`) - 回退配置
3. **系统默认值** - 最低优先级

## 🎯 功能特性

### 智能模型选择

- **视觉任务**：自动选择支持视觉的模型（如 gpt-4o）
- **文本任务**：使用配置的文本模型
- **回退机制**：非 OpenAI 绑定的视觉任务自动回退到 OpenAI

### 配置验证

- 自动验证模型视觉能力
- 配置错误时提供清晰的错误信息
- 支持配置热重载

## 📝 注意事项

1. **视觉能力**：只有支持视觉的模型（如 gpt-4o, gpt-4-turbo-vision）才能处理图像
2. **API 密钥**：确保为不同的服务提供商配置正确的 API 密钥
3. **成本控制**：合理选择模型以平衡功能和成本
4. **网络访问**：确保服务器能够访问配置的 API 端点

## 🔍 故障排除

### 常见问题

1. **视觉任务失败**：
   - 检查模型是否支持视觉
   - 验证 API 密钥是否正确
   - 确认网络连接

2. **配置不生效**：
   - 重启服务器以应用新配置
   - 检查环境变量格式是否正确
   - 查看服务器日志了解详细错误信息

3. **模型不匹配**：
   - 确保 RAGANYTHING_LLM_MODEL 存在于对应的服务中
   - 检查模型名称是否正确

## 📊 示例完整配置

创建 `.env` 文件：

```bash
# LightRAG Server Configuration
WEBUI_TITLE="LightRAG with RAGAnything"
WEBUI_DESCRIPTION="Multimodal RAG System"

# Main LLM (for traditional RAG)
LLM_BINDING=ollama
LLM_MODEL=mistral-nemo:latest
LLM_BINDING_HOST=http://localhost:11434

# RAGAnything (for multimodal tasks)
RAGANYTHING_LLM_BINDING=openai
RAGANYTHING_LLM_MODEL=gpt-4o
RAGANYTHING_LLM_BINDING_HOST=https://api.openai.com/v1
RAGANYTHING_LLM_BINDING_API_KEY=sk-your-key-here
RAGANYTHING_TEMPERATURE=0.7

# Embedding
EMBEDDING_BINDING=ollama
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024

# Server
HOST=0.0.0.0
PORT=9621
```

启动服务器：
```bash
lightrag-server
```

现在您可以享受灵活的多模态 RAG 配置了！🎉 