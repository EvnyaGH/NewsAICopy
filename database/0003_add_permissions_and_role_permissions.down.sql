-- Running downgrade 0003_add_perms -> 0002_add_roles_and_user_roles

DROP TABLE role_permissions;

DROP INDEX ix_permissions_name;

DROP TABLE permissions;