# Inventory Management System

A REST API and CLI tool for managing a small retail store's inventory, built with Flask. Employees can add, update, and remove stock, and can pull real product details (name, brand, ingredients) from the OpenFoodFacts database by scanning a barcode, instead of typing product info in by hand.

## Features

- Full CRUD REST API for inventory items
- Barcode lookup against the [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/)
- Command-line interface for interacting with the API without needing Postman or curl
- Test suite covering both the API and the CLI, with external API calls mocked

## Setup and Installation

Clone the repo:

```bash
git clone git@github.com:irene419/inventory-management-system.git
cd inventory-management-system
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Running the API

```bash
python app.py
```

The server runs at `http://localhost:5000`.

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/inventory` | Get all inventory items |
| GET | `/inventory/<id>` | Get a single item by id |
| POST | `/inventory` | Add a new item |
| PATCH | `/inventory/<id>` | Update an existing item (name, brand, price, stock, barcode) |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/inventory/lookup/<barcode>` | Look up a product on OpenFoodFacts by barcode (does not save it) |
| POST | `/inventory/lookup/<barcode>` | Look up a product on OpenFoodFacts and add it directly to inventory |

### Example: Add an item

Request:
```bash
curl -X POST http://localhost:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"name": "Green Tea", "brand": "Ketepa", "price": 1.49, "stock": 40}'
```

Response (201):
```json
{
  "id": 3,
  "name": "Green Tea",
  "brand": "Ketepa",
  "price": 1.49,
  "stock": 40,
  "barcode": ""
}
```

### Example: Look up a product by barcode

```bash
curl http://localhost:5000/inventory/lookup/3017620422003
```

Returns the product's name, brand, and ingredients pulled live from OpenFoodFacts.

## Using the CLI

With the Flask server running in one terminal, open a second terminal (with the virtual environment activated) and run:

```bash
python cli.py
```

You'll see a menu:
=== Inventory Management CLI ===

View inventory
Add new item
Update item price/stock
Delete item
Find item on OpenFoodFacts
Exit

- **View inventory** — lists every item currently in stock
- **Add new item** — prompts for name, brand, price, and stock
- **Update item** — shows the current inventory, then lets you change an item's price and/or stock by id
- **Delete item** — shows the inventory, asks for an id, and confirms before deleting
- **Find item on OpenFoodFacts** — enter a barcode to look up real product info, with the option to add it straight to inventory

## Running Tests

```bash
pytest -v
```

This runs the full suite (API + CLI), 23 tests in total. External calls to OpenFoodFacts are mocked in the tests, so the test suite runs without needing an internet connection or the Flask server running.

## Project Structure

inventory-management-system/
├── app.py # Flask REST API
├── cli.py # Command-line interface
├── test_app.py # Tests for the API
├── test_cli.py # Tests for the CLI
├── requirements.txt
└── README.md