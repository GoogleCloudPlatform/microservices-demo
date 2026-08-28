CREATE TABLE IF NOT EXISTS wishlists (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    added_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_user_product UNIQUE (user_id, product_id)
);
CREATE INDEX idx_wishlists_user_id ON wishlists(user_id);
