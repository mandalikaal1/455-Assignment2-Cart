from flask import Flask, jsonify

import requests

app = Flask(__name__)

# this is the list of carts
carts = [
    {"cart_id": 1, "products": [{"prod_name": "tomatoes", "quantity": 1, "ind. price": 2.36},
                                {"prod_name": "dish soap", "quantity": 1, "ind. price": 4.68}], "total": 7.04},
    {"cart_id": 2, "products": [{"prod_name": "detergent", "quantity": 1, "ind. price": 10.12}], "total": 10.12},
    {"cart_id": 3, "products": [{"prod_name": "dish soap", "quantity": 1, "ind. price": 4.68}], "total": 4.68}
]


# endpoint 1: get all contents of a user's cart
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart = next((cart for cart in carts if cart["cart_id"] == user_id), None)
    if cart:
        return jsonify({"cart": cart})
    else:
        return jsonify({"error": "product not found"}), 404


# Endpoint 2: add a specified quantity of a product
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_products(user_id, product_id):
    # assume the specified quantity is 1
    cur = carts[user_id - 1]
    # we get the product
    prod = requests.get(f'https://product-service-7sej.onrender.com/products/{product_id}')
    prod2 = prod.json()
    # get the name of the product
    prod_name = prod.json()['name']
    # get the price of the product
    prod_price = prod2['price']
    # isolate the list of current products in the cart
    cur_products = cur['products']
    # this is a check. if there is not enough product to be added to the cart, this will happen.
    if prod2['quantity'] - 1 < 0:
        return jsonify("Specified amount cannot be added to the cart. There is not enough")
    # cycle through the products and compare the name. If the product that we want to add
    # more quantity of isn't in the cart, we have to add it
    count = -1
    index = -1
    for x in cur_products:
        count += 1
        if x['prod_name'] == prod_name:
            index = count
    # if the index is still -1 then that means that the product is not in the cart,
    # and we need to add it
    # check = next((cart for cart in cur['products'] if carts[0]['products']['prod_name'] == "dish soap"), None)
    if index == -1:
        cur['products'].append({"prod_name": prod_name, "quantity": 1, "ind. price": prod_price})
    # otherwise, we just increase the quantity
    else:
        # this adds 1 to the existing quantity of that product and adds 1 to the total price of that
        # product in that cart, taking into account the quantity of that product.
        cur['products'][index]['quantity'] += 1
        cur['products'][index]['ind. price'] = round(cur['products'][index]['ind. price'] + prod_price, 2)
    # add the unit price to the total of the cart
    total_price = round(cur['total'] + prod_price, 2)
    cur['total'] = total_price
    carts[user_id-1] = cur
    # we reduce the quantity of the product in product service
    prod2['quantity'] -= 1
    requests.post(f'https://product-service-7sej.onrender.com/products/{product_id}', json=prod2)
    return jsonify({"cart": carts[user_id - 1]}, "cart has been updated")


# Endpoint 3: remove a specified quantity of a product from a cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
# TODO: FOR SOME REASON THIS ISN'T TAKING. FIX IT
def remove_products(user_id, product_id):
    # assume the specified quantity is 1
    cur = carts[user_id - 1]
    # we get the product
    prod = requests.get(f'https://product-service-7sej.onrender.com/products/{product_id}')
    prod2 = prod.json()
    # get the name of the product
    prod_name = prod.json()['name']
    # get the price of the product
    prod_price = prod2['price']
    # isolate the list of current products in the cart
    cur_products = cur['products']
    # cycle through the products and compare the name. If the product that we want to remove
    # more quantity of isn't in the cart, then we throw an error
    count = -1
    index = -1
    for x in cur_products:
        count += 1
        if x['prod_name'] == prod_name:
            index = count
    # if the index is still -1, then that means the product is not in the cart.
    if index == -1:
        return jsonify("The specified product is not in the cart")
    else:
        # remove a unit of the product
        cur['products'][index]['quantity'] -= 1
        # subtract the individual price from the calculated price.
        cur['products'][index]['ind. price'] = round(cur['products'][index]['ind. price'] - prod_price, 2)
        # if the quantity of that product is now 0, remove it from the list of products in the cart.
        if cur['products'][index]['quantity'] == 0:
            cur['products'].remove(cur['products'][index])
        # subtract unit price from the total
        total_price = round(cur['total']-prod_price, 2)
        cur['total'] = total_price
        carts[user_id - 1] = cur
        # we add the quantity of the product back and save it.
        prod2['quantity'] += 1
        requests.post(f'https://product-service-7sej.onrender.com/products/{product_id}', json=prod2)
        return jsonify({"cart": carts[user_id - 1]}, "cart has been updated")


if __name__ == '__main__':
    app.run(debug=False)

