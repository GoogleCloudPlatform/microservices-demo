# Python Clients with VScode
This folder holds python clients and a container configuration with docker compose and VScode.

## Container Configuration
The development container is configured with a docker compose file to run in the host network with the
sample services added as known fqdn in the /etc/hosts file of the container

# VScode Environmant

## Install VScode
[Download VScode](https://code.visualstudio.com/docs/?dv=osx)

## Install VSCode Extension
- Remote - Containers

## Add VScode cli "code" to PATH
To do this, press CMD + SHIFT + P, type shell command and select Install code command in path.<br/>

```
Afterwards, navigate to any project from the terminal and type "code ." from the directory to launch the project using VS Code.
```

## Select Open Folder In Container
VScode will launch the workspace in a container running the network inthe host network namespace.


## Activate the terminal in VScode to run the tetst.

```
python addCart.py
```

Expected Result
```
"sucessfully added 5 products to cart for user abcde"
```

```
python getProducts.py
```

Expected Result
```
product catalog printed
```

```
python placeOrder.py
```

Expected Result
```
Successfully placed order.

OrderResult(order_id='440ae577-14ad-495f-9828-84499202670e', shipping_tracking_id='ef5920bc-9204-42cd-be2d-4b95a053370e', shipping_cost=Money(currency_code='USD', units=10, nanos=100), shipping_address=Address(street_address='1600 Amp street', city='Mountain View', state='CA', country='USA', zip_code=94043), items=[OrderItem(item=CartItem(product_id='OLJCESPC7Z', quantity=37), cost=Money(currency_code='USD', units=19, nanos=990000000))]

```

