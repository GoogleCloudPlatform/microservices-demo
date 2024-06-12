# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

table_name = "catalog_items"
fields = [
    'id', 'name', 'description', 'picture', 
    'price_usd_currency_code', 'price_usd_units', 'price_usd_nanos', 
    'categories'
]

# Load the produts JSON
with open("products.json", 'r') as f:
    data = json.load(f)

# Generate SQL INSERT statements
for product in data['products']:
    columns = ', '.join(fields)
    placeholders = ', '.join(['{}'] * len(fields))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

    # Escape single quotes within product data 
    product['name'] = product['name'].replace("'", "")
    product['description'] = product['description'].replace("'", "")

    escaped_values = (
        f"'{product['id']}'",
        f"'{product['name']}'",
        f"'{product['description']}'",
        f"'{product['picture']}'",
        f"'{product['priceUsd']['currencyCode']}'",
        product['priceUsd']['units'],
        product['priceUsd']['nanos'],
        f"'{','.join(product['categories'])}'"
    )

    # Render the formatted SQL query
    print(sql.format(*escaped_values))
