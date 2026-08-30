from backend.app.services.merchant_data_service import MerchantDataService


def test_products_are_loaded():
    service = MerchantDataService()

    products = service.get_all_products()

    assert len(products) == 8


def test_product_lookup():
    service = MerchantDataService()

    product = service.get_product("P001")

    assert product is not None
    assert product["product_name"] == "SoundMax Wireless Headphones"


def test_inventory_lookup():
    service = MerchantDataService()

    inventory = service.get_inventory("P002")

    assert inventory is not None
    assert inventory["available_quantity"] == "0"


def test_delivery_lookup():
    service = MerchantDataService()

    delivery = service.get_delivery_options("P003")

    assert delivery is not None
    assert delivery["standard_days"] == "3"


def test_policy_lookup():
    service = MerchantDataService()

    policy = service.get_merchant_policy("M001")

    assert policy is not None
    assert policy["max_discount_percent"] == "15"