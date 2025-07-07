# utils/scraper.py
import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from scrapy.signalmanager import dispatcher
import logging

def run_walmart_search(search_term: str, limit: int = 20) -> list:
    """
    Run Walmart search scraper with the given search term and limit.
    
    Args:
        search_term (str): The search term to look for on Walmart
        limit (int): Maximum number of products to scrape (default: 20)
    
    Returns:
        list: List of scraped product dictionaries
    """
    results = []
    
    def collect_item(item, response, spider):
        if len(results) < limit:
            results.append(dict(item))
            print(f"Scraped product {len(results)}/{limit}: {item.get('name', 'Unknown')}")
        else:
            spider.crawler.engine.close_spider(spider, reason='limit_reached')
    
    # Connect the signal handler
    dispatcher.connect(collect_item, signal=signals.item_scraped)
    
    try:
        # Change to the walmart project directory to load correct settings
        original_cwd = os.getcwd()
        walmart_project_path = os.path.join(os.path.dirname(__file__), '..', 'walmart-python-scrapy-scraper')
        os.chdir(walmart_project_path)
        
        # Get project settings from the walmart project
        settings = get_project_settings()
        
        # Import the spider from the project
        from walmart_scraper.spiders.walmart import WalmartSpider
        
        # Create crawler process with the correct settings
        process = CrawlerProcess(settings)
        
        # Start the spider with the custom keyword
        process.crawl(WalmartSpider, custom_keyword=search_term)
        
        print(f"Starting Walmart scraper for search term: '{search_term}'")
        print(f"Limit: {limit} products")
        print(f"Using project settings from: {walmart_project_path}")
        
        # Start the crawling process
        process.start()
        
        print(f"Scraping completed. Found {len(results)} products.")
        return results
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return results
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        # Disconnect the signal handler
        dispatcher.disconnect(collect_item, signal=signals.item_scraped)

# Test code (remove this in production)
if __name__ == "__main__":
    res = run_walmart_search("laptop", limit=5)
    print(f"Final results: {len(res)} products")
    if res:
        print("First product:", res[0].get('name', 'Unknown'))