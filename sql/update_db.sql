CREATE TABLE IF NOT EXISTS users (
	id char(10) PRIMARY KEY,
	username varchar(128) NOT NULL UNIQUE,
	password char(255) NOT NULL,
	INDEX (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE hash_2_params (
	id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
	hash char(64) NOT NULL UNIQUE,
	time_created DATETIME NOT NULL,
	time_to_live int,
	expire_after_first_access BOOLEAN NOT NULL DEFAULT FALSE,
	last_access DATETIME,
	data TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE hash_2_params_historylog (
	id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
	id_hash_2_params bigint NOT NULL,
	ip varchar(16) NOT NULL,
	log_time DATETIME NOT NULL,
	CONSTRAINT hash_2_params_historylog_fk0 FOREIGN KEY (id_hash_2_params) REFERENCES hash_2_params(id)
) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS sequencers (
	id char(2) NOT NULL,
	s_partition char(2) NOT NULL,
	size smallint NOT NULL,
	active_stage char(3) NOT NULL,
	check_sum_size smallint NOT NULL,
	name varchar(16) NOT NULL UNIQUE,
	type varchar(16) NOT NULL,
	s_table varchar(32) NOT NULL UNIQUE,
	ordered BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- SESSION TOKENS --

DROP TABLE IF EXISTS session_token;
CREATE TABLE session_token (
  id char(64) PRIMARY KEY,
  id_user char(10) NOT NULL,
  created DATETIME NOT NULL,
  closed boolean DEFAULT FALSE,
	INDEX (id_user),
	INDEX (closed),
	CONSTRAINT session_token_fk0 FOREIGN KEY (id_user) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE mail_queue (
	id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
	sender varchar(128) NOT NULL,
	receiver TEXT NOT NULL,
	time_created DATETIME NOT NULL,
	time_sent DATETIME,
	sent BOOLEAN NOT NULL DEFAULT FALSE,
	message TEXT NOT NULL,
	INDEX email_sender_idx (sender),
	INDEX email_sent (sent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into sequencers (id, s_partition, active_stage, size, check_sum_size, name ,type, s_table, ordered)
values
('u','00','000',4,0,'users','STR','s_users',false),
('s','00','000',58,0,'session_token','STR','s_session_token',false),
('h','00','000',58,0,'hash_2_params','STR','s_hash_2_params ',false)
-- ('c','00','000',3,0,'clubs','STR','s_clubs',false),
-- ('e','00','000',3,0,'events','STR','s_events',false),
-- ('u','00','000',3,0,'um_transactions','STR','s_um_transactions',false)
;

drop table if exists s_users;
CREATE TABLE s_users (
    id char(10) PRIMARY KEY,
    active_stage char(3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists s_session_token;
CREATE TABLE s_session_token (
    id char(64) PRIMARY KEY,
    active_stage char(3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists s_hash_2_params ;
CREATE TABLE s_hash_2_params (
	id char(64) PRIMARY KEY,
	active_stage char(3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
