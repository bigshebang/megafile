CREATE USER 'mf-dba'@'localhost' IDENTIFIED BY 'I heard that passphrases are better than passwords 51257!$%^';
CREATE USER 'mf-dba-del'@'localhost' IDENTIFIED BY 'when will we get rid of passwords doe? 9092211';
CREATE USER 'mf-dba-upload'@'localhost' IDENTIFIED BY 'i like to upload file$ 12580335#!!';
GRANT SELECT,INSERT on MegaFile.* to 'mf-dba'@'localhost';
GRANT SELECT,DELETE on MegaFile.shares to 'mf-dba-del'@'localhost';
GRANT SELECT,DELETE on MegaFile.files to 'mf-dba-del'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.files to 'mf-dba-upload'@'localhost';
GRANT SELECT,INSERT,UPDATE on MegaFile.users to 'mf-dba-upload'@'localhost';
FLUSH PRIVILEGES;

