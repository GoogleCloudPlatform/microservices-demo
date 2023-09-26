Feature: E-commerce Website Test
  
  Scenario: Users session
	Given There are 9 users
	When All users start their sessions
	Then All sessions should complete successfully
  
  Scenario: Browse product
	Given A product list
	When A user browses products
	Then All products should be accessible
  
  Scenario: View cart
	When A user views their cart
	Then The cart page should be accessible
  
#  Scenario: Add to cart
#	Given A product list
#	When A user adds products to their cart
#	Then All products should be added successfully
  
#  Scenario: Check favicon and product image
#	When A user accesses site assets
#	Then The assets should be accessible
  
  Scenario: Checkout with products
	Given A product list
	When A user checks out with products
	Then The checkout should be successful
