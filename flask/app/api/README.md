# HPC-GBJH dashboard  API
- [HPC-GBJH dashboard API]
  * [Usage](#usage)
    + [Inventory](#inventory)
    

## Usage
All responses will have the form
Content-Type application/json

Then an array [ {"column_name":value, "column":value... }, {...}]
for a single value or multiple values

### Inventory

**Definition** 

| Endpoint                       | Expected return                      |
|:-------------------------------|:-------------------------------------|
| `GET /api/inventory`           | - returns all inventory entries      |
[api/inventory](./inventory)
