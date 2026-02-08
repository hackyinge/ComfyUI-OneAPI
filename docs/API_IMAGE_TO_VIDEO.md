# 🎬 Image-to-Video API 指南 (OpenAI 兼容模式)

本插件提供了一个强大的 **图生视频 (I2V)** 接口，完全兼容 OpenAI 的 `/v1/chat/completions` 格式。这使得您可以像调用 ChatGPT 一样调用 ComfyUI 的视频生成工作流。

---

## 🚀 核心特性

- **OpenAI 协议对齐**：使用标准的 `/v1/chat/completions` 路径和 `messages` 结构。
- **灵活的数据输入**：支持 Base64 编码的内联图片数据或远程图片 URL。
- **智能工作流路由**：通过 `model` 参数智能选择横屏 (`ltx2_landscape`) 或竖屏 (`ltx2_portrait`) 工作流，自动适配 16:9 或 9:16 分辨率。
- **生成直链返回**：生成的视频链接将直接包含在助理的回答内容中。

---

## 📡 API 路由

- `POST /v1/chat/completions`

---

## 🛠 请求格式

请求体应遵循 OpenAI Chat Completion 规范。推荐使用多模态格式（Vision）来传递图片。

### 请求示例 (Python/cURL 风格)

```json
{
  "model": "ltx2_landscape", 
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "镜头从幼年吴小凡恐惧的视角开始..."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
          }
        }
      ]
    }
  ]
}
```

> **提示**: `model` 参数直接对应 `workflows/` 目录下的 `.json` 文件名称。
> - 使用 `ltx2_landscape` 将触发横屏 (16:9) 生成逻辑。
> - 使用 `ltx2_portrait` 将触发竖屏 (9:16) 生成逻辑。

---

## 📦 响应格式

插件返回符合 OpenAI 标准的 `chat.completion` 对象。

```json
{
  "id": "chatcmpl-923...",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "ltx2_landscape",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Successfully generated video for: 镜头从幼年吴小凡...\n\nGenerated Video URL: http://your-server:6006/view?filename=LTX-2_00001.mp4&type=output"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

---

## ⚙️ 工作流配置要求

如果您想使用自定义的图生视频工作流，请确保满足以下条件：

1. **命名节点标题**：
   - `LoadImage` 节点的标题必须设置为 `$param.image`。
   - 文本编码节点设置为 `$param.text`。
   - 随机种子节点设置为 `$param.seed`（可选）。
   - 最终视频输出节点设置为 `$output.video`。

2. **放置位置**：
   将 JSON 格式的工作流文件放入 `workflows/` 目录下，文件名为模型 ID。

---

## 🧪 测试脚本

您可以使用项目自带的 `tests/test_i2v.py` 进行测试：

```bash
# 测试 Base64 输入
python tests/test_i2v.py base64 test.png "a cute cat"

# 测试 URL 输入
python tests/test_i2v.py url https://example.com/img.jpg "a flying dragon"
```

---

*“让视频生成像聊天一样简单。”*
