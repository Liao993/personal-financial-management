-- Rename the former travel sub-category without losing existing records.
UPDATE expense
SET traveling_category = 'Rental/Gas/Parking/Tolls'
WHERE traveling_category = 'Gas/Parking/Tolls';
