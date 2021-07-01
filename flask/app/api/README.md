# HPC-GBJH dashboard  API

- [HPC-GBJH dashboard API]
  - [Usage](#usage)
    - [Inventory](#Inventory)
    - [cmdb](#CMDB)
    - [aws](#AWS)

## Usage

All responses will have the form
Content-Type application/json

Then an array [ {"column_name":value, "column":value... }, {...}]
for a single value or multiple values

### Inventory

#### Definition

| Endpoint                       | Expected return                               |
|:-------------------------------|:----------------------------------------------|
| `GET /api/inventory`           | - returns all inventory entries               |
| `GET /api/inventory/hostid`    | - returns inventory entries for specific host |

#### Example(s)

[api/inventory](./inventory)

[api/inventory/gbjhvice066](./inventory/gbjhvice066)

### CMDB

#### Definition

| Endpoint             | Expected return                               |
|:---------------------|:----------------------------------------------|
| `GET /api/cmdb`      | - returns all inventory cmdb style flat JSON  |

#### Example

[api/cmdb](./cmdb)

### AWS

#### Definition

| Endpoint             | Expected return                               |
|:---------------------|:----------------------------------------------|
| `GET /api/aws`       | - returns all aws inventory style flat JSON   |

#### Example

[api/aws](./aws)
