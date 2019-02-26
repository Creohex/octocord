# Create database:
CREATE DATABASE IF NOT EXISTS octocord;


# Switch to octocord db:
USE octocord;


# Delete tables:
DROP table IF EXISTS bot;
DROP table IF EXISTS hook;
DROP table IF EXISTS user;


# Create tables:
CREATE TABLE user(
  id VARCHAR(32) NOT NULL,
  name VARCHAR(40) NOT NULL DEFAULT '',
  secret VARCHAR(32) NOT NULL,
  
  PRIMARY KEY (id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;

#CREATE TABLE bot(
#  id INT NOT NULL AUTO_INCREMENT,
#  # ...
#
#  PRIMARY KEY (id)
#) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;

CREATE TABLE hook(
  id VARCHAR(32) NOT NULL,

  name VARCHAR(126) NOT NULL DEFAULT '',
  channel_id VARCHAR(255) NOT NULL DEFAULT '',
  token VARCHAR(255) NOT NULL DEFAULT '',
  avatar VARCHAR(255) NOT NULL DEFAULT '',
  guild_id VARCHAR(255) NOT NULL DEFAULT '',
  hook_id VARCHAR(255) NOT NULL DEFAULT '',

  owner_id VARCHAR(32) NOT NULL,

  PRIMARY KEY (id, owner_id),
  FOREIGN KEY (owner_id) REFERENCES user(id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;


# Initialize default data
INSERT INTO user (id, name, secret) VALUES
('8fc3cc1961964d12b67494dac10a7d93', 'creohex', '4cadd7d38eda4dda8415720b871f0a2d')
