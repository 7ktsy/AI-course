# 图片转视频功能说明

## 功能概述

新增的图片转视频功能允许用户将AI生成的图片转换为动态视频，为写作场景提供更丰富的视觉体验。

## 后端接口

### 1. 图片转视频接口

**接口地址**: `POST /writing-assistant/image-url-to-video`

**请求参数**:
```json
{
  "prompt_text": "让这个场景动起来，添加一些动态元素",
  "image_url": "https://example.com/image.jpg",
  "ratio": "1280:720",
  "model": "gen4_turbo",
  "duration": 5
}
```

**参数说明**:
- `prompt_text`: 视频描述，说明希望生成的视频效果
- `image_url`: 源图片的URL地址
- `ratio`: 视频比例，支持 "1280:720"、"1024:1024"、"720:1280"
- `model`: 使用的模型，默认为 "gen4_turbo"
- `duration`: 视频时长（秒），范围1-10秒

**响应格式**:
```json
{
  "success": true,
  "video_url": "https://example.com/video.mp4",
  "created_at": "2024-01-01T12:00:00"
}
```

### 2. 健康检查接口

**接口地址**: `GET /writing-assistant/health`

**响应格式**:
```json
{
  "status": "healthy",
  "service": "writing_assistant"
}
```

## 前端功能

### 使用流程

1. **生成图片**: 在"写作场景模拟"标签页中输入作文内容，生成AI图片
2. **转视频**: 图片生成成功后，在结果区域会出现"将图片转换为动态视频"功能
3. **配置参数**: 
   - 输入视频描述（如："让画面动起来，添加一些动态元素"）
   - 选择视频比例
   - 设置视频时长
4. **生成视频**: 点击"生成视频"按钮开始转换
5. **查看结果**: 视频生成完成后可以预览和下载

### 功能特点

- **无缝集成**: 与现有的图片生成功能完美集成
- **参数可调**: 支持自定义视频比例和时长
- **错误处理**: 完善的错误提示和重试机制
- **下载支持**: 支持视频文件下载

## 技术实现

### 后端技术栈
- FastAPI: Web框架
- RunwayML API: AI视频生成服务
- Pydantic: 数据验证
- Requests: HTTP客户端

### 前端技术栈
- Vue 3: 前端框架
- Axios: HTTP客户端
- 响应式设计: 支持移动端

## 测试

运行测试脚本验证功能：

```bash
cd RAGBackend
python test_image_to_video.py
```

## 注意事项

1. **API密钥**: 确保RunwayML API密钥配置正确
2. **网络连接**: 视频生成需要稳定的网络连接
3. **处理时间**: 视频生成可能需要较长时间，请耐心等待
4. **文件大小**: 生成的视频文件可能较大，注意存储空间

## 错误处理

常见错误及解决方案：

- **401 Unauthorized**: 检查API密钥配置
- **500 Internal Server Error**: 检查服务器日志
- **Timeout**: 增加超时时间或检查网络连接
- **Invalid Image URL**: 确保图片URL可访问

## 更新日志

- **v1.0.0**: 初始版本，支持基本的图片转视频功能
- 支持多种视频比例
- 支持自定义视频时长
- 完善的错误处理和重试机制 