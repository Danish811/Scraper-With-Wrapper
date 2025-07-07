#!/usr/bin/env python3
"""
Test script for the Walmart scraper
"""

import sys
import os

# Add the walmart-python-scrapy-scraper directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'walmart-python-scrapy-scraper'))

from utils.scraper import run_walmart_search

def main():
    print("Testing Walmart Scraper...")
    print("=" * 50)
    
    try:
        # Test with a simple search term and small limit
        results = run_walmart_search("laptop", limit=5)
        
        print(f"\nScraping Results:")
        print(f"Total products found: {len(results)}")
        
        if results:
            print("\nFirst product details:")
            first_product = results[0]
            for key, value in first_product.items():
                print(f"  {key}: {value}")
        else:
            print("No products were scraped.")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 