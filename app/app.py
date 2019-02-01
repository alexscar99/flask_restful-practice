from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity


# Config app
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'examplekey123'

# Set up API and JWT
api = Api(app)
jwt = JWT(app, authenticate, identity)  # /auth

items = []


class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help="This field can't be left blank"
    )

    @jwt_required()
    def get(self, name):
        # 'next' gives first item matched by 'filter' or None if none match
        return {'item': next(filter(lambda x: x['name'] == name, items), None)}

    def post(self, name):
        # Check if item exists before posting
        if next(filter(lambda x: x['name'] == name, items), None):
            return {
                'message': f"An item with name '{name}' already exists"
            }, 400

        # Parse the args that come through JSON payload, put valid ones in data
        data = Item.parser.parse_args()

        item = {'name': name, 'price': data['price']}
        items.append(item)
        return item, 201

    def delete(self, name):
        # Python will think we are using the value of 'items' before it has
        # been defined, make global to reference the items list defined outside
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'Item deleted'}

    def put(self, name):
        # Parse the args that come through JSON payload, put valid ones in data
        data = Item.parser.parse_args()

        item = next(filter(lambda x: x['name'] == name, items), None)
        if item is None:
            item = {'name': name, 'price': data['price']}
            items.append(item)
        else:
            item.update(data)
        return item


class ItemList(Resource):

    def get(self):
        return {'items': items}


# Add resources to API
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')


if __name__ == '__main__':
    # Run in debug mode for the purposes of this app
    app.run(debug=True)
