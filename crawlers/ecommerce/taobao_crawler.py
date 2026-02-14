#!/usr/bin/env python3
"""
电商数据爬虫
支持淘宝/京东/拼多多/亚马逊等平台
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Product:
    """商品数据结构"""
    name: str
    price: float
    sales: str
    shop: str
    url: str
    platform: str


class EcommerceCrawler:
    """电商爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def crawl_taobao(self, keyword: str, pages: int = 5) -> List[Product]:
        """爬取淘宝商品"""
        products = []
        
        for page in range(1, pages + 1):
            url = f"https://s.taobao.com/search?q={keyword}&page={page}"
            
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'lxml')
                
                items = soup.select('.item')
                
                for item in items:
                    try:
                        name = item.select_one('.title').get_text(strip=True) if item.select_one('.title') else ''
                        price = item.select_one('.price').get_text(strip=True) if item.select_one('.price') else '0'
                        sales = item.select_one('.sales').get_text(strip=True) if item.select_one('.sales') else '0'
                        shop = item.select_one('.shop').get_text(strip=True) if item.select_one('.shop') else ''
                        url = item.select_one('a')['href'] if item.select_one('a') else ''
                        
                        products.append(Product(
                            name=name,
                            price=float(price.replace('¥', '')),
                            sales=sales,
                            shop=shop,
                            url=url,
                            platform='淘宝'
                        ))
                    except:
                        continue
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"爬取失败: {e}")
                continue
        
        return products
    
    def crawl_jd(self, keyword: str, pages: int = 5) -> List[Product]:
        """爬取京东商品"""
        products = []
        
        for page in range(1, pages + 1):
            url = f"https://search.jd.com/Search?keyword={keyword}&page={page}"
            
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'lxml')
                
                items = soup.select('.gl-item')
                
                for item in items:
                    try:
                        name = item.select_one('.p-name').get_text(strip=True) if item.select_one('.p-name') else ''
                        price = item.select_one('.p-price').get_text(strip=True) if item.select_one('.p-price') else '0'
                        shop = item.select_one('.p-shop').get_text(strip=True) if item.select_one('.p-shop') else ''
                        url = 'https:' + item.select_one('a')['href'] if item.select_one('a') else ''
                        
                        products.append(Product(
                            name=name,
                            price=float(price.replace('¥', '')),
                            sales='0',
                            shop=shop,
                            url=url,
                            platform='京东'
                        ))
                    except:
                        continue
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"爬取失败: {e}")
                continue
        
        return products
    
    def save_to_csv(self, products: List[Product], filename: str = 'products.csv'):
        """保存到CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['名称', '价格', '销量', '店铺', '链接', '平台'])
            
            for p in products:
                writer.writerow([p.name, p.price, p.sales, p.shop, p.url, p.platform])
        
        print(f"已保存 {len(products)} 个商品到 {filename}")
    
    def save_to_json(self, products: List[Product], filename: str = 'products.json'):
        """保存到JSON"""
        data = [{
            'name': p.name,
            'price': p.price,
            'sales': p.sales,
            'shop': p.shop,
            'url': p.url,
            'platform': p.platform
        } for p in products]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(products)} 个商品到 {filename}")


# 示例使用
if __name__ == "__main__":
    crawler = EcommerceCrawler()
    
    # 爬取淘宝
    print("爬取淘宝商品...")
    products = crawler.crawl_taobao("手机", pages=2)
    
    # 保存结果
    crawler.save_to_csv(products, 'taobao_products.csv')
    crawler.save_to_json(products, 'taobao_products.json')
    
    print(f"共爬取 {len(products)} 个商品")
