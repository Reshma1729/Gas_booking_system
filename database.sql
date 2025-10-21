-- Create the database
CREATE DATABASE IF NOT EXISTS gas_booking_system;

-- Use the database
USE gas_booking_system;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(10) UNIQUE NOT NULL,
    aadhaar VARCHAR(12),
    address TEXT,
    password VARCHAR(255) NOT NULL
);

-- Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company VARCHAR(50) NOT NULL,
    delivery_address TEXT NOT NULL,
    pincode VARCHAR(6) NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    payment_type VARCHAR(20) NOT NULL,
    card_number VARCHAR(16),
    expiry_date VARCHAR(7),
    cvv VARCHAR(3),
    upi_id VARCHAR(50),
    status VARCHAR(50),
    amount DECIMAL(10,2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
