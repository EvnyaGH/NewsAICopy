-- Running upgrade 0001_create_users_table -> 0002_add_roles_and_user_roles

CREATE TABLE roles (
    id UUID NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    description VARCHAR(255), 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_roles_name ON roles (name);

CREATE TABLE user_roles (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    role_id UUID NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
    FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE CASCADE, 
    CONSTRAINT uq_user_role UNIQUE (user_id, role_id)
);

CREATE INDEX ix_user_roles_user_id ON user_roles (user_id);

CREATE INDEX ix_user_roles_role_id ON user_roles (role_id);