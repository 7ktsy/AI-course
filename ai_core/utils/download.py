import os
from typing import Optional
import markdown
import pdfkit
import tempfile
import time

# 配置 wkhtmltopdf 路径
WKHTMLTOPDF_PATH = r'D:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

def save_as_markdown(markdown_text: str, filename: str) -> str:
    """
    将文本保存为markdown文件
    Args:
        markdown_text (str): 要保存的markdown文本
        filename (str): 保存文件的文件名（不包含路径和后缀）
    Returns:
        str: 保存文件的路径
    """
    try:
        # 构建输出路径
        save_dir = "D:\\Download"
        output_path = os.path.join(save_dir, f"{filename}.md")
        
        # 确保输出目录存在
        os.makedirs(save_dir, exist_ok=True)
        
        # 检查文件是否已存在，如果存在则在文件名后添加序号
        base_path = os.path.join(save_dir, filename)
        counter = 1
        while os.path.exists(output_path):
            output_path = f"{base_path}_{counter}.md"
            counter += 1
            
        # 保存markdown文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
            
        return output_path
        
    except Exception as e:
        raise Exception(f"保存markdown文件失败: {str(e)}")

def markdown_to_pdf(markdown_text: str, filename: str) -> str:
    """
    将markdown文本转换为pdf文件
    Args:
        markdown_text (str): 要转换的markdown文本
        filename (str): 保存pdf文件的文件名（不包含路径和后缀）
    Returns:
        str: 保存pdf文件的路径
    """
    try:
        # 构建输出路径
        save_dir = "D:\\Download"
        output_path = os.path.join(save_dir, f"{filename}.pdf")
        
        # 确保输出目录存在
        os.makedirs(save_dir, exist_ok=True)
        
        # 检查文件是否已存在，如果存在则在文件名后添加序号
        base_path = os.path.join(save_dir, filename)
        counter = 1
        while os.path.exists(output_path):
            output_path = f"{base_path}_{counter}.pdf"
            counter += 1
        
        # 将markdown文本转换为html，添加扩展支持
        html = markdown.markdown(
            markdown_text,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite'
            ]
        )
        
        # 用适当的html结构和一些基本的样式包装html内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: "Microsoft YaHei", Arial, sans-serif;
                        line-height: 1.6;
                        margin: 40px;
                        color: #333;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #2c3e50;
                        margin-top: 24px;
                        margin-bottom: 16px;
                    }}
                    code {{
                        font-family: Consolas, Monaco, 'Courier New', monospace;
                        background-color: #f5f5f5;
                        padding: 2px 4px;
                        border-radius: 4px;
                        font-size: 0.9em;
                    }}
                    pre {{
                        background-color: #f5f5f5;
                        padding: 16px;
                        border-radius: 4px;
                        overflow-x: auto;
                        line-height: 1.45;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                        border-radius: 0;
                    }}
                    blockquote {{
                        border-left: 4px solid #ddd;
                        padding-left: 16px;
                        margin-left: 0;
                        color: #666;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 16px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f5f5f5;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
        </html>
        """
        
        # 创建一个临时html文件
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as temp_html:
            temp_html.write(html_content)
            temp_html_path = temp_html.name
        
        try:
            # 配置wkhtmltopdf选项
            options = {
                'encoding': 'UTF-8',
                'no-outline': None,
                'quiet': '',
                'enable-local-file-access': None,
                'margin-top': '20',
                'margin-right': '20',
                'margin-bottom': '20',
                'margin-left': '20'
            }
            
            # 使用配置的wkhtmltopdf路径转换HTML为PDF
            pdfkit.from_file(temp_html_path, output_path, configuration=config, options=options)
            
            # 清理临时html文件
            os.unlink(temp_html_path)
            
            return output_path
            
        except Exception as e:
            # 在发生错误的情况下清理临时html文件
            if os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
            raise e
            
    except Exception as e:
        raise Exception(f"将markdown文本转换为pdf文件失败: {str(e)}")
    

if __name__ == "__main__":
    markdown_text = "以下是计算机网络课程**第5周：网络层（上）** 的完整教学设计，严格依据知识库中的教学大纲和知识点总结制定：\n\n---\n### **一、上周知识点回顾（5分钟）**  \n1. **数据链路层核心功能**  \n   - 帧结构（帧头/数据/帧尾）与差错控制（CRC校验）  \n   - MAC地址与**ARP协议工作流程**（请 求广播→响应单播→缓存更新）   \n   - 交换机基于MAC地址的转发原理  \n\n---\n### **二、本周知识点讲解（40分钟）**  \n#### **1. IP协议与IPv4地址（20分钟）**  \n- **IP协议核心作用**：无连接、不可靠的数据报交付  \n- **IPv4地址结构**：  \n  ```markdown\n  32位二进制 → 点分十进制（如 192.168.1.1）\n  分类地址范围：  \n    A类：1.0.0.0 ~ 126.255.255.255  \n    B类：128.0.0.0 ~ 191.255.255.255  \n    C类：192.0.0.0 ~ 223.255.255.255  \n  （特殊地址：127.0.0.1环回地址、0.0.0.0默认路由）\n  ```\n- **关键字段**：TTL（防环路）、协议号（标识TCP/UDP等）  \n\n#### **2. 子网划分与CIDR（15分钟）**  \n- **子网掩码作用**：区分网络位与主机位（如 `255.255.255.0 → /24`）  \n- **划分子网三步法**：  \n  1. 根据需求确定主机位数（主机数=2^H-2）  \n  2. 计算子网掩码（网络位向主机位“借位”）  \n  3. 推导子网地址范围  \n- **CIDR优势**：聚合路由（如 `192.168.0.0/22` 覆盖4个C类网）  \n\n#### **3. ICMP与Ping工具（5分钟）**  \n- **ICMP功能**：网络诊断（类型字段：0-回显应答，8-回显请求）  \n- **Ping工作流程**：发送ICMP Echo Request → 目标主机回复Echo Reply  \n\n---\n### **三、教学关键内容（板书/PPT重点）**  \n#### **IPv4数据报格式（Mermaid图）**  \n```mermaid\nclassDiagram\n    class IPv4Header {\n        +版本(4b)：4\n        +首部长度(4b)：5（单位：4字节）\n        +服务类型(8b)\n        +总长度(16b)\n        +标识(16b)：分片重组标识\n        +标志(3b)：DF/MF\n        +片偏移(13b)\n        +TTL(8b)\n        +协议(8b)：6=TCP, 17=UDP\n        +首部校验 和(16b)\n        +源IP地址(32b)\n        +目的IP地址(32b)\n        +选项(可选)\n    }\n```\n\n#### **Ping命令执行流程（Mermaid序列图）**  \n```mermaid\nsequenceDiagram\n    participant A as 主机A\n    participant R as 路由器\n    participant B as 主机B\n    A->>R： ICMP Echo Request (TTL=64)\n    R->>B： 转发请求（TTL减1）\n    B->>R： ICMP Echo Reply\n    R->>A： 转发回复\n```\n\n---\n### **四、实训练习与指导（30分钟）**  \n** 题目1：子网划分实战**  \n> 给定IP地址 `172.16.0.0/16`，需划分6个子网（ \n| ICMP与Ping          | 5min   | 动画演示     |  \n| 实训练习            | 30min  | 小组计算+指导|  \n| 总结与答疑          | 5min   | 互动         |  \n\n---\n### **六、相关知识点拓展**  \n- **现实问题**：IPv4地址枯竭 → 引出NAT技术（下周重点）  \n- **安全延伸**：伪造ICMP报文（死亡之Ping攻击）→ 防火墙过滤机制  \n- **前沿动态**：IPv6地址结构（128位，冒号分隔十六进制）  \n\n---\n**Citation依据**：  \n- ARP流程引用自知识点文档碎片（,4）  \n-  第五周教学内容严格遵循大纲（）  \n- 实验设计参考大纲实验列表（）"
    filename = "下载1"
    save_as_markdown(markdown_text, filename)