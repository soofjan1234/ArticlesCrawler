import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.abspath(os.path.join(current_dir, '.'))
# 添加到Python搜索路径
sys.path.append(project_root)

# 导入需要的函数
from service.utils import get_static_html_content, save_article_to_md
from service.ivey.ivey_crawler import parse_list_page, extract_article_image, parse_article_content, extract_article_meta

# 测试IVEY文章列表页URL
list_url = "https://iveybusinessjournal.com/articles/"

# 测试爬取IVEY文章
def test_ivey_article():
    try:
        print(f"开始测试IVEY爬虫...")
        print(f"1. 访问IVEY文章列表页: {list_url}")
        
        # 1. 获取文章列表页HTML
        list_html = get_static_html_content(list_url)
        print("   ✅ 成功获取文章列表页HTML内容")
        
        # 2. 解析文章列表页，获取第一篇文章的信息
        print("2. 解析文章列表页，获取第一篇文章信息...")
        # 调用parse_list_page函数，获取文章列表
        articles_info, next_page_url = parse_list_page(list_html, max_items=1)
        
        if not articles_info:
            print("   ❌ 未找到任何文章")
            return
        
        # 获取第一篇文章的信息
        title, list_image_url, article_link, category = articles_info[0]
        print(f"   ✅ 找到第一篇文章")
        print(f"   - 标题: {title}")
        print(f"   - 链接: {article_link}")
        print(f"   - 分类: {category}")
        
        # 3. 访问文章详情页
        print(f"3. 访问文章详情页: {article_link}")
        article_html = get_static_html_content(article_link)
        print("   ✅ 成功获取文章详情页HTML内容")
        
        # 4. 提取文章封面图片
        print("4. 提取文章封面图片...")
        article_image_url = extract_article_image(article_html)
        # 如果文章页面没有图片，使用列表页的图片
        image_url = article_image_url if article_image_url else list_image_url
        print(f"   ✅ 封面图片URL: {image_url}")
        
        # 5. 提取作者信息和摘要
        print("5. 提取作者信息和摘要...")
        author_info = extract_article_meta(article_html)
        print(f"   ✅ 作者信息: {author_info}")
        
        # 6. 提取文章正文
        print("6. 提取文章正文...")
        content = parse_article_content(article_html)
        print(f"   ✅ 正文长度: {len(content)} 字符")
        
        # 7. 保存为Markdown文件
        print("7. 保存为Markdown文件...")
        data_dir = "data/ivey/test"
        filename = save_article_to_md(title, image_url, content, article_link, 1, data_dir, author_info, "", category)
        print(f"   ✅ 已保存到: {filename}")
        
        print("\n=== 测试完成 ===")
        print("所有步骤均成功执行！")
        
    except Exception as e:
        print(f"\n=== 测试失败 ===")
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ivey_article()