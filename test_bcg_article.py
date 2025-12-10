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
from service.bcg.bcg_crawler import parse_article_content, extract_article_image, extract_article_meta

# 测试URL
test_url = "https://www.bcg.com/publications/2025/navigating-the-path-to-sustained-shareholder-returns"

# 测试爬取单篇BCG文章
def test_single_article():
    try:
        print(f"开始测试爬取BCG文章: {test_url}")
        
        # 1. 获取文章页面HTML
        print("1. 获取文章页面HTML...")
        article_html = get_static_html_content(test_url)
        print("   ✅ 成功获取HTML内容")
        
        # 2. 提取文章标题
        print("2. 提取文章标题...")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(article_html, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Untitled"
        print(f"   ✅ 文章标题: {title}")
        
        # 3. 提取文章封面图片
        print("3. 提取文章封面图片...")
        image_url = extract_article_image(article_html)
        print(f"   ✅ 封面图片URL: {image_url}")
        
        # 4. 提取作者信息、摘要和分类
        print("4. 提取作者信息、摘要和分类...")
        author_info, excerpt, category = extract_article_meta(article_html)
        print(f"   ✅ 作者信息: {author_info}")
        print(f"   ✅ 摘要: {excerpt[:100]}...")
        print(f"   ✅ 分类: {category}")
        
        # 5. 提取文章正文
        print("5. 提取文章正文...")
        content = parse_article_content(article_html)
        print(f"   ✅ 正文长度: {len(content)} 字符")
        
        # 6. 保存为Markdown文件
        print("6. 保存为Markdown文件...")
        data_dir = "data/bcg/test"
        filename = save_article_to_md(title, image_url, content, test_url, 1, data_dir, author_info, excerpt, category)
        print(f"   ✅ 已保存到: {filename}")
        
        print("\n=== 测试完成 ===")
        print("所有步骤均成功执行！")
        
    except Exception as e:
        print(f"\n=== 测试失败 ===")
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_article()