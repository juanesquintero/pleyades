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

CREATE TABLE [dbo].[VWDATADESERCION](
	[REGISTRO] [varchar](60) NULL,
	[semestre] [int] NULL,
	[jornada] [varchar](50) NOT NULL,
	[nombre_completo] [varchar](653) NULL,
	[tipo_documento] [varchar](50) NULL,
	[documento] [varchar](500) NULL,
	[edad] [int] NULL,
	[genero] [varchar](20) NULL,
	[estado_civil] [varchar](50) NULL,
	[lugar_residencia_sede] [varchar](507) NULL,
	[trabaja] [varchar](2) NOT NULL,
	[etnia] [varchar](50) NULL,
	[victima] [varchar](2) NOT NULL,
	[pertenece_grupo_vulnerable] [varchar](2) NOT NULL,
	[creditos_programa] [numeric](38, 0) NULL,
	[creditos_aprobados_sem] [numeric](38, 0) NULL,
	[creditos_aprobados_acum] [numeric](38, 0) NULL,
	[asignaturas_aprobadas_sem] [int] NULL,
	[asignaturas_aprobadas_acum] [int] NULL,
	[creditos_reprobados_sem] [numeric](38, 0) NULL,
	[creditos_reprobados_acum] [numeric](38, 0) NULL,
	[asignaturas_reprobadas_sem] [int] NULL,
	[asignaturas_reprobadas_acum] [int] NULL,
	[creditos_cancelados_sem] [numeric](38, 0) NULL,
	[creditos_cancelados_acum] [numeric](38, 0) NULL,
	[creditos_matriculados_sem] [numeric](38, 0) NULL,
	[creditos_matriculados_acum] [numeric](38, 0) NULL,
	[promedio_semestre] [float] NULL,
	[promedio_acumulado] [float] NULL,
	[puntaje_icfes] [float] NULL,
	[beca] [varchar](2) NOT NULL,
	[intersemestral] [varchar](2) NOT NULL,
	[desertor] [varchar](2) NOT NULL,
	[periodo_ingreso] [varchar](61) NULL,
	[ultimo_periodo] [varchar](61) NULL,
	[biologia] [float] NULL,
	[ciencias_naturales] [float] NULL,
	[ciencias_sociales] [float] NULL,
	[competencias_ciudadanas] [float] NULL,
	[filosofia] [float] NULL,
	[fisica] [float] NULL,
	[geografia] [float] NULL,
	[historia] [float] NULL,
	[ingles] [float] NULL,
	[lectura_critica] [float] NULL,
	[lenguaje] [float] NULL,
	[matematicas] [float] NULL,
	[quimica] [float] NULL,
	[razonamiento_cuantitativo] [float] NULL,
	[sociales_y_ciudadanas] [float] NULL,
	[idmatricula] [numeric](10, 0) NULL,
	[idaspiracion] [numeric](10, 0) NULL,
	[programa] [varchar](153) NULL,
	[tipo_programa] [varchar](64) NOT NULL,
	[idprograma] [numeric](10, 0) NULL,
	[idfacultad] [numeric](10, 0) NOT NULL,
	[facultad] [varchar](128) NOT NULL,
	[estrato_residencia] [varchar](20) NULL,
	[celular_telefono] [varchar](100) NULL,
	[fecha_nacimiento] [varchar](20) NULL,
	[sanciones_multas] [varchar](20) NULL,
	[participacion_semillero_investigacion] [varchar](20) NULL,
	[correo_electronico] [varchar](200) NULL,
	[asignaturas_programa] [int] NULL,
	[asignaturas_canceladas_sem] [int] NULL,
	[asignaturas_canceladas_acum] [int] NULL,
	[DTFECHAREGISTRO] [datetime] NULL,
	[idestado] [numeric](10, 0) NULL
) 
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
