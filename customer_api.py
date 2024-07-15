import json
from flask import Flask, Response, jsonify
from flask_restx import Api, Resource, fields
import yaml

from api_docs import customer_api_docs

app = Flask(__name__)
api = Api(app, version='1.0', title='Customer Services API',
          description='API Documentation for Customer Services')

ns = api.namespace('customers', description='Customer operations')

# Define the model for the Customer
customer_model = api.model('Customer', {
    'id': fields.Integer(readonly="true", description='The customer unique identifier'),
    'name': fields.String(required="true", description='The customer name'),
    'email': fields.String(required="true", description='The customer email')
})

# Sample in-memory storage for customers
customers = {}

# Endpoint to serve OpenAPI JSON
@app.route('/openapi.json')
def get_openapi_json():
    return customer_api_docs

@ns.route('/')
class CustomerList(Resource):
    '''Shows a list of all customers and allows creation of new customers'''

    @ns.doc('list_customers', summary='List all customers', description='Retrieve a list of all customers in the system.')
    @ns.marshal_list_with(customer_model)
    @ns.response(200, 'Success')
    def get(self):
        '''List all customers'''
        return list(customers.values())

    @ns.doc('create_customer', summary='Create a new customer', description='Create a new customer with the provided information.')
    @ns.expect(customer_model)
    @ns.marshal_with(customer_model, code=201)
    @ns.response(201, 'Customer created successfully')
    @ns.response(400, 'Validation Error')
    def post(self):
        '''Create a new customer'''
        data = api.payload
        customer_id = len(customers) + 1
        data['id'] = customer_id
        customers[customer_id] = data
        return data, 201


@ns.route('/<int:customer_id>')
@ns.response(404, 'Customer not found')
@ns.param('customer_id', 'The customer identifier')
class Customer(Resource):
    '''Show a single customer, update it, or delete it'''

    @ns.doc('get_customer', summary='Fetch a given customer', description='Fetch details of a specific customer using their ID.')
    @ns.marshal_with(customer_model)
    @ns.response(200, 'Success')
    @ns.response(404, 'Customer not found')
    def get(self, customer_id):
        '''Fetch a given customer'''
        if customer_id in customers:
            return customers[customer_id]
        api.abort(404)

    @ns.doc('delete_customer', summary='Delete a customer', description='Delete a customer with the specified ID.')
    @ns.response(204, 'Customer deleted successfully')
    @ns.response(404, 'Customer not found')
    def delete(self, customer_id):
        '''Delete a customer given its identifier'''
        if customer_id in customers:
            del customers[customer_id]
            return '', 204
        api.abort(404)

    @ns.doc('update_customer', summary='Update a customer', description='Update the information of a specific customer using their ID.')
    @ns.expect(customer_model)
    @ns.marshal_with(customer_model)
    @ns.response(200, 'Customer updated successfully')
    @ns.response(404, 'Customer not found')
    @ns.response(400, 'Validation Error')
    def put(self, customer_id):
        '''Update a customer given its identifier'''
        if customer_id in customers:
            data = api.payload
            customers[customer_id].update(data)
            return customers[customer_id]
        api.abort(404)


# Add the namespace to the API
api.add_namespace(ns)

if __name__ == '__main__':
    app.run(debug="true")