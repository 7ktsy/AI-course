import base64
from PIL import Image
import io

def image_to_base64(image_path: str, max_size: tuple = (800, 800)) -> str:
    """
    将图片转换为base64编码，会先压缩图片以确保不超过大小
    Args:
        image_path (str): 图片文件路径
        max_size (tuple): 最大尺寸 (宽, 高)
    Returns:
        str: base64编码的图片数据，包含MIME类型前缀
    """
    try:
        # 打开并压缩图片
        with Image.open(image_path) as img:
            # 转换为RGB模式（去除透明通道）
            if img.mode in ('RGBA', 'LA'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整图片大小
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存到内存中
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=70)  # 使用JPEG格式和较低的质量来减小大小
            img_data = buffer.getvalue()
            
            # 转换为base64
            base64_data = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_data}"
            
    except Exception as e:
        raise Exception(f"图片转换失败: {str(e)}")

if __name__ == "__main__":
    # 测试代码
    test_image_path = "C:/Users/SevenPills/Pictures/壁纸.jpg"
    result = image_to_base64(test_image_path)
    print(f"Base64字符串长度: {len(result)}")
    print("Base64字符串前100个字符: " + result[:100] + "...")
