from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import update
from sqlalchemy.ext.hybrid import hybrid_property
from app import  db


class DTO():    
    def insert(_class, fields):
        row = _class(**fields)
        db.session.add(row)
        db.session.commit()
        return row
    
    def delete(_class, field):
        row = _class._get_one(field)
        db.session.delete(row)
        db.session.commit()
        return row
    
    def update(sql):
        row = db.session.execute(sql)
        db.session.commit()
        return row


class Usuario(db.Model, SerializerMixin):
    __tablename__ = 'usuarios'
    correo = db.Column(db.String, primary_key=True, nullable=False)
    nombre = db.Column(db.String, nullable=False)
    clave = db.Column(db.String, nullable=False)
    rol = db.Column(db.String, nullable=False)

    def get_all():
        return [row.to_dict() for row in Usuario.query.all()]

    def _get_one(correo):
        return Usuario.query.filter(Usuario.correo==correo).first_or_404()
    
    def get_one(correo):
        return Usuario._get_one(correo).to_dict()
    
    def get_rol(rol):
        query = Usuario.query.filter(Usuario.rol==rol).all()
        return [row.to_dict() for row in query]

    def get_login(correo,clave):
        row = Usuario.query.filter(
            Usuario.correo==correo,
            Usuario.clave==clave
        ).one()
        return row.to_dict()
    
    def insert(fields):
        return DTO.insert(Usuario, fields)

    def delete(correo):
        return DTO.delete(Usuario, correo)
    
    def update(correo, fields):
        return DTO.update(
            update(Usuario).where(Usuario.correo == correo).values(**fields)
        )



class Conjunto(db.Model, SerializerMixin):
    __tablename__ = 'conjuntosdedatos'

    programa = db.Column(db.Integer, nullable=False)
    encargado = db.Column(db.String, nullable=False)
    nombre = db.Column(db.String, primary_key=True, nullable=False)
    tipo = db.Column(db.String, nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    periodoInicial = db.Column(db.Integer, nullable=False)
    periodoFinal = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String, nullable=False)
    
    def get_all():
        return [row.to_dict() for row in Conjunto.query.all()]

    def get_estado(estado):
        query = Conjunto.query.filter(Conjunto.estado==estado)
        return [row.to_dict() for row in query.all()]
    
    def get_tipo(tipo):
        query = Conjunto.query.filter(Conjunto.tipo==tipo)
        return [row.to_dict() for row in query.all()]
        
    def get_programa(programa):
        query = Conjunto.query.filter(Conjunto.programa==programa)
        return [row.to_dict() for row in query.all()]

    def get_rango(inicio, fin):
        query = Conjunto.query.filter(
            Conjunto.periodoInicial==inicio,
            Conjunto.periodoFinal==fin,
        )
        return [row.to_dict() for row in query.all()]

    def get_numero(programa, inicio, fin):
        query = Conjunto.query.filter(
            Conjunto.programa==programa,
            Conjunto.periodoInicial==inicio,
            Conjunto.periodoFinal==fin
        ).order_by(Conjunto.numero.desc())
        return [row.to_dict() for row in query.all()]

    def get_encargado(encargado, estado=None):
        query = Conjunto.query.filter(Conjunto.encargado==encargado)
        if estado:
            query = query.filter(Conjunto.estado==estado)
        return [row.to_dict() for row in query.all()]

    def _get_one(nombre):
        return Conjunto.query.filter(Conjunto.nombre==nombre).first_or_404()
    
    def get_one(nombre):
        return Conjunto._get_one(nombre).to_dict()
        
    def insert(fields):
        return DTO.insert(Conjunto, fields)

    def delete(nombre):
        return DTO.delete(Conjunto, nombre)
    
    def update(nombre, fields):
        return DTO.update(
            update(Conjunto).where(Conjunto.nombre == nombre).values(**fields)
        )


class Preparacion(db.Model, SerializerMixin):
    __tablename__ = 'preparaciones'
    serialize_only = (
        'preparador',
        'conjunto',
        'nombre',
        'numero',
        'fechaInicial',
        'fechaFinal',
        'estado',
        'observaciones', 
        'duracion'
    )

    preparador = db.Column(db.String, nullable=False)
    conjunto = db.Column(db.String, nullable=False)
    nombre = db.Column(db.String, primary_key=True, nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    fechaInicial = db.Column(db.DateTime, nullable=False)
    fechaFinal = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String, nullable=False)
    observaciones = db.Column(JSON, nullable=True)

    @hybrid_property
    def duracion(self):
        return int((self.fechaFinal - self.fechaInicial).total_seconds())
        
    @duracion.expression
    def duracion(cls):
        return int((cls.fechaFinal - cls.fechaInicial).total_seconds())

    def get_all():
        return [row.to_dict() for row in Preparacion.query.all()]
    
    def get_conjunto(conjunto):
        query = Preparacion.query.filter(Preparacion.conjunto==conjunto).all()
        return [row.to_dict() for row in query]
    
    def get_consecutivo(conjunto):
        query = Preparacion.query.filter(Preparacion.conjunto==conjunto)
        return [row.to_dict() for row in query.order_by(Preparacion.numero.desc()).all()]
    
    def get_preparador(preparador):
        query = Preparacion.query.filter(Preparacion.preparador==preparador).all()
        return [row.to_dict() for row in query]

    def _get_one(nombre):
        return Preparacion.query.filter(Preparacion.nombre==nombre).first_or_404()
    
    def get_one(nombre):
        return Preparacion._get_one(nombre).to_dict()
    
    def insert(fields):
        return DTO.insert(Preparacion, fields)

    def delete(nombre):
        return DTO.delete(Preparacion, nombre)

    def delete_conjunto(conjunto):
        return Preparacion.__table__.delete().where(Preparacion.conjunto==conjunto)
    
    def update(nombre, fields):
        return DTO.update(
            update(Preparacion).where(Preparacion.nombre == nombre).values(**fields)
        )

class Ejecucion(db.Model, SerializerMixin):
    __tablename__ = 'ejecuciones'
    serialize_only = (
        'ejecutor',
        'conjunto',
        'nombre',
        'numero',
        'fechaInicial',
        'fechaFinal',
        'estado',
        'precision_modelo',
        'resultados', 
        'duracion'
    )

    ejecutor = db.Column(db.String, nullable=False)
    conjunto = db.Column(db.String, nullable=False)
    nombre = db.Column(db.String, primary_key=True, nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    fechaInicial = db.Column(db.DateTime, nullable=False)
    fechaFinal = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String, nullable=False)
    precision_modelo = db.Column(db.Float, nullable=False)
    resultados = db.Column(db.String, nullable=False)

    @hybrid_property
    def duracion(self):
        return int((self.fechaFinal - self.fechaInicial).total_seconds())
        
    @duracion.expression
    def duracion(cls):
        return int((cls.fechaFinal - cls.fechaInicial).total_seconds())

    def get_all():
        return [row.to_dict() for row in Ejecucion.query.all()]

    def get_conjunto(conjunto):
        query = Ejecucion.query.filter(Ejecucion.conjunto==conjunto).all()
        return [row.to_dict() for row in query]
    
    def get_consecutivo(conjunto):
        query = Ejecucion.query.filter(Ejecucion.conjunto==conjunto)
        return [row.to_dict() for row in query.order_by(Ejecucion.numero.desc()).all()]
    
    def get_ejecutor(ejecutor):
        query = Ejecucion.query.filter(Ejecucion.ejecutor==ejecutor).all()
        return [row.to_dict() for row in query]

    def _get_one(nombre):
        return Ejecucion.query.filter(Ejecucion.nombre==nombre).first_or_404()
    
    def get_one(nombre):
        return Ejecucion._get_one(nombre).to_dict()
    
    def insert(fields):
        return DTO.insert(Ejecucion, fields)

    def delete(nombre):
        return DTO.delete(Ejecucion, nombre)
    
    def delete_conjunto(conjunto):
        return Ejecucion.__table__.delete().where(Ejecucion.conjunto==conjunto)
    
    def update(nombre, fields):
        return DTO.update(
            update(Ejecucion).where(Ejecucion.nombre == nombre).values(**fields)
        )