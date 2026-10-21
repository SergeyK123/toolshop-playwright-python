FIRST_TERM = "Pliers"
SECOND_TERM = "Hammer"
EXPECTED_CHEAPER = SECOND_TERM   


def test_two_products_can_be_compared_by_price(product_page):
    product_page.open_catalog()
    product_page.search(FIRST_TERM)
    product_page.open_by_name(FIRST_TERM)
    first = product_page.read_details()

    product_page.open_catalog()
    product_page.search(SECOND_TERM)
    product_page.open_by_name(SECOND_TERM)
    second = product_page.read_details()

    
    assert FIRST_TERM.lower() in first["name"].lower()
    assert SECOND_TERM.lower() in second["name"].lower()
    assert first["name"] != second["name"]
    assert first["price"] > 0 and second["price"] > 0

   
    cheaper = min((first, second), key=lambda p: p["price"])
    assert EXPECTED_CHEAPER.lower() in cheaper["name"].lower()
    assert second["price"] < first["price"], (
        f"{second['name']} ({second['price']}) should be cheaper than "
        f"{first['name']} ({first['price']})"
    )