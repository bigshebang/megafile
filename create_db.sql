DROP DATABASE IF EXISTS MegaFile;
CREATE DATABASE MegaFile;
USE MegaFile;
CREATE TABLE users (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username varchar(64) NOT NULL,
	first varchar(64) NOT NULL,
	last varchar(64) NOT NULL,
	bio varchar(8192) NOT NULL DEFAULT 'Bio',
    password varchar(128) NOT NULL, #TODO: why is this a varchar?
    admin INT NOT NULL DEFAULT 0
);

CREATE TABLE files (
	id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	name varchar(256) NOT NULL,
	type varchar(128) NOT NULL,
	size INT NOT NULL,
	content MEDIUMBLOB NOT NULL,
	userid INT NOT NULL,

	FOREIGN KEY (userid) REFERENCES users(id)
);

CREATE TABLE shares (
	ownerid INT NOT NULL,
	shareid INT NOT NULL,
	PRIMARY KEY (ownerid, shareid),
	FOREIGN KEY (ownerid) REFERENCES users(id),
	FOREIGN KEY (shareid) REFERENCES users(id)
);

CREATE TABLE privkeys (
	id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	privkey varchar(2048) NOT NULL,
	userid INT NOT NULL,
	FOREIGN KEY (userid) REFERENCES users(id)
);

CREATE TABLE xml_uploads (
	id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	uploader_id INT NOT NULL,
	contents varchar(8192) NOT NULL,
	ip varchar(16) NOT NULL,
	upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (uploader_id) REFERENCES users(id)
);

CREATE TABLE redis_logs (
	id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	message varchar(4096) NOT NULL,
	db_result varchar(2048),
	attempt_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

# create admin user with password of 'password', so you should change it
INSERT INTO users (username, password, first, last, bio, admin) VALUES (
	'admin',
	'eae889ceda1452b34555b2b52b9f05d28a1e8ed8d5dc8c62362b90ee49746af1b99bf53cb3e58323d29c1dcc5b1203e45f824d10d87b1a63b9d6eec59a2f6740',
	'first',
	'last',
	'i am the admin',
	1
);
