import os
import cv2
import re
import shutil
from moviepy import VideoFileClip
import whisper # 语音识别
from paddleocr import PaddleOCR
import numpy as np

# 使用更简单的输出目录
output_base_dir = "D:/my_project/softwareDemo/file/Linux"

# 初始化PaddleOCR模型（全局变量）
ocr = PaddleOCR(use_angle_cls=True, lang='ch') 

# 1. 提取视频帧
def extract_frames(video_path, interval_sec=10):
    # 获取视频文件名（不含扩展名）
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    
    # 直接保存到目标目录
    target_dir = os.path.join(output_base_dir, f"{video_name}_frames")
    print(f"视频路径: {video_path}")
    print(f"目标目录: {target_dir}")
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"创建目标目录成功: {target_dir}")
    except Exception as e:
        print(f"创建目标目录失败: {str(e)}")
        return None, 0
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("错误：无法打开视频文件")
        return None, 0
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval_sec)
    frame_count = 0
    saved_count = 0
    
    print(f"正在提取视频帧...")
    print(f"视频FPS: {fps}, 提取间隔: {interval_sec}秒")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frame_filename = f"frame_{frame_count:06d}.jpg"
            frame_path = os.path.join(target_dir, frame_filename)
            try:
                success = cv2.imwrite(frame_path, frame)
                if success:
                    print(f"已保存: {frame_filename}")
                    saved_count += 1
                else:
                    print(f"保存失败: {frame_filename}")
            except Exception as e:
                print(f"保存出错 {frame_filename}: {str(e)}")
        frame_count += 1
    cap.release()
    
    print(f"总共提取了 {frame_count} 帧，保存了 {saved_count} 张图片")
    return target_dir, frame_count

def ocr_frames_optimized(frame_dir, save_text=True):
    """优化后的OCR识别函数（逐张 predict，避免接口过时）"""
    
    image_files = [f for f in os.listdir(frame_dir)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    results = []

    for img_file in image_files:
        img_path = os.path.join(frame_dir, img_file)
        try:
            # 推荐接口：predict()
            result = ocr.predict(img_path, det=True, rec=True, cls=True)

            if result and len(result[0]) > 0:
                texts = [line[1][0] for line in result[0]]
                results.append((img_file, texts))
        except Exception as e:
            print(f"{img_file} 识别失败: {e}")
    
    # 保存文本结果
    if save_text:
        text_file = os.path.join(frame_dir, "ocr_results_optimized.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            for img_file, texts in results:
                f.write(f"{img_file}:\n")
                f.write("\n".join(f"  - {text}" for text in texts))
                f.write("\n" + "-"*30 + "\n")

    return results

#3. 语音识别
def speech_recognition(video_path, output_dir=None):
    """
    从视频中提取音频并保存到指定路径
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录路径，如果为None则使用视频所在目录
    """
    # 获取视频文件名（不含扩展名）
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(video_path)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建音频文件路径
    audio_path = os.path.join(output_dir, f"{video_name}_audio.wav")
    
    try:
        print(f"正在提取音频...")
        print(f"视频路径: {video_path}")
        print(f"音频输出路径: {audio_path}")
        
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()
        
        print(f"音频提取完成: {audio_path}")
        model = whisper.load_model("base")  # 或 "small", "medium", "large"
        audio_path = os.path.abspath(audio_path)
        audio_path = os.path.normpath(audio_path)
        print(f"Whisper 读取音频路径: {audio_path}")
        result = model.transcribe(audio_path)
        # 将结果保存到txt文件中
        with open(os.path.join(output_dir, f"{video_name}_whisper_result.txt"), "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        return audio_path
        
    except Exception as e:
        print(f"音频提取失败: {str(e)}")
        return None

# 执行示例
if __name__ == "__main__":
    video_path = "D:/my_project/softwareDemo/file/Linux/cp07/01_know_TensorFlow.js-1.mp4"
    
    # 提取视频帧
    print("开始提取视频帧...")
    frames_dir, total_frames = extract_frames(video_path)
    print(f"视频帧提取完成！")
    print(f"保存目录: {frames_dir}")
    print(f"总帧数: {total_frames}")


    # 启用OCR识别
    if frames_dir is not None and os.path.exists(frames_dir):
        print("\n开始OCR识别...")
        ocr_frames_optimized(frames_dir, save_text=True)
    else:
        print("视频处理失败或目录不存在，跳过OCR识别")

    # # 语音识别示例
    # print("\n开始语音识别...")
    
    # # 使用指定输出目录
    # custom_output_dir = "D:/my_project/softwareDemo/file/Linux/audio_output"
    # audio_path = speech_recognition(video_path, output_dir=custom_output_dir)
    

    # if audio_path:
    #     print(f"音频已保存到: {audio_path}")


