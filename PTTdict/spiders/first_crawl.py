# -*- coding: utf-8 -*-
import scrapy
import datetime
import socket
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, urljoin
from PTTdict.items import PropertiesItem

DENY_URLs = [r'\?veaction=edit', r'\?action=edit', r'/zh/wiki/%E7%89%B9%E6%AE%8A:', r'/zh/wiki/%E5%88%86%E9%A1%9E:']

class DictSpider(CrawlSpider):
    name = 'first_crawl'
    allowed_domains = ['pttpedia.fandom.com']
    start_urls = [
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E6%B5%81%E8%A1%8C%E7%94%A8%E8%AA%9E',  # 流行用語
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E6%96%87%E5%8C%96',  # 鄉民文化
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E6%B5%81%E8%A1%8C%E7%AC%A6%E8%99%9F',  # 流行符號
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E5%9F%BA%E6%9C%AC%E7%94%A8%E8%AA%9E',  # 基本用語
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E5%90%8D%E4%BA%BA',  # 名人
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E7%9C%8B%E6%9D%BF',  # 看板
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E4%BA%8B%E4%BB%B6',  # 事件
        'https://pttpedia.fandom.com/zh/wiki/%E5%88%86%E9%A1%9E:PTT%E7%9B%B8%E9%97%9C%E4%BA%8B%E7%89%A9',  # 相關事物\
        'https://pttpedia.fandom.com/zh/wiki/PTT%E7%9A%84%E5%90%84%E9%A1%9E%E6%96%87%E7%AB%A0',  # 各類文章
        
        # 隨機頁面
        'https://pttpedia.fandom.com/zh/wiki/PTT%E6%94%BF%E6%B2%BB%E4%BA%BA%E7%89%A9%E7%B6%BD%E8%99%9F%E5%88%97%E8%A1%A8',
        'https://pttpedia.fandom.com/zh/wiki/%E5%8F%8D%E6%9C%8D%E8%B2%BF%E6%94%BB%E4%BD%94%E7%AB%8B%E6%B3%95%E9%99%A2%E8%88%87ptt',
        'https://pttpedia.fandom.com/zh/wiki/%E7%B4%AB%E7%88%86'
    ]

    # Rules for Horizontal & vertical crawling
    rules = (
        Rule(LinkExtractor(restrict_css='.category-page__pagination-next',
                           deny=DENY_URLs)),  # horizontal
        Rule(LinkExtractor(restrict_css='.category-page__member-link',
                           deny=DENY_URLs), callback='parse_item'),  # vertical
        Rule(LinkExtractor(restrict_css='.mw-redirect',
                           deny=DENY_URLs), callback='parse_item'),
        Rule(LinkExtractor(restrict_xpaths='//a[@title]',
                           deny=DENY_URLs), callback='parse_item'),
    )


    # Scraping an individual page
    def parse_item(self, response):
        # Parse this page
        l = ItemLoader(item=PropertiesItem(), response=response)
        l.add_xpath('title', '//h1[@class="page-header__title"]/text()')
        l.add_xpath('bold', '//p/b/text()', re='.{2,}')
        # Match all words but '「' & '」' in 「 ... 」
        l.add_xpath('bracket', '//p/text()', re='「[^(「|」)]{2,}」')
        l.add_xpath('link_new', '//p/a[@class="new"]/text()', re='.{2,}')
        l.add_xpath('link_redr', '//a[@class="mw-redirect"]/text()')
        l.add_xpath('link_title', '//a[@title]/text()')

        # Housekeeping fields
        l.add_value('url', response.url)
        l.add_value('date', datetime.datetime.now())

        # Save extracted links
        links = LinkExtractor(restrict_xpaths=['//a[@class="mw-redirect"]', '//a[@title]'], deny=DENY_URLs).extract_links(response)
        with open('extracted_links.txt', 'a') as f:
            for link in links:
                if 'pttpedia.fandom.com' in link.url:
                    f.write(link.url + '\n')

        return l.load_item()