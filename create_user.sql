CREATE USER 'mf-dba'@'localhost' IDENTIFIED BY 'mf-dba-devpass1029384756%^';
CREATE USER 'mf-dba-del'@'localhost' IDENTIFIED BY 'mf-dba-del-devpass1029384756$%';
CREATE USER 'mf-dba-upload'@'localhost' IDENTIFIED BY 'mf-dba-upload-devpass1029384756#$';
CREATE USER 'mf-redis'@'localhost' IDENTIFIED BY 'mf-redis-devpass1029384756@#!';
GRANT SELECT,INSERT on MegaFile.* to 'mf-dba'@'localhost';
GRANT SELECT,DELETE on MegaFile.shares to 'mf-dba-del'@'localhost';
GRANT SELECT,DELETE on MegaFile.files to 'mf-dba-del'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.files to 'mf-dba-upload'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.users to 'mf-dba-upload'@'localhost';
GRANT SELECT on MegaFile.* to 'mf-redis'@'localhost'; #needed for reflection with sqlalchemy
GRANT SELECT,INSERT on MegaFile.shares to 'mf-redis'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.redis_logs to 'mf-redis'@'localhost';
FLUSH PRIVILEGES;
