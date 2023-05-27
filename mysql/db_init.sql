CREATE DATABASE IF NOT EXISTS stori;
USE stori;
DROP TABLE IF EXISTS Transaction;
CREATE TABLE Transaction (t_id int PRIMARY KEY, t_value FLOAT, t_date DATE);