from flask import Flask, jsonify, request
import requests

app = Flask(__name__)


HEADERS = {"User-Agent": "InventoryManagementApp/1.0 (github.com/irene419)"}

inventory = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "brand": "Brookside Dairy",
        "price": 3.99,
        "stock": 25,
        "barcode": "0025293001165"
    },
    {
        "id": 2,
        "name": "Green Tea",
        "brand": "Ketepa",
        "price": 1.49,
        "stock": 40,
        "barcode": "0051500255511"
    }
]

next_id = 3  


def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


# GET /inventory - fetch all items
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory)


# GET
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": f"No item with id {item_id}"}), 404
    return jsonify(item)


# POST 
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Item must have at least a 'name'"}), 400

    new_item = {
        "id": next_id,
        "name": data["name"],
        "brand": data.get("brand", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0),
        "barcode": data.get("barcode", "")
    }
    inventory.append(new_item)
    next_id += 1

    return jsonify(new_item), 201


# PATCH 
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": f"No item with id {item_id}"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

   
    for field in ["name", "brand", "price", "stock", "barcode"]:
        if field in data:
            item[field] = data[field]

    return jsonify(item)


# DELETE
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": f"No item with id {item_id}"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200



@app.route("/inventory/lookup/<barcode>", methods=["GET"])
def lookup_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
    except requests.exceptions.RequestException:
        return jsonify({"error": "Could not reach OpenFoodFacts"}), 502

    try:
        data = response.json()
    except ValueError:
        return jsonify({"error": "OpenFoodFacts returned an invalid response"}), 502

    if data.get("status") != 1:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    product = data["product"]
    result = {
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", "Unknown"),
        "barcode": barcode,
        "ingredients": product.get("ingredients_text", "")
    }
    return jsonify(result)

# POST AND add it straight into our inventory
@app.route("/inventory/lookup/<barcode>", methods=["POST"])
def lookup_and_add(barcode):
    global next_id
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
    except requests.exceptions.RequestException:
        return jsonify({"error": "Could not reach OpenFoodFacts"}), 502

    try:
        data = response.json()
    except ValueError:
        return jsonify({"error": "OpenFoodFacts returned an invalid response"}), 502

    if data.get("status") != 1:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    product = data["product"]
    new_item = {
        "id": next_id,
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", "Unknown"),
        "price": 0,      
        "stock": 0,      
        "barcode": barcode
    }
    inventory.append(new_item)
    next_id += 1

    return jsonify(new_item), 201


if __name__ == "__main__":
    app.run(debug=True)