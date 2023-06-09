CREATE TABLE IF NOT EXISTS sellers (
    id VARCHAR(40) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,

    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL

);



CREATE TABLE products (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,

    price NUMERIC(10, 2) NOT NULL,

    seller_id VARCHAR(40) NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers (id)
);

CREATE TABLE delivery_method (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- TODO: GOTTA FINISH THESES DELIVERY METHODS AND THEN DO THE MODIFIERS AGAIN!!
CREATE TABLE IF NOT EXISTS product_delivery_method (
    product_id UUID REFERENCES products(id),
    delivery_method_id INT REFERENCES delivery_method(id),
    delivery_range INT,
    PRIMARY KEY (product_id, delivery_method_id)
    -- FOREIGN KEY (product_id) REFERENCES products (id),
    -- FOREIGN KEY (delivery_method_id) REFERENCES delivery_methods (id)
);

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


INSERT INTO delivery_method (id, name) VALUES (1, 'Local Pickup');
INSERT INTO delivery_method (id, name) VALUES (2, 'Shipping');
INSERT INTO delivery_method (id, name) VALUES (3, 'Local Delivery');
