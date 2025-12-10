import requests
import os
import re

def get_static_html_content(url):
    """
    获取静态网页内容
    
    参数:
        url: 网页URL地址
    
    返回:
        网页HTML内容
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


import re
import requests
from bs4 import BeautifulSoup

def download_image(image_url, save_dir, filename, retries=3):
    """
    下载图片到本地目录，支持重试机制
    
    参数:
        image_url: 图片的URL地址
        save_dir: 保存图片的目录
        filename: 保存的文件名
        retries: 重试次数
    
    返回:
        保存的图片路径，如果下载失败返回None
    """
    for attempt in range(retries):
        try:
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # 确保图片目录存在
            os.makedirs(save_dir, exist_ok=True)
            
            # 生成图片文件路径
            img_path = os.path.join(save_dir, filename)
            
            # 保存图片
            with open(img_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return img_path
        except Exception as e:
            print(f"下载图片失败 (尝试 {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                import time
                time.sleep(1)  # 等待1秒后重试
    
    return None

def extract_images_from_content(content):
    """
    从文章内容中提取所有图片URL
    
    参数:
        content: 文章内容（HTML或Markdown）
    
    返回:
        图片URL列表
    """
    # 首先尝试解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img')
    
    if img_tags:
        return [img['src'] for img in img_tags if 'src' in img.attrs]
    
    # 如果不是HTML，尝试解析Markdown中的图片链接
    md_img_pattern = r'!\[.*?\]\((.*?)\)'
    return re.findall(md_img_pattern, content)

def replace_image_references(content, img_mapping):
    """
    替换文章内容中的图片引用为本地路径
    
    参数:
        content: 文章内容
        img_mapping: 图片URL到本地路径的映射
    
    返回:
        替换后的文章内容
    """
    # 首先处理HTML格式的图片
    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img')
    
    for img in img_tags:
        if 'src' in img.attrs:
            img_url = img['src']
            if img_url in img_mapping:
                img['src'] = img_mapping[img_url]
    
    html_content = str(soup)
    
    # 然后处理Markdown格式的图片
    md_img_pattern = r'!\[.*?\]\((.*?)\)'
    
    def replace_md_img(match):
        img_url = match.group(1)
        if img_url in img_mapping:
            return f"![image]({img_mapping[img_url]})"
        return match.group(0)
    
    return re.sub(md_img_pattern, replace_md_img, html_content)

def save_article_to_md(title, image_url, content, article_link, index, data_dir, author_info="", excerpt=""):
    """
    保存文章到Markdown文件，实现图片自动下载和引用替换
    
    参数:
        title: 文章标题
        image_url: 图片URL
        content: 文章内容
        article_link: 文章链接
        index: 文章索引
        data_dir: 数据保存目录
    
    返回:
        保存的Markdown文件路径
    """
    # 生成标题前20个字符
    short_title = title[:20] if title else "untitled"
    # 替换非法字符
    safe_short_title = re.sub(r'[<>:"/\\|?*]', '-', short_title)
    safe_short_title = safe_short_title.strip()
    
    # 创建以"index-标题前20个字符"命名的子文件夹
    article_dir = os.path.join(data_dir, f"{index}-{safe_short_title}")
    # 确保文章目录存在
    os.makedirs(article_dir, exist_ok=True)
    
    # 提取所有图片URL（包括封面图和正文图片）
    all_img_urls = []
    if image_url:
        all_img_urls.append(image_url)
    
    # 从正文内容中提取图片URL
    content_img_urls = extract_images_from_content(content)
    all_img_urls.extend(content_img_urls)
    
    # 下载所有图片并生成映射关系
    img_mapping = {}
    for img_index, img_url in enumerate(all_img_urls, 1):
        # 生成图片文件名：1.jpg, 2.jpg等
        img_filename = f"{img_index}.jpg"
        # 图片保存目录（在文章子文件夹内）
        img_path = os.path.join(article_dir, img_filename)
        
        # 下载图片
        download_success = download_image(img_url, article_dir, img_filename)
        if download_success:
            # 生成相对引用路径
            img_mapping[img_url] = img_filename
    
    # 构建Markdown内容：标题+作者信息+摘要+图片+文章
    md_content = f"# {title}\n\n"
    
    # 添加作者信息和时间
    if author_info:
        md_content += f"**{author_info}**\n\n"
    
    # 添加摘要
    if excerpt:
        md_content += f"&gt; {excerpt}\n\n"
    
    # 如果有封面图片，添加到标题下方
    if image_url and image_url in img_mapping:
        md_content += f"![image]({img_mapping[image_url]})\n\n"
    
    # 替换内容中的图片引用
    processed_content = replace_image_references(content, img_mapping)
    
    # 使用markdownify转换为Markdown格式（如果是HTML）
    try:
        from bs4 import BeautifulSoup
        import markdownify
        # 检查是否为HTML内容
        soup = BeautifulSoup(processed_content, 'html.parser')
        if soup.find():
            # 是HTML，转换为Markdown
            md_content_temp = markdownify.markdownify(processed_content, heading_style="ATX")
            # 将转换结果中的&gt;替换为>
            md_content_temp = md_content_temp.replace("&gt;", ">")
            # 添加到最终内容中
            md_content += md_content_temp
        else:
            # 已经是Markdown，直接添加
            md_content += processed_content
    except Exception as e:
        # 转换失败，直接使用原始内容
        md_content += processed_content
    
    # 生成content.md文件路径
    filename = os.path.join(article_dir, "content.md")
    
    # 保存到文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filename

