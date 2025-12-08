import requests
from bs4 import BeautifulSoup
import re

# 目标URL
url = "https://www.library.hbs.edu/working-knowledge/many-gen-ai-players-remain-far-away-from-profiting-interview-with-andy-wu"

# 发送请求获取网页内容
def get_html_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# 解析HTML，提取目标内容
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # 查找目标div
    article_div = soup.find('div', class_='hbs-global-align-center hbs-rich-text hbs-use-dropcap')
    if not article_div:
        raise Exception("未找到目标文章内容div")
    return article_div

# 将HTML转换为Markdown
def html_to_markdown(html_element):
    # 处理引用块
    for blockquote in html_element.find_all('blockquote', class_='hbs-pullquote'):
        blockquote.replace_with(BeautifulSoup(f'<blockquote>{blockquote.get_text(strip=True)}</blockquote>', 'html.parser'))
    
    # 获取所有需要处理的元素
    elements = html_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'blockquote', 'a'])
    
    markdown = ""
    processed_p_elements = set()
    
    for element in elements:
        if element.name == 'p':
            # 避免重复处理
            if element in processed_p_elements:
                continue
            processed_p_elements.add(element)
            
            # 处理段落，检查是否包含链接
            text = ""
            for child in element.children:
                if child.name == 'a':
                    # 处理链接
                    link_text = child.get_text(strip=True)
                    link_href = child.get('href', '')
                    if link_text and link_href:
                        text += f"[{link_text}]({link_href})"
                else:
                    # 处理普通文本
                    text += child.get_text(strip=True)
            
            if text and text != '$/$$/$$/$':
                markdown += f"{text}\n\n"
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # 处理标题
            level = int(element.name[1])
            # 处理标题中的链接
            text = ""
            for child in element.children:
                if child.name == 'a':
                    link_text = child.get_text(strip=True)
                    link_href = child.get('href', '')
                    if link_text and link_href:
                        text += f"[{link_text}]({link_href})"
                else:
                    text += child.get_text(strip=True)
            markdown += f"{'#' * level} {text}\n\n"
        elif element.name == 'blockquote':
            # 处理引用块
            text = element.get_text(strip=True)
            if text:
                markdown += f"> {text}\n\n"
        elif element.name == 'ul':
            # 处理无序列表
            for li in element.find_all('li'):
                # 处理列表项中的链接
                text = ""
                for child in li.children:
                    if child.name == 'a':
                        link_text = child.get_text(strip=True)
                        link_href = child.get('href', '')
                        if link_text and link_href:
                            text += f"[{link_text}]({link_href})"
                    else:
                        text += child.get_text(strip=True)
                if text:
                    markdown += f"- {text}\n"
            markdown += "\n"
        elif element.name == 'ol':
            # 处理有序列表
            for i, li in enumerate(element.find_all('li'), 1):
                # 处理列表项中的链接
                text = ""
                for child in li.children:
                    if child.name == 'a':
                        link_text = child.get_text(strip=True)
                        link_href = child.get('href', '')
                        if link_text and link_href:
                            text += f"[{link_text}]({link_href})"
                    else:
                        text += child.get_text(strip=True)
                if text:
                    markdown += f"{i}. {text}\n"
            markdown += "\n"
    
    # 如果没有找到元素，直接获取所有文本
    if not markdown:
        all_text = html_element.get_text(separator='\n', strip=True)
        # 过滤掉特殊字符和空行
        lines = [line for line in all_text.split('\n') if line and line != '$/$$/$$/$']
        markdown = '\n\n'.join(lines)
    
    return markdown

# 保存Markdown到文件
def save_to_md(content, filename="output.md"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# 主函数
def main():
    try:
        # 获取HTML内容
        html_content = get_html_content(url)
        
        # 解析HTML，提取目标div
        article_div = parse_html(html_content)
        
        # 转换为Markdown
        markdown_content = html_to_markdown(article_div)
        
        # 保存到文件
        save_to_md(markdown_content)
        
        print("Markdown文件已成功生成：output.md")
        
    except Exception as e:
        print(f"处理过程中出错：{e}")

if __name__ == "__main__":
    main()