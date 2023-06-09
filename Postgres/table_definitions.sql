CREATE TABLE IF NOT EXISTS sellers (
    id VARCHAR(40) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    -- description TEXT,
    -- instagram VARCHAR(255),
    -- tiktok VARCHAR(255),
    -- pinterest VARCHAR(255),
    -- facebook VARCHAR(255),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
    -- stripe_account_id VARCHAR(255) NOT NULL,
);

-- CREATE TABLE store_address (
--     id UUID PRIMARY KEY DEFAULT UUID_GENERATE_V4(),
--     seller_id VARCHAR(255) NOT NULL,
--     address_line_1 VARCHAR(255),
--     address_line_2 VARCHAR(50),
--     zip_code VARCHAR(10) NOT NULL,
--     city VARCHAR(100),
--     state VARCHAR(2),
--     FOREIGN KEY (seller_id) REFERENCES sellers (id)
-- )


CREATE TABLE products (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    -- description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    -- stock INTEGER,
    seller_id VARCHAR(40) NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers (id)
);

-- CREATE TABLE seller_images (
--     id SERIAL PRIMARY KEY,
--     seller_id VARCHAR(255) NOT NULL,
--     image_url TEXT,
--     FOREIGN KEY (seller_id) REFERENCES sellers (id)
-- );

-- CREATE TABLE product_images (
--     id SERIAL PRIMARY KEY,
--     product_id UUID NOT NULL,
--     image_url TEXT,
--     FOREIGN KEY (product_id) REFERENCES products (id)
-- );

-- CREATE TABLE modifiers (
--     id UUID PRIMARY KEY DEFAULT UUID_GENERATE_V4(), -- mod1
--     name VARCHAR(255) NOT NULL, -- Choose a color
--     modifier_type VARCHAR(7) NOT NULL, -- choice
--     max_options INT, -- 1
--     modifier_required BOOLEAN DEFAULT TRUE,
--     max_characters INT -- NULL
-- );

-- CREATE TABLE modifier_details (
--     id UUID PRIMARY KEY DEFAULT UUID_GENERATE_V4(), -- opt1, opt2, opt3
--     modifier_id UUID NOT NULL, -- mod1, mod1, mod1
--     name VARCHAR(255) NOT NULL, -- Blue, Green, Yellow
--     price NUMERIC(10, 2), -- NULL, NULL, NULL
--     FOREIGN KEY (modifier_id) REFERENCES modifiers(id) -- mod1, mod1, mod1
-- );

-- CREATE TABLE product_modifiers (
--     product_id UUID NOT NULL, -- prod1
--     modifier_id UUID NOT NULL, -- mod1
--     PRIMARY KEY (product_id, modifier_id), -- (1, 1)
--     FOREIGN KEY (product_id) REFERENCES products(id),
--     FOREIGN KEY (modifier_id) REFERENCES modifiers(id)
-- );

-- CREATE TABLE IF NOT EXISTS local_pickup_methods (
--     id SERIAL PRIMARY KEY,
--     -- other fields specific to local pickup
-- );

-- CREATE TABLE IF NOT EXISTS shipping_methods (
--     id SERIAL PRIMARY KEY,
--     -- other fields specific to shipping
-- );

-- CREATE TABLE IF NOT EXISTS delivery_methods (
--     id SERIAL PRIMARY KEY,
--     -- other fields specific to delivery
-- );

CREATE TABLE delivery_method (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);


-- CREATE TABLE IF NOT EXISTS sellers_delivery_methods (
--     seller_id INT NOT NULL,
--     local_pickup_method_id INT,
--     shipping_method_id INT,
--     delivery_method_id INT,
--     CONSTRAINT fk_seller
--         FOREIGN KEY(seller_id) 
--             REFERENCES sellers(id),
--     CONSTRAINT fk_local_pickup_method
--         FOREIGN KEY(local_pickup_method_id) 
--             REFERENCES local_pickup_methods(id),
--     CONSTRAINT fk_shipping_method
--         FOREIGN KEY(shipping_method_id) 
--             REFERENCES shipping_methods(id),
--     CONSTRAINT fk_delivery_method
--         FOREIGN KEY(delivery_method_id) 
--             REFERENCES delivery_methods(id),
--     CONSTRAINT unique_seller_delivery_methods
--         UNIQUE(seller_id)
-- );

-- TODO: GOTTA FINISH THESES DELIVERY METHODS AND THEN DO THE MODIFIERS AGAIN!!
CREATE TABLE IF NOT EXISTS product_delivery_method (
    product_id UUID REFERENCES products(id),
    delivery_method_id INT REFERENCES delivery_method(id),
    delivery_range INT,
    PRIMARY KEY (product_id, delivery_method_id)
    -- FOREIGN KEY (product_id) REFERENCES products (id),
    -- FOREIGN KEY (delivery_method_id) REFERENCES delivery_methods (id)
);

-- CREATE TABLE IF NOT EXISTS seller_delivery_methods (
--     seller_id VARCHAR(255) NOT NULL,
--     delivery_method_id INTEGER NOT NULL,
--     PRIMARY KEY (seller_id, delivery_method_id),
--     FOREIGN KEY (seller_id) REFERENCES sellers (id),
--     FOREIGN KEY (delivery_method_id) REFERENCES delivery_methods (id)
-- );

-- CREATE TABLE seller_ratings (
--     id SERIAL PRIMARY KEY,
--     seller_id VARCHAR(255) NOT NULL,
--     rating INT CHECK (rating >= 1 AND rating <= 10),
--     review TEXT,
--     FOREIGN KEY (seller_id) REFERENCES sellers (id)
-- );

-- CREATE TABLE product_ratings (
--     id SERIAL PRIMARY KEY,
--     product_id UUID NOT NULL,
--     rating INT CHECK (rating >= 1 AND rating <= 10),
--     review TEXT,
--     FOREIGN KEY (product_id) REFERENCES products (id)
-- );

CREATE OR REPLACE FUNCTION haversine(
    lat1 FLOAT, lon1 FLOAT,
    lat2 FLOAT, lon2 FLOAT
) RETURNS FLOAT AS $$
DECLARE
    x FLOAT := 69.1 * (lat2 - lat1);
    y FLOAT := 69.1 * (lon2 - lon1) * COS(lat1 / 57.3);
BEGIN
    RETURN SQRT(x * x + y * y);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION filter_products(
    client_lat float, client_long float,
    option_ids int[], client_radius float
)
RETURNS TABLE (
    product_id uuid,
    product_name varchar,
    delivery_option varchar,
    delivery_range int
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id, p.name, dm.name, pdm.delivery_range
    FROM 
        products p
        INNER JOIN product_delivery_method pdm ON p.id = pdm.product_id
        INNER JOIN delivery_method dm ON pdm.delivery_option_id = dm.id
    WHERE 
        dm.id = ANY(option_ids) AND 
        (
            NOT array[1] <@ option_ids OR 
            (client_lat IS NOT NULL AND client_long IS NOT NULL AND client_radius IS NOT NULL AND
            calculate_distance(p.latitude, p.longitude, client_lat, client_long) <= client_radius)
        ) AND 
        (
            NOT array[3] <@ option_ids OR 
            (client_lat IS NOT NULL AND client_long IS NOT NULL AND
            calculate_distance(p.latitude, p.longitude, client_lat, client_long) <= pdm.delivery_range)
        );
END
$$ LANGUAGE plpgsql;

-- INSERT INTO delivery_methods (method_name) VALUES
-- ('Local Pickup'),
-- ('Delivery'),
-- ('Shipping');

-- INSERT INTO sellers (id, title, description, instagram, tiktok, pinterest, facebook, latitude, longitude)
-- VALUES
-- ('Seller1', 'Seller 1', 'This is seller 1 🎉', 'https://instagram.com/seller1', 'https://tiktok.com/seller1', 'https://pinterest.com/seller1', 'https://facebook.com/seller1', 40.730610, -73.935242),
-- ('Seller2', 'Seller 2', 'This is seller 2 😊', 'https://instagram.com/seller2', NULL, NULL, NULL, 34.052235, -118.243683),
-- ('Seller3', 'Seller 3', 'This is seller 3 🚀', NULL, 'https://tiktok.com/seller3', NULL, NULL, 37.774930, -122.419418);

-- INSERT INTO seller_delivery_methods (seller_id, delivery_method_id)
-- VALUES
-- ((SELECT id FROM sellers WHERE title = 'Seller 1'), 1),
-- ((SELECT id FROM sellers WHERE title = 'Seller 1'), 2),
-- ((SELECT id FROM sellers WHERE title = 'Seller 2'), 2),
-- ((SELECT id FROM sellers WHERE title = 'Seller 2'), 3),
-- ((SELECT id FROM sellers WHERE title = 'Seller 3'), 1),
-- ((SELECT id FROM sellers WHERE title = 'Seller 3'), 3);



-- WITH inserted AS (
--     INSERT INTO products(title, description, price, stock, seller_id)
--     VALUES ('Product 1', 'Yee doggy', 5.5, 1, 'Seller1')
--     RETURNING id
-- )
-- INSERT INTO product_delivery_methods(product_id, delivery_method_id)
-- SELECT inserted.id, 1 FROM inserted;

-- SELECT products.title, delivery_methods.method_name
-- FROM products
-- INNER JOIN product_delivery_methods ON product_delivery_methods.product_id = products.id
-- INNER JOIN delivery_methods ON delivery_methods.id = product_delivery_methods.delivery_method_id;

INSERT INTO delivery_method (id, name) VALUES (1, 'Local Pickup');
INSERT INTO delivery_method (id, name) VALUES (2, 'Shipping');
INSERT INTO delivery_method (id, name) VALUES (3, 'Local Delivery');
