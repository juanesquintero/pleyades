-- CREATE Tables
USE [$(MSSQL_DBNAME)]
GO

IF OBJECT_ID('VWFACULTADDESERCION', 'U') IS NULL
BEGIN
CREATE TABLE VWFACULTADDESERCION(
  codigo NUMERIC(10,0) NOT NULL,
  nombre VARCHAR(200) NOT NULL);
END

IF OBJECT_ID('VWPROGRAMADESERCION', 'U') IS NULL
BEGIN
CREATE TABLE VWPROGRAMADESERCION (
  codigo NUMERIC(10,0) NOT NULL,
  nombre VARCHAR(200) NOT NULL,
  nombre_corto VARCHAR(10) NOT NULL,
  facultad INT NOT NULL,
  nombre_facultad VARCHAR(200));
END

-- Table Desercion Crudos

IF OBJECT_ID('VWDATADESERCION', 'U') IS NULL
BEGIN
CREATE TABLE VWDATADESERCION(
  	REGISTRO INT NOT NULL,
  	semestre INT NOT NULL,
  	jornada VARCHAR(100) NULL,
  	nombre_completo VARCHAR(300) NOT NULL,
  	tipo_documento VARCHAR(100) NOT NULL,
  	documento VARCHAR(50) NOT NULL,
	edad INT NULL,
	genero VARCHAR(100) NULL,
	estado_civil VARCHAR(100) NULL,
	lugar_residencia_sede VARCHAR(100) NULL,
	trabaja VARCHAR(2) NULL,
	etnia VARCHAR(300) NULL,
	victima VARCHAR(2) NULL,
	pertenece_grupo_vulnerable VARCHAR(2) NULL,
	creditos_programa INT NULL,
	creditos_aprobados_sem INT NULL,
	creditos_aprobados_acum INT NULL,
	asignaturas_aprobadas_sem INT NULL,
	asignaturas_aprobadas_acum INT NULL,
	creditos_reprobados_sem INT NULL,
	creditos_reprobados_acum INT NULL,
	asignaturas_reprobadas_sem INT NULL,
	asignaturas_reprobadas_acum INT NULL,
	creditos_cancelados_sem INT NULL,
	creditos_cancelados_acum INT NULL,
	creditos_matriculados_sem INT NULL,
	creditos_matriculados_acum INT NULL,
	promedio_semestre DECIMAL NULL,
	promedio_acumulado DECIMAL NULL,
	puntaje_icfes DECIMAL NULL,
	beca VARCHAR(2) NULL,
	intersemestral VARCHAR(2) NULL,
	desertor VARCHAR(2) NULL,
	periodo_ingreso INT NULL,
	ultimo_periodo INT NULL,
	biologia DECIMAL NULL,
	ciencias_naturales DECIMAL NULL,
	ciencias_sociales DECIMAL NULL,
	competencias_ciudadanas DECIMAL NULL,
	filosofia DECIMAL NULL,
	fisica DECIMAL NULL,
	geografia DECIMAL NULL,
	historia DECIMAL NULL,
	ingles DECIMAL NULL,
	lectura_critica DECIMAL NULL,
	lenguaje DECIMAL NULL,
	matematicas DECIMAL NULL,
	quimica DECIMAL NULL,
	razonamiento_cuantitativo DECIMAL NULL,
	sociales_y_ciudadanas DECIMAL NULL,
	idmatricula VARCHAR(50) NULL,
	idaspiracion VARCHAR(50) NULL,
	idprograma VARCHAR(30) NULL,
	programa VARCHAR(100) NULL,
	tipo_programa VARCHAR(50) NULL,
	idfacultad VARCHAR(30) NULL,
	facultad VARCHAR(100) NULL,
	estrato_residencia VARCHAR(50) NULL,
	celular_telefono VARCHAR(100) NULL,
	fecha_nacimiento VARCHAR(100) NULL,
	sanciones_multas VARCHAR(50) NULL,
	participacion_semillero_investigacion VARCHAR(50) NULL,
	correo_electronico VARCHAR(100) NULL,
	asignaturas_programa INT NULL,
	asignaturas_canceladas_sem INT NULL,
	asignaturas_canceladas_acum INT NULL,
	DTFECHAREGISTRO DATE NULL,
	idestado INT NULL,);
END

IF OBJECT_ID('TBLDES_RESULTADO_PREDICCION', 'U') IS NULL
BEGIN
CREATE TABLE TBLDES_RESULTADO_PREDICCION (
  documento VARCHAR(50) NOT NULL, 
  nombre_completo VARCHAR(300) NOT NULL, 
  desertor INT NOT NULL, 
  prediccion INT NOT NULL, 
  semestre_prediccion INT NOT NULL,
  idprograma VARCHAR(30) NOT NULL,
  blnultimo INT NULL);
END

GO
