-- **********************************
-- ************ Tables **************
-- **********************************
use pleyades;
-- table usuarios
CREATE TABLE  usuarios (
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

-- table preparaciones
CREATE TABLE  preparaciones (
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

-- table ejecuciones
CREATE TABLE  ejecuciones (
	ejecutor VARCHAR (200) NOT NULL 	,	
	conjunto VARCHAR (200) NOT NULL 	,
	nombre VARCHAR (250) NOT NULL 	,
	numero INT (30) NOT NULL 	,
	fechaInicial DATETIME NOT NULL 	,
	fechaFinal DATETIME NOT NULL 	,
	estado VARCHAR (50) NOT NULL 	,
	precision_modelo FLOAT		,
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
	REFERENCES  usuarios ( correo )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For ejecuciones(fk_Preparacion_ConjuntoDeDatos) 
ALTER TABLE ejecuciones ADD(
	CONSTRAINT fk_Ejecucion_ConjuntoDeDatos
	FOREIGN KEY ( conjunto )
	REFERENCES  conjuntosdedatos ( nombre )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For ejecuciones(fk_Ejecucion_Usuario) 
ALTER TABLE ejecuciones ADD(
	CONSTRAINT fk_Ejecucion_Usuario
	FOREIGN KEY ( ejecutor )
	REFERENCES  usuarios ( correo )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For preparaciones(fk_Preparacion_ConjuntoDeDatos) 
ALTER TABLE preparaciones ADD(
	CONSTRAINT fk_Preparacion_ConjuntoDeDatos
	FOREIGN KEY ( conjunto )
	REFERENCES  conjuntosdedatos ( nombre )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- For preparaciones(fk_Preparacion_Usuario) 
ALTER TABLE preparaciones ADD(
	CONSTRAINT fk_Preparacion_Usuario
	FOREIGN KEY ( preparador )
	REFERENCES  usuarios ( correo )
	ON DELETE CASCADE
    ON UPDATE CASCADE
);