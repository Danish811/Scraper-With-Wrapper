#!/usr/bin/env python3
"""
Amazon test spider to verify our scraper infrastructure
"""

import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from scrapy.signalmanager import dispatcher
import scrapy
from urllib.parse import urlencode

class AmazonTestSpider(scrapy.Spider):
    name = "amazon_test"
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }
    
    def __init__(self, search_term=None, *args, **kwargs):
        super(AmazonTestSpider, self).__init__(*args, **kwargs)
        self.search_term = search_term or 'laptop'
    
    def start_requests(self):
        # Amazon search URL
        payload = {'k': self.search_term}
        amazon_search_url = 'https://www.amazon.com/s?' + urlencode(payload)
        
        yield scrapy.Request(
            url=amazon_search_url,
            callback=self.parse_search_results,
            meta={'search_term': self.search_term},
            headers={
                'Referer': 'https://www.amazon.com/',
            }
        )
    
    def parse_search_results(self, response):
        self.logger.info(f"Parsing Amazon search results for: {response.meta['search_term']}")
        self.logger.info(f"Response URL: {response.url}")
        self.logger.info(f"Response status: {response.status}")
        
        # Look for product containers
        products = response.css('[data-component-type="s-search-result"]')
        self.logger.info(f"Found {len(products)} product containers")
        
        for idx, product in enumerate(products[:5]):  # Limit to first 5 products
            try:
                # Extract basic product info
                title = product.css('h2 a span::text').get()
                price = product.css('.a-price-whole::text').get()
                rating = product.css('.a-icon-alt::text').get()
                
                if title:
                    self.logger.info(f"Found product {idx + 1}: {title[:50]}...")
                    
                    yield {
                        'search_term': response.meta['search_term'],
                        'position': idx + 1,
                        'title': title,
                        'price': price,
                        'rating': rating,
                        'url': response.url
                    }
                    
            except Exception as e:
                self.logger.warning(f"Error parsing product {idx + 1}: {e}")
        
        # Save response for debugging
        with open('amazon_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info("Saved response to amazon_debug.html")

def run_amazon_test(search_term="laptop", limit=5):
    """Run Amazon test scraper"""
    results = []
    
    def collect_item(item, response, spider):
        if len(results) < limit:
            results.append(dict(item))
            print(f"Scraped product {len(results)}/{limit}: {item.get('title', 'Unknown')[:50]}...")
        else:
            spider.crawler.engine.close_spider(spider, reason='limit_reached')
    
    # Connect the signal handler
    dispatcher.connect(collect_item, signal=signals.item_scraped)
    
    try:
        # Create crawler process with basic settings
        settings = {
            'BOT_NAME': 'amazon_test',
            'SPIDER_MODULES': [],
            'NEWSPIDER_MODULE': '',
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 3,
            'CONCURRENT_REQUESTS': 1,
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'DEFAULT_REQUEST_HEADERS': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        }
        
        process = CrawlerProcess(settings)
        process.crawl(AmazonTestSpider, search_term=search_term)
        
        print(f"Starting Amazon test scraper for search term: '{search_term}'")
        print(f"Limit: {limit} products")
        
        process.start()
        
        print(f"Amazon test completed. Found {len(results)} products.")
        return results
        
    except Exception as e:
        print(f"Error during Amazon test: {str(e)}")
        return results
    finally:
        # Disconnect the signal handler
        dispatcher.disconnect(collect_item, signal=signals.item_scraped)

if __name__ == "__main__":
    print("Testing Amazon scraper...")
    print("=" * 50)
    
    results = run_amazon_test("laptop", limit=3)
    
    if results:
        print("\n✅ SUCCESS: Amazon scraper is working!")
        print(f"Scraped {len(results)} products")
        for item in results:
            print(f"  - {item.get('title', 'Unknown')[:60]}...")
            print(f"    Price: {item.get('price', 'N/A')}")
            print(f"    Rating: {item.get('rating', 'N/A')}")
            print()
    else:
        print("\n❌ FAILED: Amazon scraper is not working")
        print("Check amazon_debug.html for response details") 