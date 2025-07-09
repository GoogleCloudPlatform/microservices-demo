CREATE TABLE products (
  id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  picture VARCHAR(255),
  price_usd_currency_code CHAR(3) NOT NULL,
  price_usd_units INT NOT NULL,
  price_usd_nanos INT NOT NULL,
  categories JSON NOT NULL
);

INSERT INTO products (id, name, description, picture, price_usd_currency_code, price_usd_units, price_usd_nanos, categories) VALUES
('0PUK6V6EV0', 'Candle Holder', 'This small but intricate candle holder is an excellent gift.', '/static/img/products/candle-holder.jpg', 'USD', 18, 990000000, '["decor", "home"]'),
('1YMWWN1N4O', 'Watch', 'This gold-tone stainless steel watch will work with most of your outfits.', '/static/img/products/watch.jpg', 'USD', 109, 990000000, '["accessories"]'),
('2ZYFJ3GM2N', 'Hairdryer', 'This lightweight hairdryer has 3 heat and speed settings. It''s perfect for travel.', '/static/img/products/hairdryer.jpg', 'USD', 24, 990000000, '["hair", "beauty"]'),
('66VCHSJNUP', 'Tank Top', 'Perfectly cropped cotton tank, with a scooped neckline.', '/static/img/products/tank-top.jpg', 'USD', 18, 990000000, '["clothing", "tops"]'),
('6E92ZMYYFZ', 'Mug', 'A simple mug with a mustard interior.', '/static/img/products/mug.jpg', 'USD', 16, 500000000, '["kitchen"]'),
('9SIQT8TOJO', 'Bamboo Glass Jar', 'This bamboo glass jar can hold 57 oz (1.7 l) and is perfect for any kitchen.', '/static/img/products/bamboo-glass-jar.jpg', 'USD', 5, 490000000, '["kitchen"]'),
('L9ECAV7KIM', 'Loafers', 'A neat addition to your summer wardrobe.', '/static/img/products/loafers.jpg', 'USD', 89, 990000000, '["footwear"]'),
('LS4PSXUNUM', 'Salt & Pepper Shakers', 'Add some flavor to your kitchen.', '/static/img/products/salt-and-pepper-shakers.jpg', 'USD', 18, 490000000, '["kitchen"]'),
('OLJCESPC7Z', 'Sunglasses', 'Add a modern touch to your outfits with these sleek aviator sunglasses.', '/static/img/products/sunglasses.jpg', 'USD', 19, 990000000, '["accessories"]');
