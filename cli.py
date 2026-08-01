import requests

BASE_URL = "http://localhost:5000"


def view_inventory():
    response = requests.get(f"{BASE_URL}/inventory")
    items = response.json()

    if not items:
        print("Inventory is empty.")
        return

    print("\n--- Inventory ---")
    for item in items:
        print(f"[{item['id']}] {item['name']} ({item['brand']}) "
              f"- ${item['price']} - stock: {item['stock']}")


def add_item():
    print("\n--- Add New Item ---")
    name = input("Name: ").strip()

    if not name:
        print("Name is required, cancelling.")
        return

    brand = input("Brand (optional): ").strip()

    price_input = input("Price (optional): ").strip()
    try:
        price = float(price_input) if price_input else 0
    except ValueError:
        print("Invalid price, defaulting to 0.")
        price = 0

    stock_input = input("Stock quantity (optional): ").strip()
    try:
        stock = int(stock_input) if stock_input else 0
    except ValueError:
        print("Invalid stock number, defaulting to 0.")
        stock = 0

    new_item = {"name": name, "brand": brand, "price": price, "stock": stock}
    response = requests.post(f"{BASE_URL}/inventory", json=new_item)

    if response.status_code == 201:
        item = response.json()
        print(f"Added '{item['name']}' with id {item['id']}.")
    else:
        print(f"Something went wrong: {response.json().get('error')}")


def update_item():
    print("\n--- Update Item ---")
    view_inventory()
    item_id = input("\nEnter the id of the item to update: ").strip()

    print("Leave a field blank to leave it unchanged.")
    price_input = input("New price: ").strip()
    stock_input = input("New stock: ").strip()

    updates = {}
    try:
        if price_input:
            updates["price"] = float(price_input)
        if stock_input:
            updates["stock"] = int(stock_input)
    except ValueError:
        print("Price and stock must be numbers. Cancelling update.")
        return

    if not updates:
        print("Nothing to update.")
        return

    response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=updates)

    if response.status_code == 200:
        item = response.json()
        print(f"Updated '{item['name']}' - price: ${item['price']}, stock: {item['stock']}")
    elif response.status_code == 404:
        print(f"No item with id {item_id}.")
    else:
        print(f"Something went wrong: {response.json().get('error')}")


def delete_item():
    print("\n--- Delete Item ---")
    view_inventory()
    item_id = input("\nEnter the id of the item to delete: ").strip()

    confirm = input(f"Are you sure you want to delete item {item_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    response = requests.delete(f"{BASE_URL}/inventory/{item_id}")

    if response.status_code == 200:
        print(f"Item {item_id} deleted.")
    elif response.status_code == 404:
        print(f"No item with id {item_id}.")
    else:
        print(f"Something went wrong: {response.json().get('error')}")


def find_on_api():
    print("\n--- Look Up Product by Barcode ---")
    barcode = input("Enter barcode: ").strip()

    if not barcode:
        print("Barcode is required.")
        return

    response = requests.get(f"{BASE_URL}/inventory/lookup/{barcode}")

    if response.status_code == 404:
        print("Product not found on OpenFoodFacts.")
        return
    elif response.status_code != 200:
        print(f"Something went wrong: {response.json().get('error')}")
        return

    product = response.json()
    print(f"\nFound: {product['name']} ({product['brand']})")
    if product.get("ingredients"):
        print(f"Ingredients: {product['ingredients']}")

    add_choice = input("\nAdd this to inventory? (y/n): ").strip().lower()
    if add_choice == "y":
        add_response = requests.post(f"{BASE_URL}/inventory/lookup/{barcode}")
        if add_response.status_code == 201:
            item = add_response.json()
            print(f"Added '{item['name']}' with id {item['id']}. "
                  f"You can update its price and stock from the update menu.")
        else:
            print("Failed to add item.")


def main():
    while True:
        print("\n=== Inventory Management CLI ===")
        print("1. View inventory")
        print("2. Add new item")
        print("3. Update item price/stock")
        print("4. Delete item")
        print("5. Find item on OpenFoodFacts")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            view_inventory()
        elif choice == "2":
            add_item()
        elif choice == "3":
            update_item()
        elif choice == "4":
            delete_item()
        elif choice == "5":
            find_on_api()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()