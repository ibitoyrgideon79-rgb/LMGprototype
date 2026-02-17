-- Sample data for Luminous Glow Cosmetics

INSERT INTO products (name, description, price, category, image_url, stock) VALUES
('Rose Glow Perfume', 'A romantic floral fragrance with a luminous finish.', 49999.00, 'Perfumes', '/static/images/rose-glow.svg', 25),
('Luminous Lip Gloss', 'High-shine gloss with a glassy, hydrating feel.', 19999.00, 'Lip Gloss', '/static/images/lip-gloss.svg', 60),
('Pink Lip Balm', 'Soft, cushiony balm for all-day comfort.', 14999.00, 'Lip Care', '/static/images/lip-balm.svg', 80),
('Radiance Face Cream', 'Silky cream that leaves skin dewy and radiant.', 39999.00, 'Creams', '/static/images/face-cream.svg', 40),
('Silk Hair Serum', 'Gloss-boosting serum with a smooth finish.', 29999.00, 'Hair Products', '/static/images/hair-serum.svg', 35),
('Glow Setting Spray', 'Mist that locks makeup with a soft glow.', 24999.00, 'Makeup', '/static/images/setting-spray.svg', 50);

INSERT INTO reviews (user_name, rating, comment, created_at) VALUES
('Sarah M.', 5, 'Absolutely love the lip gloss! So glossy and long-lasting', NOW()),
('Jessica R.', 4, 'The perfume smells amazing, subtle and elegant', NOW()),
('Emily K.', 5, 'Best skincare products I''ve ever used. My skin feels amazing', NOW()),
('Michael T.', 4, 'Great customer service and quick delivery', NOW()),
('Amanda P.', 5, 'The cream transformed my skin, highly recommend', NOW());
