# 重要修复：动态服务器地址支持

## 问题描述

在之前的版本中，所有内部 API 调用都硬编码为 `127.0.0.1:8188`，这导致在以下场景中会出现连接错误：

1. **远程访问**：当通过局域网 IP（如 `192.168.100.170:4020`）访问时
2. **自定义端口**：使用非默认端口时
3. **反向代理**：通过 Nginx 等反向代理访问时

### 错误示例

```json
{
  "error": "Failed to submit workflow: [<class 'aiohttp.client_exceptions.ClientConnectorError'>] Cannot connect to host 127.0.0.1:8188 ssl:default [Connect call failed ('127.0.0.1', 8188)]"
}
```

## 解决方案

### 核心改进

添加了 `_get_internal_api_url(request)` 函数，从请求的 `Host` 头部动态获取服务器地址和端口：

```python
def _get_internal_api_url(request):
    """
    Get internal API base URL for ComfyUI API calls.
    Uses the same host and port from the incoming request to avoid hardcoding.
    
    Returns:
        Internal API base URL string (e.g., "http://192.168.100.170:4020")
    """
    # Default to localhost
    internal_url = "http://127.0.0.1:8188"
    
    if request:
        host = request.headers.get('Host')
        if host:
            # For internal API calls, always use http (not https)
            # as we're calling the same server
            internal_url = f"http://{host}"
    
    return internal_url
```

### 修改的函数

以下所有函数都已更新，添加了 `request` 参数并使用动态 URL：

1. **_apply_params_to_workflow** - 处理工作流参数
2. **_process_node_params** - 处理节点参数
3. **_process_param_marker** - 处理参数标记
4. **_handle_media_upload** - 处理媒体上传
5. **_upload_media_from_source** - 从 URL 上传媒体
6. **_upload_media** - 上传媒体文件
7. **_queue_prompt** - 提交工作流到队列
8. **_wait_for_results** - 等待执行结果

### 具体修改点

#### 1. 上传媒体（Upload Image）

**修改前：**
```python
async with session.post("http://127.0.0.1:8188/upload/image", data=data):
```

**修改后：**
```python
internal_url = _get_internal_api_url(request)
async with session.post(f"{internal_url}/upload/image", data=data):
```

#### 2. 提交任务（Queue Prompt）

**修改前：**
```python
async with session.post("http://127.0.0.1:8188/prompt", data=json_data):
```

**修改后：**
```python
internal_url = _get_internal_api_url(request)
async with session.post(f"{internal_url}/prompt", data=json_data):
```

#### 3. 查询历史（Get History）

**修改前：**
```python
async with session.get(f"http://127.0.0.1:8188/history/{prompt_id}"):
```

**修改后：**
```python
internal_url = _get_internal_api_url(request)
async with session.get(f"{internal_url}/history/{prompt_id}"):
```

## 工作原理

### 地址获取流程

1. 客户端发送请求到 `http://192.168.100.170:4020/oneapi/v1/execute`
2. 服务器从 `request.headers.get('Host')` 获取 `192.168.100.170:4020`
3. 所有内部 API 调用使用 `http://192.168.100.170:4020` 作为基础 URL
4. 成功连接到正确的服务器地址

### 兼容性

- ✅ **本地访问**：`http://127.0.0.1:8188` → 使用 `127.0.0.1:8188`
- ✅ **局域网访问**：`http://192.168.100.170:4020` → 使用 `192.168.100.170:4020`
- ✅ **自定义端口**：`http://localhost:9999` → 使用 `localhost:9999`
- ✅ **反向代理**：`http://proxy.example.com` → 使用代理地址

## 测试验证

### 测试场景 1：本地访问

```bash
curl -X POST "http://127.0.0.1:8188/oneapi/v1/execute" \
  -H "Content-Type: application/json" \
  -d '{"workflow": "test.json"}'
```

**结果**：✅ 正常工作，使用 `127.0.0.1:8188`

### 测试场景 2：局域网访问

```bash
curl -X POST "http://192.168.100.170:4020/oneapi/v1/execute" \
  -H "Content-Type: application/json" \
  -d '{"workflow": "test.json"}'
```

**结果**：✅ 正常工作，使用 `192.168.100.170:4020`

### 测试场景 3：Swagger UI 测试

在浏览器中访问 `http://192.168.100.170:4020/oneapi/docs`，通过 Swagger UI 测试 API。

**结果**：✅ 正常工作，所有请求使用正确的服务器地址

## 注意事项

### HTTP vs HTTPS

内部 API 调用始终使用 `http://`，即使客户端使用 `https://` 访问。这是因为内部调用是服务器自己调用自己，不需要经过 SSL/TLS。

如果使用反向代理（如 Nginx）：
- 客户端 → Nginx：`https://example.com`
- Nginx → ComfyUI：`http://localhost:8188`
- ComfyUI 内部调用：`http://localhost:8188`

### 默认回退

如果无法从 `request` 对象获取 `Host` 信息，系统会回退到默认值 `http://127.0.0.1:8188`，确保向后兼容性。

## 相关文件

- `oneapi.py` - 主要修改文件
- `CHANGELOG.md` - 更新日志
- `README.md` - 使用说明

## 更新时间

2026-02-07 - v1.1.1
