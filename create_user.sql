CREATE USER 'mf-dba'@'localhost' IDENTIFIED BY 'I heard that passphrases are better than passwords 51257!$%^';
CREATE USER 'mf-dba-del'@'localhost' IDENTIFIED BY 'when will we get rid of passwords doe? 9092211';
CREATE USER 'mf-dba-upload'@'localhost' IDENTIFIED BY 'i like to upload file$, is that okay? 12580335#!!';
CREATE USER 'mf-redis'@'localhost' IDENTIFIED BY 'why do i have so many of these db account passwords? $9990$';
GRANT SELECT,INSERT on MegaFile.* to 'mf-dba'@'localhost';
GRANT SELECT,DELETE on MegaFile.shares to 'mf-dba-del'@'localhost';
GRANT SELECT,DELETE on MegaFile.files to 'mf-dba-del'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.files to 'mf-dba-upload'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.users to 'mf-dba-upload'@'localhost';
GRANT SELECT on MegaFile.* to 'mf-redis'@'localhost'; #needed for reflection with sqlalchemy
GRANT SELECT,INSERT on MegaFile.shares to 'mf-redis'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.redis_logs to 'mf-redis'@'localhost';
FLUSH PRIVILEGES;
