# 数据量统计
## hbs
注意去重
https://www.library.hbs.edu/working-knowledge/collections/strategy-and-innovation 约416
https://www.library.hbs.edu/working-knowledge/collections/data-and-technology 约257
https://www.library.hbs.edu/working-knowledge/collections/leadership 约493
https://www.library.hbs.edu/working-knowledge/collections/marketing-and-consumers 约403
https://www.library.hbs.edu/working-knowledge/collections/managing-the-business 约475
https://www.library.hbs.edu/working-knowledge/collections/regulation-and-compliance 约419
https://www.library.hbs.edu/working-knowledge/collections/economics-and-global-commerce 约377
https://www.library.hbs.edu/working-knowledge/collections/career-and-workplace 约455 
https://www.library.hbs.edu/working-knowledge/collections/social-responsibility-and-sustainability 约358

## ivey
https://iveybusinessjournal.com/articles/ 约10*14=140

## bcg
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff5173002a&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约918
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff51730012&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约247
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff4ad80191&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约87
https://www.bcg.com/search?q=&f4=0000018e-5c40-d24a-a9ff-dce485ef0000&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约81
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff51730005&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约484
https://www.bcg.com/search?q=&f4=00000172-0edd-d58d-a97a-5effbc6f006c&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约487
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff51730004&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约447
https://www.bcg.com/search?q=&f4=0000018a-760c-d98b-adaa-77fdb3090000&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约86
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff51730007&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约142
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff4ad80195&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约177
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff51730034&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约1177
https://www.bcg.com/search?q=&f4=00000172-f4a0-d350-a3f3-f4b47aa301d5&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约23
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff4ad8019d&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约18
https://www.bcg.com/search?q=&f4=00000172-0efd-d58d-a97a-5eff51730017&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约113
https://www.bcg.com/search?q=&f4=00000172-0edd-d58d-a97a-5effbc700069&f7=00000171-f17b-d394-ab73-f3fbae0d0000&s=0 约90

# 爬取解析方案
selenium + markdownify

# 异步爬取实现方案
为了提高爬取效率，建议使用以下异步爬取方案：

- 使用asyncio库来管理协程
- 使用httpx.AsyncClient进行异步HTTP请求，这允许在等待网络响应时不阻塞程序的其他部分
- 使用asyncio.gather来并发执行多个协程，这些协程分别处理不同页面的数据获取

## 实现建议
1. 控制并发数：根据目标网站的反爬策略，设置合理的并发数（如20-50）
2. 添加延迟：在请求之间添加适当延迟（如0.1-0.5秒），模拟人工浏览
3. 实现重试机制：处理网络错误、超时等异常情况
4. 考虑代理：如果网站有IP限制，准备代理IP池
5. 分布式爬取：可考虑多机器分布式爬取，进一步提高效率

## 预期效果
使用异步爬取方案，8000条数据的爬取时间可从约2.2小时缩短至约10-20分钟，显著提高爬取效率。约8370条


