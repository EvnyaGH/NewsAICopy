-- Running downgrade 0001_create_users_table -> 

DROP INDEX ix_users_email;

DROP TABLE users;