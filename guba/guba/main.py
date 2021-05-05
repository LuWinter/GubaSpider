from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 根据项目配置获取 CrawlerProcess 实例
process = CrawlerProcess(get_project_settings())

# 添加需要执行的爬虫
process.crawl('GubaCrawl')
# process.crawl('GubaCrawl2')
# process.crawl('GubaCrawl3')
# process.crawl('GubaCrawl4')
# process.crawl('GubaCrawl5')
# process.crawl('GubaCrawl6')
# process.crawl('GubaCrawl7')
# process.crawl('GubaCrawl8')
# process.crawl('GubaCrawl9')
# process.crawl('GubaCrawl10')
# process.crawl('GubaCrawl11')
# process.crawl('GubaCrawl12')
# process.crawl('GubaCrawl13')
# process.crawl('GubaCrawl14')
# process.crawl('GubaCrawl15')
# process.crawl('GubaCrawl16')
# process.crawl('GubaCrawl17')
# process.crawl('GubaCrawl18')
# process.crawl('GubaCrawl19')
# process.crawl('GubaCrawl20')

# 执行
process.start()
