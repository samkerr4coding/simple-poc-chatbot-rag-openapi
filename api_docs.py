import json

customer_api_docs = {
  "openapi": "3.0.0",
  "info": {
    "title": "Customer Services API",
    "version": "1.0",
    "description": "API Documentation for Customer Services"
  },
  "servers": [
    {
      "url": "http://localhost:5000",
      "description": "Local development server"
    }
  ],
  "paths": {
    "/customers/": {
      "get": {
        "summary": "List all customers",
        "operationId": "list_customers",
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Customer"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "summary": "Create a new customer",
        "operationId": "create_customer",
        "requestBody": {
          "required": "true",
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Customer"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Customer created successfully",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Customer"
                }
              }
            }
          },
          "400": {
            "description": "Validation Error"
          }
        }
      }
    },
    "/customers/{customer_id}": {
      "parameters": [
        {
          "name": "customer_id",
          "in": "path",
          "required": "true",
          "schema": {
            "type": "integer",
            "format": "int32"
          },
          "description": "The customer identifier"
        }
      ],
      "get": {
        "summary": "Fetch a given customer",
        "operationId": "get_customer",
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Customer"
                }
              }
            }
          },
          "404": {
            "description": "Customer not found"
          }
        }
      },
      "put": {
        "summary": "Update a customer",
        "operationId": "update_customer",
        "requestBody": {
          "required": "true",
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Customer"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Customer updated successfully",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Customer"
                }
              }
            }
          },
          "404": {
            "description": "Customer not found"
          },
          "400": {
            "description": "Validation Error"
          }
        }
      },
      "delete": {
        "summary": "Delete a customer",
        "operationId": "delete_customer",
        "responses": {
          "204": {
            "description": "Customer deleted successfully"
          },
          "404": {
            "description": "Customer not found"
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Customer": {
        "type": "object",
        "properties": {
          "id": {
            "type": "integer",
            "readOnly": "true",
            "description": "The customer unique identifier"
          },
          "name": {
            "type": "string",
            "description": "The customer name"
          },
          "email": {
            "type": "string",
            "description": "The customer email"
          }
        }
      }
    }
  }
}


customer_api_docs = json.dumps(customer_api_docs, indent=2)
