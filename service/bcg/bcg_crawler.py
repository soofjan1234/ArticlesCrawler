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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import markdownify
import re
import time
from service.utils import download_image, get_static_html_content, save_article_to_md

# 目标列表URL
LIST_URL = "https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff5173002a&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0"
# 数据保存目录
DATA_DIR = "data/bcg"

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 使用Selenium获取动态加载的页面内容，返回driver和初始HTML
def get_initial_driver(url):
    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 初始化WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    
    # 打开URL
    driver.get(url)
    
    # 等待页面加载
    time.sleep(3)
    
    # 获取初始页面HTML
    initial_html = driver.page_source
    
    return driver, initial_html

# 下滑页面加载更多内容
def scroll_to_load_more(driver):
    # 向下滚动到页面底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # 等待加载
    time.sleep(2)
    # 获取当前页面HTML
    current_html = driver.page_source
    return current_html

# 解析列表页面，只提取文章链接
def parse_list_page(html_content, existing_links=None, max_items=20):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找文章列表容器：div.search-results-item-set / div[data-qa=hits]
    results_div = soup.find('div', class_='search-results-item-set')
    if not results_div:
        raise Exception("未找到文章列表容器")
    
    # 使用data-qa=hits查找hits div
    hits_div = results_div.find('div', attrs={'data-qa': 'hits'})
    if not hits_div:
        # 直接查找data-qa=hits
        hits_div = soup.find('div', attrs={'data-qa': 'hits'})
        if not hits_div:
            raise Exception("未找到文章列表hits")
    
    # 查找所有a标签，提取文章链接
    a_tags = hits_div.find_all('a')
    
    # 从每个a标签中提取文章链接
    articles_links = []
    existing_set = set(existing_links) if existing_links else set()
    
    for a_tag in a_tags:
        # 提取链接
        link = a_tag.get('href', '')
        if not link:
            continue
        
        # 确保链接是完整的URL
        if not link.startswith(('http://', 'https://')):
            link = f"https://www.bcg.com{link}"
        
        # 只保留publications链接且不在已存在列表中
        if '/publications/' in link and link not in existing_set:
            articles_links.append(link)
            existing_set.add(link)
            
            # 达到最大数量则停止
            if len(articles_links) >= max_items:
                break
    
    return articles_links

# 提取文章封面图片
def extract_article_image(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找目标图片div
    image_wrapper_div = soup.find('div', class_='heroAnimatedPanel_image_wrapper')
    if not image_wrapper_div:
        return None
    
    # 查找图片标签
    img_tag = image_wrapper_div.find('img')
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    
    return None

# 解析文章页面，提取文章正文并转换为Markdown
def parse_article_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找目标文章内容div
    article_div = soup.find('div', class_='ReadingExperience-articleBody richtext-content')
    if not article_div:
        article_div = soup.find('div', class_='LocalArticlePage-articleBody richtext-content')
        if not article_div:
            raise Exception("未找到目标文章内容div")
    
    # 返回原始HTML内容，由utils.py中的save_article_to_md函数统一转换为Markdown
    return str(article_div)

# 从文章页面提取标题
def extract_article_title(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找h1标题
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text(strip=True)
    
    # 查找其他可能的标题标签
    h2_tag = soup.find('h2')
    if h2_tag:
        return h2_tag.get_text(strip=True)
    
    return "Untitled"

# 提取文章作者、时间和摘要
def extract_article_meta(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取作者信息和时间
    author_info = ""
    details_div = soup.find('div', class_='heroAnimatedPanel_details')
    if details_div:
        author_info = details_div.get_text(strip=True)
    
    # 提取摘要
    excerpt = ""
    key_takeaways_div = soup.find('div', class_='keyTakeAways_description')
    if key_takeaways_div:
        excerpt = key_takeaways_div.get_text(strip=True)
        # 使用正则表达式处理"Key Takeaways"后面的空格问题
        import re
        # 将"Key Takeaways"后面没有空格的情况替换为带空格的形式
        excerpt = re.sub(r'Key Takeaways(?!\s)', r'Key Takeaways ', excerpt)
    
    return author_info, excerpt

# 主函数
def main():
    try:
        print(f"开始爬取 {LIST_URL} 的文章列表...")
        
        max_items = 20  # 目标文章数量
        all_articles_links = []
        max_scrolls = 10  # 最大下滑次数
        scroll_count = 0
        
        # 获取初始driver和页面内容
        driver, current_html = get_initial_driver(LIST_URL)
        
        try:
            while len(all_articles_links) < max_items and scroll_count < max_scrolls:
                # 解析当前页面，提取增量文章链接
                new_links = parse_list_page(current_html, existing_links=all_articles_links, max_items=max_items - len(all_articles_links))
                
                if new_links:
                    # 添加新链接到总列表
                    all_articles_links.extend(new_links)
                    print(f"已提取 {len(all_articles_links)}/{max_items} 篇文章链接")
                    
                    # 如果已达到目标数量，停止
                    if len(all_articles_links) >= max_items:
                        break
                
                # 下滑加载更多内容
                print(f"下滑加载更多内容... (第 {scroll_count + 1}/{max_scrolls} 次)")
                current_html = scroll_to_load_more(driver)
                scroll_count += 1
                
                # 如果没有新增链接，可能已加载完所有内容，停止
                if not new_links:
                    print("没有找到新的文章链接，停止加载")
                    break
        finally:
            # 关闭浏览器
            driver.quit()
        
        print(f"\n成功提取 {len(all_articles_links)} 篇文章链接")
        
        if not all_articles_links:
            print("未找到任何文章链接，爬取终止")
            return
        
        print(f"\n=== 开始爬取 {len(all_articles_links)} 篇文章的详细内容 ===")
        
        # 爬取每篇文章的详细内容并保存为Markdown
        for i, article_link in enumerate(all_articles_links, 1):
            print(f"\n正在处理第 {i}/{len(all_articles_links)} 篇文章: {article_link}")
            
            try:
                # 获取文章页面HTML
                article_html = get_static_html_content(article_link)
                
                # 从文章页面提取标题
                title = extract_article_title(article_html)
                
                # 从文章页面提取封面图片
                image_url = extract_article_image(article_html)
                
                # 提取作者信息、时间和摘要
                author_info, excerpt = extract_article_meta(article_html)
                
                # 提取文章正文
                content = parse_article_content(article_html)
                
                # 保存为Markdown文件
                filename = save_article_to_md(title, image_url, content, article_link, i, DATA_DIR, author_info, excerpt)
                print(f"  已保存到: {filename}")
                
            except Exception as e:
                print(f"  处理失败: {e}")
                continue
        
        print(f"\n=== 爬取完成 ===")
        print(f"共爬取了 {len(all_articles_links)} 篇文章")
        print(f"Markdown文件已保存到: {os.path.abspath(DATA_DIR)}")
        
    except Exception as e:
        print(f"处理过程中出错：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()