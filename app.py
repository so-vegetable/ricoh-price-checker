import time

from flask import Flask, jsonify, render_template

from scrapers import DELAY, scrape
from targets import TARGETS

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/prices")
def prices():
    results = []
    for target in TARGETS:
        item = {
            "model": target["model"],
            "retailer": target["retailer"],
            "url": target.get("url", ""),
            "price": None,
            "available": None,
            "error": None,
        }
        try:
            data = scrape(target)
            item["price"] = data["price"]
            item["available"] = data["available"]
        except Exception as exc:
            item["error"] = str(exc)
        results.append(item)
        time.sleep(DELAY)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
