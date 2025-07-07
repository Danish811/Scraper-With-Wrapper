import json
import math
import scrapy
from urllib.parse import urlencode

class WalmartSpider(scrapy.Spider):
    name = "walmart"

    custom_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    }

    def __init__(self, custom_keyword=None, *args, **kwargs):
        super(WalmartSpider, self).__init__(*args, **kwargs)
        self.custom_keyword = custom_keyword or 'laptop'

    async def start(self):
        """Async start method for Scrapy 2.13+"""
        payload = {'keyword': self.custom_keyword, 'sort': 'rlvncy'}
        snapdeal_search_url = 'https://www.snapdeal.com/search?' + urlencode(payload)
        yield scrapy.Request(
            url=snapdeal_search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.custom_keyword, 'page': 1},
            headers={
                'Referer': 'https://www.snapdeal.com/',
                'Sec-Fetch-Site': 'same-origin',
            }
        )

    def start_requests(self):
        """Legacy method for backward compatibility"""
        # Test with a simple website that doesn't block scrapers
        payload = {"keyword": self.custom_keyword, "sort": "rlvncy", "page": 1}
        search_url = "https://www.snapdeal.com/search?" + urlencode(payload)
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={
                "playwright": True, 
                "playwright_page_methods": [
                # optional: wait for the product-list container to appear
                    {"name": "wait_for_selector", "args": ["div.product-tuple-listing"]},
                ],
                "keyword": self.custom_keyword, 
                "page": 1,
                },
            headers={
                'Referer': 'https://www.snapdeal.com/',
                'Sec-Fetch-Site': 'same-origin',
            }
        )

    def parse_search_results(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword']
        
        # Debug: Log the response
        self.logger.info(f"Parsing search results for keyword: {keyword}, page: {page}")
        self.logger.info(f"Response URL: {response.url}")
        self.logger.info(f"Response status: {response.status}")
        
        products = response.xpath('//div[contains(@class, "product-tuple-listing")]')
        if products:
            self.logger.info("Found Snapdeal product listings")
            try:
                product_list = products
                self.logger.info(f"Found {len(product_list)} products in the list")
                for idx, product in enumerate(product_list):
                    product_url = product.xpath('.//a[@class="dp-widget-link"]/@href').get()
                    if product_url:
                        snapdeal_product_url = response.urljoin(product_url)
                        self.logger.info(f"Requesting product URL: {snapdeal_product_url}")
                        yield scrapy.Request(
                            url=snapdeal_product_url,
                            callback=self.parse_product_data,
                            meta={
                              "playwright": True,        # in case product pages need JS
                              "keyword": response.meta["keyword"],
                              "page": response.meta["page"],
                              "position": idx + 1,
                            },
                        )
            except Exception as e:
                self.logger.warning(f"Failed to parse Snapdeal product listings: {e}")
        else:
            self.logger.warning("No Snapdeal product listings found")
            with open('debug_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            self.logger.info("Saved response body to debug_response.html")

    def parse_product_data(self, response):
        # Snapdeal product details extraction (example, may need adjustment)
        title = response.xpath('//h1[@class="pdp-e-i-head"]//text()').get()
        price = response.xpath('//span[contains(@class, "payBlkBig")]/text()').get()
        image_url = response.xpath('//img[@class="cloudzoom"]/@src').get()
        description = response.xpath('//div[@class="spec-section"]//text()').getall()
        yield {
            'keyword': response.meta['keyword'],
            'page': response.meta['page'],
            'position': response.meta['position'],
            'name': title,
            'price': price,
            'image_url': image_url,
            'description': ' '.join(description).strip(),
            'url': response.url
        }
