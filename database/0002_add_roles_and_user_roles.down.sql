-- Running downgrade 0002_add_roles_and_user_roles -> 0001_create_users_table

DROP INDEX ix_user_roles_role_id;

DROP INDEX ix_user_roles_user_id;

DROP TABLE user_roles;

DROP INDEX ix_roles_name;

DROP TABLE roles;