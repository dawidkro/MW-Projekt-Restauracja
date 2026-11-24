CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(32) NOT NULL DEFAULT 'nowe'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    qty INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    UNIQUE KEY menu_category_name (category, name)
) ENGINE=InnoDB;

INSERT INTO orders (status) VALUES ('nowe');
SET @initial_order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, name, qty) VALUES
    (@initial_order_id, 'Pizza', 2),
    (@initial_order_id, 'Cola', 1);

INSERT IGNORE INTO menu (category, name) VALUES
    ('Przystawki', 'Talerz wędlin'),
    ('Przystawki', 'Talerz serów'),
    ('Przystawki', 'Zupka'),
    ('Napoje', 'Cola'),
    ('Napoje', 'Woda'),
    ('Napoje', 'Sok pomarańczowy'),
    ('Napoje', 'Kawa'),
    ('Dania główne', 'Frytki'),
    ('Dania główne', 'Nuggetsy'),
    ('Dania główne', 'Pizza'),
    ('Dania główne', 'Burger'),
    ('Dania główne', 'Sushi'),
    ('Deser', 'Sernik'),
    ('Deser', 'Murzynek');