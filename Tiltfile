# Disable Titl analytics
analytics_settings(enable=False)

# Disable Tilt redacted secret
secret_settings(disable_scrub=True)

# Load Tilt extensions (https://github.com/tilt-dev/tilt-extensions)
load('ext://restart_process', 'docker_build_with_restart')

# Check if Kubernetes context is set to docker-desktop
if k8s_context() != 'docker-desktop':
    fail('Kubernetes context is not set to docker-desktop')

# Function to remove security context from yaml before applying
# Tilt does not support security context
def remove_security_context(yaml):
    objects = read_yaml_stream(yaml)
    for o in objects:
        if o['kind'] == 'Deployment':
            o['spec']['template']['spec']['securityContext'] = {}
            o['spec']['template']['spec']['containers'][0]['securityContext'] = {}
    k8s_yaml(encode_yaml_stream(objects))

# Kubernetes manifests
yamls = [
    './kubernetes-manifests/frontend.yaml',
    './kubernetes-manifests/cartservice.yaml',
    './kubernetes-manifests/productcatalogservice.yaml',
    './kubernetes-manifests/currencyservice.yaml',
    './kubernetes-manifests/paymentservice.yaml',
    './kubernetes-manifests/shippingservice.yaml',
    './kubernetes-manifests/emailservice.yaml',
    './kubernetes-manifests/checkoutservice.yaml',
    './kubernetes-manifests/recommendationservice.yaml',
    './kubernetes-manifests/adservice.yaml',
    './kubernetes-manifests/redis.yaml',
]

# Remove security context and apply Kubernetes manifests
for yaml in yamls:
    remove_security_context(yaml)

###
# Service: frontend
# Desc: Exposes an HTTP server to serve the website
#       Does not require signup/login and generates session IDs
#       for all users automatically
# Language: Go
###
docker_build_with_restart('frontend', context='./src/frontend',
    entrypoint='/src/server',
    live_update=[
        sync('./src/frontend', '/src'),
    ],
)

###
# Service: cartservice
# Desc: Stores the items in the user's shopping cart in Redis and retrieves it
# Language: C#
###
docker_build_with_restart('cartservice', context='./src/cartservice/src',
    entrypoint='/app/cartservice',
    live_update=[
        sync('./src/cartservice/src', '/app'),
    ],
)

###
# Service: productcatalogservice
# Desc: Provides the list of products from a JSON file and
#       ability to search products and get individual products
# Language: Go
###
docker_build_with_restart('productcatalogservice',
    context='./src/productcatalogservice',
    entrypoint='/src/server',
    live_update=[
        sync('./src/productcatalogservice', '/src'),
    ],
)

###
# Service: currencyservice
# Desc: Converts one money amount to another currency.
#       Uses real values fetched from European Central Bank.
#       It's the highest QPS service
# Language: Node.js
###
docker_build_with_restart('currencyservice',
    context='./src/currencyservice',
    entrypoint='node /usr/src/app/server.js',
    live_update=[
        sync('./src/currencyservice', '/usr/src/app'),
        run('cd /usr/src/app && npm install', trigger=['./src/currencyservice/package.json']),
    ]
)

###
# Service: paymentservice
# Desc: Charges the given credit card info (mock) with the given amount
#       and returns a transaction ID
# Language: Node.js
###
docker_build_with_restart('paymentservice',
    context='./src/paymentservice',
    entrypoint='node /usr/src/app/index.js',
    live_update=[
        sync('./src/paymentservice', '/usr/src/app'),
        run('cd /usr/src/app && npm install', trigger=['./src/paymentservice/package.json']),
    ]
)

###
# Service: shippingservice
# Desc: Gives shipping cost estimates based on the shopping cart.
#       Ships items to the given address (mock)
# Language: Go
###
docker_build_with_restart('shippingservice',
    context='./src/shippingservice',
    entrypoint='/src/shippingservice',
    live_update=[
        sync('./src/shippingservice', '/src'),
    ],
)

###
# Service: emailservice
# Desc: Sends users an order confirmation email (mock)
# Language: Python
###
docker_build('emailservice',
    context='./src/emailservice',
    live_update=[
        sync('./src/emailservice', '/email_server'),
        run('cd /email_server && pip install -r requirements.txt',
            trigger='./src/emailservice/requirements.txt'),
    ],
)

###
# Service: checkoutservice
# Desc: Retrieves user cart, prepares order and orchestrates the payment,
#       shipping and the email notification
# Language: Go
###
docker_build_with_restart('checkoutservice',
    context='./src/checkoutservice',
    entrypoint='/src/checkoutservice',
    live_update=[
        sync('./src/checkoutservice', '/src'),
    ],
)

###
# Service: recommendationservice
# Desc: Recommends other products based on what's given in the cart
# Language: Python
###
docker_build('recommendationservice',
    context='./src/recommendationservice',
    live_update=[
        sync('./src/recommendationservice', '/recommendationservice'),
        run('cd /recommendationservice && pip install -r requirements.txt',
            trigger='./src/recommendationservice/requirements.txt'),
    ],
)

###
# Service: adservice
# Desc: Provides text ads based on given context words
# Language: Java
###
docker_build_with_restart('adservice',
    context='./src/adservice',
    entrypoint='/app/build/install/hipstershop/bin/AdService',
    live_update=[
        sync('./src/adservice', '/app'),
    ],
)
