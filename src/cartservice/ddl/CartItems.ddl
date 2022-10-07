CREATE TABLE CartItems (
  userId STRING(1024),
  productId STRING(1024),
  quantity INT64,
) PRIMARY KEY (userId, productId);

CREATE INDEX CartItemsByUserId ON CartItems(userId);
