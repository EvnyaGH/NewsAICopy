-- Running upgrade  -> 0001_create_users_table

CREATE TABLE users (
    id UUID NOT NULL, 
    email VARCHAR(254) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    display_name VARCHAR(100), 
    first_name VARCHAR(100), 
    last_name VARCHAR(100), 
    profile_image_url VARCHAR(2048), 
    email_verified_at TIMESTAMP, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);