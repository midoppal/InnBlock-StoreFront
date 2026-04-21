# Commands
## Start Site
```
uvicorn app.main:app --reload
```
## Get all products
### Example request
```
GET /products
```
### Example Response
```
[
  {
    "id": 1,
    "name": "Basic Black T-Shirt",
    "description": "Soft cotton t-shirt for everyday wear.",
    "price": 19.99,
    "stock": 25,
    "image_url": "https://via.placeholder.com/300x200?text=Black+T-Shirt",
    "is_active": true
  }.
  {
    "id": 2,
    "name": "Gloves",
    "description": "Fingers.",
    "price": 29.99,
    "stock": 35,
    "image_url": "https://via.placeholder.com/300x200?text=Black+T-Shirt",
    "is_active": true
  }
]
```

## Get one product
### Example request
```
GET /products/1
```
### Example Response
```
[
  {
    "id": 1,
    "name": "Basic Black T-Shirt",
    "description": "Soft cotton t-shirt for everyday wear.",
    "price": 19.99,
    "stock": 25,
    "image_url": "https://via.placeholder.com/300x200?text=Black+T-Shirt",
    "is_active": true
  }
]
```

## POST /orders

### Request body
```
{
  "customer_name": "Milin Doppalapudi",
  "customer_email": "milin@example.com",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}
```
### Response body
```
{
  "id": 5,
  "customer_name": "Milin Doppalapudi",
  "customer_email": "milin@example.com",
  "total_amount": 64.97,
  "created_at": "2026-04-20T16:20:00.000000+00:00",
  "items": [
    {
      "id": 8,
      "product_id": 1,
      "quantity": 2,
      "price_at_purchase": 19.99
    },
    {
      "id": 9,
      "product_id": 3,
      "quantity": 1,
      "price_at_purchase": 24.99
    }
  ]
}
```
