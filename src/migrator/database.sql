CREATE TABLE user(
	_account_id INT UNSIGNED NOT NULL,
	username VARCHAR(20),
	CONSTRAINT PRIMARY KEY (_account_id)
);

CREATE TABLE review(
	_number INT UNSIGNED NOT NULL,
	branch VARCHAR(255),
	change_id CHAR(41),
	created DATETIME,
	current_revision CHAR(40),
	deletions INT UNSIGNED,
	insertions INT UNSIGNED,
	meta_rev_id CHAR(40),
	project VARCHAR(255),
	status VARCHAR(15),
	subject VARCHAR(1024),
	submission_id VARCHAR(30),
	submitted DATETIME,
	total_comment_count INT UNSIGNED,
	unresolved_comment_count INT UNSIGNED,
	updated DATETIME,
	owner_id INT UNSIGNED,
	submitter_id INT UNSIGNED,
	CONSTRAINT review_pk PRIMARY KEY (_number),
	CONSTRAINT review_owner_id
		FOREIGN KEY (owner_id) REFERENCES user (_account_id),
	CONSTRAINT review_submitter_id
		FOREIGN KEY (submitter_id) REFERENCES user (_account_id),
	INDEX review_branch (branch),
	INDEX review_change_id (change_id),
	INDEX review_created (created),
	INDEX review_current_revision (current_revision),
	INDEX review_meta_rev_id (meta_rev_id),
	INDEX review_project (project),
	INDEX review_status (status),
	INDEX review_subject (subject),
	INDEX review_submission_id (submission_id),
	INDEX review_submitted (submitted),
	INDEX review_updated (updated)
);

CREATE TABLE label (
	id INT AUTO_INCREMENT,
	review_id INT UNSIGNED,
	user_id INT UNSIGNED,
	label_type VARCHAR(20),
	value INT,
	date DATETIME,
	CONSTRAINT label_pk PRIMARY KEY (id),
	CONSTRAINT label_review_id
		FOREIGN KEY (review_id) REFERENCES review (_number),
	CONSTRAINT label_user_id
		FOREIGN KEY (user_id) REFERENCES user (_account_id),
	INDEX label_label_type (label_type),
	INDEX label_value (value),
	INDEX label_date (date)
);

CREATE TABLE revision (
	id CHAR(40),
	review_id INT UNSIGNED,
	kind VARCHAR(20),
	_number INT UNSIGNED,
	created DATETIME,
	uploader_id INT UNSIGNED,
	ref VARCHAR(40),
	CONSTRAINT revision_pk PRIMARY KEY (id),
	CONSTRAINT revision_review_id
		FOREIGN KEY (review_id) REFERENCES review (_number),
	CONSTRAINT revision_uploader_id
		FOREIGN KEY (uploader_id) REFERENCES user (_account_id),
	INDEX revision_kind (kind),
	INDEX revision_created (created),
	INDEX revision_ref (ref)
);

CREATE TABLE messages (
	id CHAR(40),
	review_id INT UNSIGNED,
	tag VARCHAR(100),
	author_id INT UNSIGNED,
	real_author_id INT UNSIGNED,
	date DATETIME,
	message MEDIUMTEXT,
	_revision_number INT UNSIGNED,
	CONSTRAINT messages_pk PRIMARY KEY (id),
	CONSTRAINT messages_review_id
		FOREIGN KEY (review_id) REFERENCES review (_number),
	CONSTRAINT messages_author_id
		FOREIGN KEY (author_id) REFERENCES user (_account_id),
	CONSTRAINT messages_real_author_id
		FOREIGN KEY (real_author_id) REFERENCES user (_account_id),
	INDEX messages_tag (tag),
	INDEX messages_date (date)
);

CREATE TABLE inline_comments (
	id CHAR(17),
	review_id INT UNSIGNED,
	_revision_number INT UNSIGNED,
	author_id INT UNSIGNED,
	file_name VARCHAR(500),
	unresolved BOOLEAN,
	line INT,
	start_line INT,
	start_character INT,
	end_line INT,
	end_character INT,
	in_reply_to CHAR(17),
	updated DATETIME,
	message MEDIUMTEXT,
	commit_id CHAR(40),
	CONSTRAINT inline_comments_pk PRIMARY KEY (id),
	CONSTRAINT inline_comments_review_id
		FOREIGN KEY (review_id) REFERENCES review (_number),
	CONSTRAINT inline_comments_author_id
		FOREIGN KEY (author_id) REFERENCES user (_account_id),
	CONSTRAINT inline_comments_in_reply_to
		FOREIGN KEY (in_reply_to) REFERENCES inline_comments (id),
	INDEX inline_comments (file_name),
	INDEX inline_comments_unresolved (unresolved),
	INDEX inline_comments_updated (updated),
	INDEX inline_comments_message (message),
	INDEX inline_comments_commit_id (commit_id)
);
