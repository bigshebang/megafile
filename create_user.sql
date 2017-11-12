CREATE USER 'mf-dba-dev'@'localhost' IDENTIFIED BY 'mf-dba-devpass1029384756%^';
CREATE USER 'mf-dba-del-dev'@'localhost' IDENTIFIED BY 'mf-dba-del-devpass1029384756$%';
CREATE USER 'mf-dba-upload-dev'@'localhost' IDENTIFIED BY 'mf-dba-upload-devpass1029384756#$';
GRANT SELECT,INSERT on MegaFileDev.* to 'mf-dba-dev'@'localhost';
GRANT SELECT,DELETE on MegaFileDev.shares to 'mf-dba-del-dev'@'localhost';
GRANT SELECT,DELETE on MegaFileDev.files to 'mf-dba-del-dev'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFileDev.files to 'mf-dba-upload-dev'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFileDev.users to 'mf-dba-upload-dev'@'localhost';
FLUSH PRIVILEGES;
