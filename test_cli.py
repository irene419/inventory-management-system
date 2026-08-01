from unittest.mock import Mock
import cli


def test_view_inventory_prints_items(capsys, mocker):
    fake_response = Mock()
    fake_response.json.return_value = [
        {"id": 1, "name": "Almond Milk", "brand": "Silk", "price": 3.99, "stock": 25}
    ]
    mocker.patch("cli.requests.get", return_value=fake_response)

    cli.view_inventory()

    captured = capsys.readouterr()
    assert "Almond Milk" in captured.out


def test_view_inventory_empty(capsys, mocker):
    fake_response = Mock()
    fake_response.json.return_value = []
    mocker.patch("cli.requests.get", return_value=fake_response)

    cli.view_inventory()

    captured = capsys.readouterr()
    assert "Inventory is empty." in captured.out


def test_add_item_success(capsys, mocker):
    # simulate the user typing: name, brand, price, stock
    mocker.patch("builtins.input", side_effect=["Eggs", "Farmhouse", "5.5", "12"])

    fake_response = Mock()
    fake_response.status_code = 201
    fake_response.json.return_value = {"id": 3, "name": "Eggs"}
    mock_post = mocker.patch("cli.requests.post", return_value=fake_response)

    cli.add_item()

    captured = capsys.readouterr()
    assert "Added 'Eggs' with id 3." in captured.out
    mock_post.assert_called_once()


def test_add_item_no_name_cancels(capsys, mocker):
    mocker.patch("builtins.input", side_effect=[""])
    mock_post = mocker.patch("cli.requests.post")

    cli.add_item()

    captured = capsys.readouterr()
    assert "Name is required" in captured.out
    mock_post.assert_not_called()


def test_add_item_invalid_price_defaults_to_zero(capsys, mocker):
    mocker.patch("builtins.input", side_effect=["Eggs", "Farmhouse", "notanumber", "12"])

    fake_response = Mock()
    fake_response.status_code = 201
    fake_response.json.return_value = {"id": 3, "name": "Eggs"}
    mocker.patch("cli.requests.post", return_value=fake_response)

    cli.add_item()

    captured = capsys.readouterr()
    assert "Invalid price, defaulting to 0." in captured.out


def test_update_item_success(capsys, mocker):
    mocker.patch("cli.requests.get", return_value=Mock(json=lambda: []))
    mocker.patch("builtins.input", side_effect=["1", "10.0", "5"])

    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"name": "Eggs", "price": 10.0, "stock": 5}
    mock_patch = mocker.patch("cli.requests.patch", return_value=fake_response)

    cli.update_item()

    captured = capsys.readouterr()
    assert "Updated 'Eggs'" in captured.out
    mock_patch.assert_called_once()


def test_update_item_bad_input_cancels(capsys, mocker):
    mocker.patch("cli.requests.get", return_value=Mock(json=lambda: []))
    mocker.patch("builtins.input", side_effect=["1", "notanumber", "5"])
    mock_patch = mocker.patch("cli.requests.patch")

    cli.update_item()

    captured = capsys.readouterr()
    assert "must be numbers" in captured.out
    mock_patch.assert_not_called()


def test_delete_item_confirmed(capsys, mocker):
    mocker.patch("cli.requests.get", return_value=Mock(json=lambda: []))
    mocker.patch("builtins.input", side_effect=["2", "y"])

    fake_response = Mock()
    fake_response.status_code = 200
    mock_delete = mocker.patch("cli.requests.delete", return_value=fake_response)

    cli.delete_item()

    captured = capsys.readouterr()
    assert "Item 2 deleted." in captured.out
    mock_delete.assert_called_once()


def test_delete_item_cancelled(capsys, mocker):
    mocker.patch("cli.requests.get", return_value=Mock(json=lambda: []))
    mocker.patch("builtins.input", side_effect=["2", "n"])
    mock_delete = mocker.patch("cli.requests.delete")

    cli.delete_item()

    captured = capsys.readouterr()
    assert "Cancelled." in captured.out
    mock_delete.assert_not_called()


def test_find_on_api_found(capsys, mocker):
    mocker.patch("builtins.input", side_effect=["3017620422003", "n"])

    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "name": "Nutella", "brand": "Ferrero", "ingredients": "Sugar, cocoa"
    }
    mocker.patch("cli.requests.get", return_value=fake_response)

    cli.find_on_api()

    captured = capsys.readouterr()
    assert "Found: Nutella" in captured.out


def test_find_on_api_not_found(capsys, mocker):
    mocker.patch("builtins.input", side_effect=["0000000000000"])

    fake_response = Mock()
    fake_response.status_code = 404
    mocker.patch("cli.requests.get", return_value=fake_response)

    cli.find_on_api()

    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()