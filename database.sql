CREATE DATABASE web_project;
USE web_project;

CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    user_name VARCHAR(50),
    email VARCHAR(50) UNIQUE,
    phone_no VARCHAR(14),
    address VARCHAR(60),
    userpass VARCHAR(255) NOT NULL
);

CREATE TABLE vehicle (
    user_id VARCHAR(36) NOT NULL,
    vehicle_name VARCHAR(50),
    vehicle_id VARCHAR(36) PRIMARY KEY NOT NULL UNIQUE,
    make VARCHAR(60),
    model VARCHAR(60),
    make_year INT,
    licence_number VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE registration_documents (
    registration_id VARCHAR(36) PRIMARY KEY NOT NULL,
    vehicle_id VARCHAR(36) NOT NULL,
    document_name VARCHAR(50) NOT NULL,
    document_number VARCHAR(20) UNIQUE,
    expiration_date DATE,
    file_path VARCHAR(255) NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE insurance_documents (
    insurance_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    vehicle_id VARCHAR(36) NOT NULL,
    policy_number VARCHAR(40),
    expire_date DATE,
    upload_date DATE DEFAULT CURRENT_DATE,
    file_path VARCHAR(255) NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE emissiondocuments (
    emission_id VARCHAR(36) PRIMARY KEY NOT NULL,
    vehicle_id VARCHAR(36) NOT NULL,
    certificate_number VARCHAR(30),
    issue_date DATE,
    expiration_date DATE,
    file_path VARCHAR(255) NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE ON UPDATE CASCADE
);
