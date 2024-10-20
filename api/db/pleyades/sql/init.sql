-- **********************************
-- ************ Tables **************
-- **********************************
-- table users
CREATE TABLE  users (
	correo VARCHAR (200) NOT NULL 	,
	nombre VARCHAR (200) NOT NULL 	,
	clave VARCHAR (50) NOT NULL 	,
	rol VARCHAR (50) NOT NULL 	,
	CONSTRAINT  pk_Usuario 
	PRIMARY KEY( correo )
);

-- table conjuntosdedatos
CREATE TABLE  conjuntosdedatos (
	programa INT (30) NOT NULL 	,
	encargado VARCHAR (200) NOT NULL 	,
	nombre VARCHAR (200) NOT NULL 	,
	tipo VARCHAR (50) NOT NULL 	,
	numero INT (30) NOT NULL 	,
	periodoInicial INT (6) NOT NULL 	,
	periodoFinal INT (6) NOT NULL 	,
	estado VARCHAR (50) NOT NULL 	,
	CONSTRAINT  pk_ConjuntoDeDatos 
	PRIMARY KEY( nombre )
);

-- table preparations
CREATE TABLE  preparations (
	preparador VARCHAR (200) NOT NULL 	,
	conjunto VARCHAR (200) NOT NULL 	,
	nombre VARCHAR (250) NOT NULL 	,
	numero INT (30) NOT NULL 	,
	fechaInicial DATETIME  NOT NULL 	,
	fechaFinal DATETIME 	,
	estado VARCHAR (50) NOT NULL 	,
	observaciones JSON NULL,
	CONSTRAINT  pk_Preparacion 
	PRIMARY KEY( nombre )
);

-- table executions
CREATE TABLE  executions (
	ejecutor VARCHAR (200) NOT NULL 	,	
	conjunto VARCHAR (200) NOT NULL 	,
	nombre VARCHAR (250) NOT NULL 	,
	numero INT (30) NOT NULL 	,
	fechaInicial DATETIME NOT NULL 	,
	fechaFinal DATETIME NOT NULL 	,
	estado VARCHAR (50) NOT NULL 	,
	precision_model FLOAT		,
	resultados JSON NOT NULL,
	CONSTRAINT  pk_Ejecucion 
	PRIMARY KEY( nombre )
);



-- ****************************************
-- ************ Foreign Keys **************
-- ****************************************

-- For conjuntosdedatos(fk_ConjuntoDeDatos_Usuario) 
ALTER TABLE conjuntosdedatos ADD(
	CONSTRAINT fk_ConjuntoDeDatos_Usuario
	FOREIGN KEY ( encargado )
	REFERENCES  users ( correo )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For executions(fk_Preparacion_ConjuntoDeDatos) 
ALTER TABLE executions ADD(
	CONSTRAINT fk_Ejecucion_ConjuntoDeDatos
	FOREIGN KEY ( student_set )
	REFERENCES  conjuntosdedatos ( nombre )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For executions(fk_Ejecucion_Usuario) 
ALTER TABLE executions ADD(
	CONSTRAINT fk_Ejecucion_Usuario
	FOREIGN KEY ( ejecutor )
	REFERENCES  users ( correo )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For preparations(fk_Preparacion_ConjuntoDeDatos) 
ALTER TABLE preparations ADD(
	CONSTRAINT fk_Preparacion_ConjuntoDeDatos
	FOREIGN KEY ( student_set )
	REFERENCES  conjuntosdedatos ( nombre )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For preparations(fk_Preparacion_Usuario) 
ALTER TABLE preparations ADD(
	CONSTRAINT fk_Preparacion_Usuario
	FOREIGN KEY ( preparador )
	REFERENCES  users ( correo )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);


-- **********************************
-- ************ Initial Inserts **************
-- **********************************
    
INSERT INTO `users`(`nombre`,`correo`,`clave`,`rol`) VALUES
('SUPER ADMIN','admin@pleyades.com','25d55ad283aa400af464c76d713c07ad','Admin');