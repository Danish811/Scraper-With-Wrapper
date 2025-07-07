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
        payload = {'q': self.custom_keyword, 'sort': 'best_seller', 'page': 1, 'affinityOverride': 'default'}
        walmart_search_url = 'https://www.amazon.com/search?' + urlencode(payload)
        yield scrapy.Request(
            url=walmart_search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.custom_keyword, 'page': 1},
            headers={
                'Referer': 'https://www.amazon.com/',
                'Sec-Fetch-Site': 'same-origin',
            }
        )

    def start_requests(self):
        """Legacy method for backward compatibility"""
        # Test with a simple website that doesn't block scrapers
        test_url = 'https://httpbin.org/html'
        yield scrapy.Request(
            url=test_url,
            callback=self.parse_search_results,
            meta={'keyword': self.custom_keyword, 'page': 1},
            headers={
                'Referer': 'https://httpbin.org/',
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
        
        script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        
        if script_tag:
            self.logger.info("Found __NEXT_DATA__ script tag")
            try:
                json_blob = json.loads(script_tag)
                self.logger.info("Successfully parsed JSON blob")
                
                # Debug: Log the JSON structure
                if "props" in json_blob:
                    self.logger.info("Found 'props' in JSON")
                    if "pageProps" in json_blob["props"]:
                        self.logger.info("Found 'pageProps' in JSON")
                        if "initialData" in json_blob["props"]["pageProps"]:
                            self.logger.info("Found 'initialData' in JSON")
                            if "searchResult" in json_blob["props"]["pageProps"]["initialData"]:
                                self.logger.info("Found 'searchResult' in JSON")
                                if "itemStacks" in json_blob["props"]["pageProps"]["initialData"]["searchResult"]:
                                    self.logger.info("Found 'itemStacks' in JSON")
                                    if len(json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"]) > 0:
                                        self.logger.info("Found items in itemStacks")
                                        product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
                                        self.logger.info(f"Found {len(product_list)} products in the list")
                                        
                                        for idx, product in enumerate(product_list):
                                            walmart_product_url = 'https://www.amazon.com/' + product.get('canonicalUrl', '').split('?')[0]
                                            self.logger.info(f"Requesting product URL: {walmart_product_url}")
                                            yield scrapy.Request(
                                                url=walmart_product_url,
                                                callback=self.parse_product_data,
                                                meta={'keyword': keyword, 'page': page, 'position': idx + 1}
                                            )

                                        if page == 1:
                                            total_product_count = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["count"]
                                            max_pages = min(5, math.ceil(total_product_count / 40))
                                            self.logger.info(f"Total products: {total_product_count}, Max pages: {max_pages}")
                                            for p in range(2, max_pages + 1):
                                                payload = {'q': keyword, 'sort': 'best_seller', 'page': p, 'affinityOverride': 'default'}
                                                walmart_search_url = 'https://www.amazon.com//search?' + urlencode(payload)
                                                yield scrapy.Request(
                                                    url=walmart_search_url,
                                                    callback=self.parse_search_results,
                                                    meta={'keyword': keyword, 'page': p}
                                                )
                                    else:
                                        self.logger.warning("No items found in itemStacks")
                                else:
                                    self.logger.warning("No 'itemStacks' found in searchResult")
                            else:
                                self.logger.warning("No 'searchResult' found in initialData")
                        else:
                            self.logger.warning("No 'initialData' found in pageProps")
                    else:
                        self.logger.warning("No 'pageProps' found in props")
                else:
                    self.logger.warning("No 'props' found in JSON blob")
                    
            except KeyError as e:
                self.logger.warning(f"Failed to parse search result JSON structure: {e}")
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to decode JSON: {e}")
        else:
            self.logger.warning("No __NEXT_DATA__ script tag found")
            # Debug: Save the response body to see what we're getting
            with open('debug_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            self.logger.info("Saved response body to debug_response.html")

    def parse_product_data(self, response):
        script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag:
            try:
                json_blob = json.loads(script_tag)
                raw_product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]
                yield {
                    'keyword': response.meta['keyword'],
                    'page': response.meta['page'],
                    'position': response.meta['position'],
                    'id': raw_product_data.get('id'),
                    'type': raw_product_data.get('type'),
                    'name': raw_product_data.get('name'),
                    'brand': raw_product_data.get('brand'),
                    'averageRating': raw_product_data.get('averageRating'),
                    'manufacturerName': raw_product_data.get('manufacturerName'),
                    'shortDescription': raw_product_data.get('shortDescription'),
                    'thumbnailUrl': raw_product_data['imageInfo'].get('thumbnailUrl'),
                    'price': raw_product_data['priceInfo']['currentPrice'].get('price'),
                    'currencyUnit': raw_product_data['priceInfo']['currentPrice'].get('currencyUnit'),
                }
            except KeyError:
                self.logger.warning("Failed to parse product JSON structure")
