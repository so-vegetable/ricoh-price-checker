import json

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0 Safari/537.36"),
}
TIMEOUT = 10
DELAY = 0.5


# ---------- Shopify ----------

def parse_shopify(data):
    """解析 Shopify /products/<handle>.js 的 JSON。
    兼容带 "product" 外层和不带外层两种格式，返回 {price, available} 或 None。"""
    product = data.get("product", data)
    variants = product.get("variants") or []
    if not variants:
        return None
    prices = [int(v["price"]) / 100 for v in variants]
    available = any(v.get("available", False) for v in variants)
    return {"price": min(prices), "available": available}


def fetch_shopify(shop, handle):
    url = f"https://{shop}/products/{handle}.js"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return parse_shopify(resp.json())


# ---------- JSON-LD（Pentax 官方等） ----------

def parse_jsonld(data):
    """从 JSON-LD 里找 @type 含 Product 的项，提取价格。返回 {price, available} 或 None。"""
    items = data if isinstance(data, list) else [data]
    for item in items:
        if not isinstance(item, dict):
            continue
        if "Product" not in str(item.get("@type", "")):
            continue
        offers = item.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price = offers.get("price")
        if price is None:
            continue
        availability = str(offers.get("availability", ""))
        # 只有明确标 InStock 才算现货；BackOrder/OutOfStock/PreOrder 都不是
        available = (availability == "") or availability.endswith("InStock")
        return {"price": float(price), "available": available}
    return None


def parse_jsonld_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (TypeError, ValueError):
            continue
        result = parse_jsonld(data)
        if result:
            return result
    return None


# ---------- meta itemprop="price"（CameraPro / Magento） ----------

def parse_metaprice(html):
    """从 <meta itemprop="price"> 或 data-price-amount 提取价格。返回 {price, available} 或 None。"""
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", attrs={"itemprop": "price"})
    if tag and tag.get("content"):
        return {"price": float(tag["content"]), "available": True}
    el = soup.find(attrs={"data-price-amount": True})
    if el:
        return {"price": float(el["data-price-amount"]), "available": True}
    return None


# ---------- 通用 ----------

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text


def scrape(target):
    """根据 target 的 type 调用对应抓取逻辑，返回 {price, available}。"""
    t = target["type"]
    if t == "shopify":
        return fetch_shopify(target["shop"], target["handle"])
    if t == "jsonld":
        return parse_jsonld_from_html(fetch_html(target["url"]))
    if t == "metaprice":
        return parse_metaprice(fetch_html(target["url"]))
    raise ValueError(f"未知抓取类型: {t}")
