-- Running upgrade 0002_add_roles_and_user_roles -> 0003_add_perms

CREATE TABLE permissions (
    id UUID NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    resource VARCHAR(100), 
    action VARCHAR(50), 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_permissions_name ON permissions (name);

CREATE TABLE role_permissions (
    role_id UUID NOT NULL, 
    permission_id UUID NOT NULL, 
    PRIMARY KEY (role_id, permission_id), 
    FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE CASCADE, 
    FOREIGN KEY(permission_id) REFERENCES permissions (id) ON DELETE CASCADE
);