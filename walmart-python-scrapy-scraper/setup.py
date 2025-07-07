from setuptools import setup, find_packages

setup(
    name="walmart_scrapy_spider",
    version="0.1.0",
    packages=["walmart_scraper", "walmart_scraper.spiders"],
    install_requires=[
        "scrapy>=2.0",
        "scrapeops-scrapy",
        "scrapeops-scrapy-proxy-sdk",
    ],
)
