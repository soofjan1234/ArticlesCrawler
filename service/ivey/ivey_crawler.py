import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
# 添加到Python搜索路径
sys.path.append(project_root)

import requests
from bs4 import BeautifulSoup
import markdownify
import re
from ..utils import download_image, get_static_html_content, save_article_to_md

# 目标列表URL
base_url = "https://iveybusinessjournal.com/articles/"
# 数据保存目录
data_dir = "data/ivey"

# 确保数据目录存在
os.makedirs(data_dir, exist_ok=True)

# 解析列表页面，提取文章标题和链接
def parse_list_page(html_content, max_items=10):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找文章列表容器
    posts_div = soup.find('div', class_='cmsmasters-blog__posts')
    if not posts_div:
        raise Exception("未找到文章列表容器")
    
    # 查找所有article元素
    articles = posts_div.find_all('article', limit=max_items)
    
    if not articles:
        raise Exception("未找到文章列表项")
    
    # 从每个article中提取文章信息
    articles_info = []
    for article in articles:
        # 查找h2标题
        h2_tag = article.find('h2', class_='entry-title cmsmasters-widget-title__heading')
        if not h2_tag:
            continue
        
        # 提取标题和链接
        a_tag = h2_tag.find('a')
        if not a_tag or 'href' not in a_tag.attrs:
            continue
        
        title = a_tag.get_text(strip=True)
        link = a_tag['href']
        
        # 先不提取图片，留待后续从文章页面提取
        image_url = None
        
        # 保存文章信息
        articles_info.append((title, image_url, link))
    
    # 提取下一页链接
    next_page_url = ""

    # 先找ul class=page-numbers
    ul_tag = soup.find('ul', class_='page-numbers')
    if ul_tag:
        # 找li下面的a标签，class为next page-numbers
        next_button = ul_tag.find('a', class_='next page-numbers')
        if next_button and 'href' in next_button.attrs:
            next_page_url = next_button['href']

            if not next_page_url.startswith(('http://', 'https://')):
                # 转换为绝对URL
                next_page_url = f"https://iveybusinessjournal.com{next_page_url}"
    
    return articles_info, next_page_url

# 提取文章封面图片
def extract_article_image(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找目标图片div
    media_div = soup.find('div', class_='cmsmasters-single-post-media cmsmasters-section-container')
    if not media_div:
        return None
    
    # 查找图片标签
    img_tag = media_div.find('img')
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    
    return None

# 解析文章页面，提取文章正文并转换为Markdown
def parse_article_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找目标文章内容div
    article_div = soup.find('div', class_='cmsmasters-single-post-content entry-content')
    if not article_div:
        raise Exception("未找到目标文章内容div")
    
    # 使用markdownify库进行转换
    markdown = markdownify.markdownify(str(article_div), heading_style="ATX")
    return markdown



# 主函数
def main():
    try:
        all_articles = []
        current_url = base_url
        pages_to_crawl = 2  # 只抓取前两页
        
        print(f"开始爬取 {base_url} 的前 {pages_to_crawl} 页内容...")
        
        for page in range(1, pages_to_crawl + 1):
            print(f"\n=== 正在抓取第 {page} 页: {current_url} ===")
            
            # 获取静态页面HTML
            list_html = get_static_html_content(current_url)
            
            # 解析页面，获取文章信息和下一页链接
            page_articles, next_page_url = parse_list_page(list_html, max_items=10)
            print(f"成功提取第 {page} 页的 {len(page_articles)} 篇文章信息")
            
            # 添加到总列表
            all_articles.extend(page_articles)
            
            # 如果没有下一页或已经抓取了足够的页面，停止
            if not next_page_url or page >= pages_to_crawl:
                break
            
            # 更新当前URL为下一页URL
            current_url = next_page_url
        
        print(f"\n=== 开始爬取 {len(all_articles)} 篇文章的详细内容 ===")
        
        # 爬取每篇文章的详细内容并保存为Markdown
        for i, (title, list_image_url, article_link) in enumerate(all_articles, 1):
            print(f"\n正在处理第 {i}/{len(all_articles)} 篇文章: {title}")
            
            try:
                # 获取文章页面HTML
                article_html = get_static_html_content(article_link)
                
                # 从文章页面提取封面图片（优先级更高）
                article_image_url = extract_article_image(article_html)
                # 如果文章页面没有图片，使用列表页的图片
                image_url = article_image_url if article_image_url else list_image_url
                
                # 提取文章正文
                content = parse_article_content(article_html)
                
                # 保存为Markdown文件
                filename = save_article_to_md(title, image_url, content, article_link, i, data_dir)
                print(f"  已保存到: {filename}")
                
            except Exception as e:
                print(f"  处理失败: {e}")
                continue
        
        print(f"\n=== 爬取完成 ===")
        print(f"共爬取了 {len(all_articles)} 篇文章")
        print(f"Markdown文件已保存到: {os.path.abspath(data_dir)}")
        
    except Exception as e:
        print(f"处理过程中出错：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()