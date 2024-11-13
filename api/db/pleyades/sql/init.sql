-- **********************************
-- ************ Tables **************
-- **********************************
-- table users
CREATE TABLE users (
	email VARCHAR (200) NOT NULL ,
	name VARCHAR (200) NOT NULL ,
	password VARCHAR (50) NOT NULL ,
	role VARCHAR (50) NOT NULL ,
	CONSTRAINT pk_User 
	PRIMARY KEY( email )
);

-- table datasets
CREATE TABLE datasets (
	program INT (30) NOT NULL ,
	manager VARCHAR (200) NOT NULL ,
	name VARCHAR (200) NOT NULL ,
	type VARCHAR (50) NOT NULL ,
	number INT (30) NOT NULL ,
	initialPeriod INT (6) NOT NULL ,
	finalPeriod INT (6) NOT NULL ,
	status VARCHAR (50) NOT NULL ,
	CONSTRAINT pk_Dataset 
	PRIMARY KEY( name )
);

-- table preparations
CREATE TABLE preparations (
	preparer VARCHAR (200) NOT NULL ,
	dataset VARCHAR (200) NOT NULL ,
	name VARCHAR (250) NOT NULL ,
	number INT (30) NOT NULL ,
	startDate DATETIME NOT NULL ,
	endDate DATETIME ,
	status VARCHAR (50) NOT NULL ,
	observations JSON NULL,
	CONSTRAINT pk_Preparation 
	PRIMARY KEY( name )
);

-- table executions
CREATE TABLE executions (
	executor VARCHAR (200) NOT NULL ,	
	dataset VARCHAR (200) NOT NULL ,
	name VARCHAR (250) NOT NULL ,
	number INT (30) NOT NULL ,
	startDate DATETIME NOT NULL ,
	endDate DATETIME NOT NULL ,
	status VARCHAR (50) NOT NULL ,
	modelPrecision FLOAT ,
	results JSON NOT NULL,
	CONSTRAINT pk_Execution 
	PRIMARY KEY( name )
);



-- ****************************************
-- ************ Foreign Keys **************
-- ****************************************

-- For datasets(fk_Dataset_User) 
ALTER TABLE datasets ADD(
	CONSTRAINT fk_Dataset_User
	FOREIGN KEY ( manager )
	REFERENCES users ( email )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For executions(fk_Execution_Dataset) 
ALTER TABLE executions ADD(
	CONSTRAINT fk_Execution_Dataset
	FOREIGN KEY ( dataset )
	REFERENCES datasets ( name )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For executions(fk_Execution_User) 
ALTER TABLE executions ADD(
	CONSTRAINT fk_Execution_User
	FOREIGN KEY ( executor )
	REFERENCES users ( email )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For preparations(fk_Preparation_Dataset) 
ALTER TABLE preparations ADD(
	CONSTRAINT fk_Preparation_Dataset
	FOREIGN KEY ( dataset )
	REFERENCES datasets ( name )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For preparations(fk_Preparation_User) 
ALTER TABLE preparations ADD(
	CONSTRAINT fk_Preparation_User
	FOREIGN KEY ( preparer )
	REFERENCES users ( email )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);


-- **********************************
-- ************ Initial Inserts **************
-- **********************************
    
INSERT INTO `users` (`name`,`email`,`password`,`role`) VALUES
('SUPER ADMIN','admin@pleyades.com','25d55ad283aa400af464c76d713c07ad','Admin');