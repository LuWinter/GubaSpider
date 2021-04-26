from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 根据项目配置获取 CrawlerProcess 实例
process = CrawlerProcess(get_project_settings())

# 添加需要执行的爬虫
process.crawl('GubaCrawl')
process.crawl('GubaCrawl2')
process.crawl('GubaCrawl3')
process.crawl('GubaCrawl4')
process.crawl('GubaCrawl5')
process.crawl('GubaCrawl6')

# 执行
process.start()
