import json

from scrapers import (
    parse_shopify,
    parse_jsonld,
    parse_jsonld_from_html,
    parse_metaprice,
)


SHOPIFY_BARE = {
    "id": 8461901463737,
    "title": "Ricoh GR IV HDF",
    "price": 238900,
    "variants": [{"id": 1, "price": 238900, "available": True}],
}

SHOPIFY_WRAPPED = {
    "product": {
        "title": "Ricoh GR IV HDF",
        "variants": [
            {"id": 1, "price": 237900, "available": True},
            {"id": 2, "price": 240000, "available": False},
        ],
    }
}


def test_parse_shopify_bare():
    result = parse_shopify(SHOPIFY_BARE)
    assert result["price"] == 2389.0
    assert result["available"] is True


def test_parse_shopify_wrapped_picks_lowest():
    result = parse_shopify(SHOPIFY_WRAPPED)
    assert result["price"] == 2379.0
    assert result["available"] is True


def test_parse_shopify_no_variants():
    assert parse_shopify({"variants": []}) is None


def test_parse_jsonld_backorder_not_available():
    data = [{
        "@type": "Product",
        "name": "Ricoh GR IV HDF Edition Camera",
        "offers": {
            "price": 2395.0,
            "priceCurrency": "AUD",
            "availability": "https://schema.org/BackOrder",
        },
    }]
    result = parse_jsonld(data)
    assert result["price"] == 2395.0
    assert result["available"] is False


def test_parse_jsonld_in_stock():
    data = {"@type": "Product", "offers": {
        "price": 1999.0, "availability": "https://schema.org/InStock"}}
    assert parse_jsonld(data)["available"] is True


def test_parse_jsonld_ignores_non_product():
    data = [{"@type": "BreadcrumbList"}, {"@type": "FAQPage"}]
    assert parse_jsonld(data) is None


def test_parse_metaprice():
    html = '<meta itemprop="price" content="2395" />'
    assert parse_metaprice(html)["price"] == 2395.0


def test_parse_metaprice_data_amount_fallback():
    html = '<span data-price-amount="2050" class="price-wrapper">$2,050.00</span>'
    assert parse_metaprice(html)["price"] == 2050.0


def test_parse_jsonld_from_html_extracts():
    html = ('<html><head><script type="application/ld+json">'
            + json.dumps({"@type": "Product", "offers": {
                "price": 2395.0,
                "availability": "https://schema.org/InStock"}})
            + '</script></head></html>')
    assert parse_jsonld_from_html(html)["price"] == 2395.0
