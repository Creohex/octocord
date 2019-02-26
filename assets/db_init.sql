# Create database:
CREATE DATABASE IF NOT EXISTS octocord;

# Switch to octocord db:
USE octocord;

# Delete tables:
DROP table IF EXISTS user;
DROP table IF EXISTS bot;
DROP table IF EXISTS hook;

# Create tables:
CREATE TABLE user(
  id BINARY(16) NOT NULL,
  name VARCHAR(40) NOT NULL DEFAULT '',
  secret BINARY(16) NOT NULL,
  
  PRIMARY KEY (id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;

CREATE TABLE bot(
  id INT NOT NULL AUTO_INCREMENT,
  # ...

  PRIMARY KEY (id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;

CREATE TABLE hook(
  id INT NOT NULL AUTO_INCREMENT,
  
  name VARCHAR(126) NOT NULL DEFAULT '',
  channel_id VARCHAR(255) NOT NULL,
  token VARCHAR(255) NOT NULL,
  avatar VARCHAR(255) NOT NULL,
  guild_id VARCHAR(255) NOT NULL,
  hook_id VARCHAR(255) NOT NULL,

  link VARCHAR(255) NOT NULL DEFAULT '',

  PRIMARY KEY (id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;


# Initialize default data
# ...
