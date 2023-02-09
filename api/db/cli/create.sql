USE [CLI_desercion]
GO
CREATE TABLE VWFACULTADDESERCION(
  codigo NUMERIC(10,0) NOT NULL,
  nombre VARCHAR(200) NOT NULL);
GO

USE [CLI_desercion]
GO
CREATE TABLE VWPROGRAMADESERCION (
  codigo NUMERIC(10,0) NOT NULL,
  nombre VARCHAR(200) NOT NULL,
  nombre_corto VARCHAR(10) NOT NULL,
  facultad INT NOT NULL,
  nombre_facultad VARCHAR(200) NOT NULL);
GO

-- Table Desercion Crudos
USE [CLI_desercion]
GO
CREATE TABLE VWDATADESERCION(
  REGISTRO INT NOT NULL,
  semestre INT NOT NULL,
  jornada VARCHAR(100) NOT NULL,
  nombre_completo VARCHAR(300) NOT NULL,
  tipo_documento VARCHAR(100) NOT NULL,
  documento VARCHAR(50) NOT NULL,
	edad INT,
	genero VARCHAR(100),
	estado_civil VARCHAR(100),
	lugar_residencia_sede VARCHAR(100) NOT NULL,
	trabaja VARCHAR(2) NOT NULL,
	etnia VARCHAR(300) NOT NULL,
	victima VARCHAR(2) NOT NULL,
	pertenece_grupo_vulnerable VARCHAR(2) NOT NULL,
	creditos_programa INT NOT NULL,
	creditos_aprobados_sem INT NOT NULL,
	creditos_aprobados_acum INT NOT NULL,
	asignaturas_aprobadas_sem INT NOT NULL,
	asignaturas_aprobadas_acum INT NOT NULL,
	creditos_reprobados_sem INT NOT NULL,
	creditos_reprobados_acum INT NOT NULL,
	asignaturas_reprobadas_sem INT NOT NULL,
	asignaturas_reprobadas_acum INT NOT NULL,
	creditos_cancelados_sem INT NOT NULL,
	creditos_cancelados_acum INT NOT NULL,
	creditos_matriculados_sem INT NOT NULL,
	creditos_matriculados_acum INT,
	promedio_semestre FLOAT,
	promedio_acumulado FLOAT,
	puntaje_icfes FLOAT,
	beca VARCHAR(2) NOT NULL,
	intersemestral VARCHAR(2) NOT NULL,
	desertor VARCHAR(2) NOT NULL,
	periodo_ingreso INT NOT NULL,
	ultimo_periodo INT,
	biologia FLOAT,
	ciencias_naturales FLOAT,
	ciencias_sociales FLOAT,
	competencias_ciudadanas FLOAT,
	filosofia FLOAT,
	fisica FLOAT,
	geografia FLOAT,
	historia FLOAT,
	ingles FLOAT,
	lectura_critica FLOAT,
	lenguaje FLOAT,
	matematicas FLOAT,
	quimica FLOAT,
	razonamiento_cuantitativo FLOAT,
	sociales_y_ciudadanas FLOAT,
	idmatricula VARCHAR(50) NOT NULL,
	idaspiracion VARCHAR(50) NOT NULL,
	idprograma VARCHAR(30) NOT NULL,
	programa VARCHAR(100) NOT NULL,
    tipo_programa VARCHAR(50) NOT NULL,
	idfacultad VARCHAR(30) NOT NULL,
	facultad VARCHAR(100) NOT NULL,
	estrato_residencia VARCHAR(50) NULL,
	celular_telefono VARCHAR(100) NULL,
	fecha_nacimiento VARCHAR(100) NULL,
	sanciones_multas VARCHAR(50),
	participacion_semillero_investigacion VARCHAR(50),
	correo_electronico VARCHAR(100) NULL,
	asignaturas_programa INT,
	asignaturas_canceladas_sem INT,
	asignaturas_canceladas_acum INT,
	DTFECHAREGISTRO DATE);
	-- idestado INT,);
GO

USE [CLI_desercion]
GO
CREATE TABLE TBLDES_RESULTADO_PREDICCION (
  documento VARCHAR(50) NOT NULL, 
  nombre_completo VARCHAR(300) NOT NULL, 
  desertor INT NOT NULL, 
  prediccion INT NOT NULL, 
  semestre_prediccion INT NOT NULL,
  idprograma VARCHAR(30) NOT NULL,
  blnultimo INT NULL);
GO