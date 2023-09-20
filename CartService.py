
from flask import Flask, jsonify, request

import requests

app = Flask(__name__)

carts = [
    {"cart_id": 1, "products": [{"prod_name": "tomatoes", "quantity": 1}, {"prod_id": "dish soap", "quantity": 1}],
     "total": 7.04},
    {"cart_id": 2, "products": {"prod_name": "detergent", "quantity": 1}, "total": 10.12},
    {"cart_id": 3, "products": {"prod_name": "dish soap", "quantity": 1}, "total": 4.68}
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
    cur = next((cart for cart in carts if cart["cart_id"] == user_id), None)
    prod = requests.get(f'https://product-service-7sej.onrender.com/products/{product_id}')
    prod2 = prod.json()
    prod_name = prod2['name']
    if prod2['quantity'] - 1 >= 0:
        cur_products = cur[user_id]['products']
        add_prod = next((add for add in cur_products if cur_products["prod_name"] == prod_name), None)
        cur[user_id - 1]['products']['add_prod'] += 1
        prod2['quantity'] -= 1
        requests.post(f'https://product-service-7sej.onrender.com/products/{product_id}', json=prod2)
        return jsonify("Product in cart is updated")
    else:
        return jsonify("error: specified quantity is not available")


# Endpoint 3: remove a specified quantity of a product from a cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_products(user_id, product_id):
    # assume the specified quantity is 1
    cur = get_cart(user_id)
    prod = requests.get(f'https://product-service-7sej.onrender.com/products/{product_id}')
    prod2 = prod.json()
    prod_name = prod2['name']
    cur_products = cur[user_id]['products']
    add_prod = next((add for add in cur_products if cur_products["prod_name"] == prod_name), None)
    cur[user_id - 1]['products']['add_prod'] -= 1
    prod2['quantity'] += 1
    requests.post(f'https://product-service-7sej.onrender.com/products/{product_id}', json=prod2)
    return jsonify("Product in cart is updated")


if __name__ == '__main__':
    app.run(debug=True)

# prod url: https://product-service-7sej.onrender.com

# f'http://127.0.0.1:5000/tasks/{task_id}'
