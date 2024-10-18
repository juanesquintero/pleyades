from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import update
from sqlalchemy.ext.hybrid import hybrid_property
from app import db


class DTO():
    def insert(_class, fields):
        row = _class(**fields)
        db.session.add(row)
        db.session.commit()
        return row

    def post_delete(_class, field):
        row = _class._get_one(field)
        db.session.delete(row)
        db.session.commit()
        return row

    def update(sql):
        row = db.session.execute(sql)
        db.session.commit()
        return row


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    correo = db.Column(db.String, primary_key=True, nullable=False)
    nombre = db.Column(db.String, nullable=False)
    clave = db.Column(db.String, nullable=False)
    rol = db.Column(db.String, nullable=False)

    def get_all():
        return [row.to_dict() for row in User.query.all()]

    def _get_one(correo):
        return User.query.filter(User.correo == correo).first_or_404()

    def get_one(correo):
        return User._get_one(correo).to_dict()

    def get_rol(rol):
        query = User.query.filter(User.rol == rol).all()
        return [row.to_dict() for row in query]

    def get_login(correo, clave):
        row = User.query.filter(
            User.correo == correo,
            User.clave == clave
        )
        if not row:
            return None
        try:
            return row.one().to_dict()
        except:
            return None

    def insert(fields):
        return DTO.insert(User, fields)

    def post_delete(correo):
        return DTO.delete(User, correo)

    def update(correo, fields):
        return DTO.update(
            update(User).where(User.correo == correo).values(**fields)
        )


class Set(db.Model, SerializerMixin):
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
        return [row.to_dict() for row in Set.query.all()]

    def get_state(estado):
        query = Set.query.filter(Set.estado == estado)
        return [row.to_dict() for row in query.all()]

    def get_tipo(tipo):
        query = Set.query.filter(Set.tipo == tipo)
        return [row.to_dict() for row in query.all()]

    def get_programa(programa):
        query = Set.query.filter(Set.programa == programa)
        return [row.to_dict() for row in query.all()]

    def get_rango(inicio, fin):
        query = Set.query.filter(
            Set.periodoInicial == inicio,
            Set.periodoFinal == fin,
        )
        return [row.to_dict() for row in query.all()]

    def get_numero(programa, inicio, fin):
        query = Set.query.filter(
            Set.programa == programa,
            Set.periodoInicial == inicio,
            Set.periodoFinal == fin
        ).order_by(Set.numero.desc())
        return [row.to_dict() for row in query.all()]

    def get_encargado(encargado, estado=None):
        query = Set.query.filter(Set.encargado == encargado)
        if estado:
            query = query.filter(Set.estado == estado)
        return [row.to_dict() for row in query.all()]

    def _get_one(nombre):
        return Set.query.filter(Set.nombre == nombre).first_or_404()

    def get_one(nombre):
        return Set._get_one(nombre).to_dict()

    def insert(fields):
        return DTO.insert(Set, fields)

    def post_delete(nombre):
        return DTO.delete(Set, nombre)

    def update(nombre, fields):
        return DTO.update(
            update(Set).where(
                Set.nombre == nombre).values(**fields)
        )


class Preparacion(db.Model, SerializerMixin):
    __tablename__ = 'preparations'
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
    student_set = db.Column(db.String, nullable=False)
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
        query = Preparacion.query.filter(
            Preparacion.conjunto == conjunto).all()
        return [row.to_dict() for row in query]

    def get_consecutivo(conjunto):
        query = Preparacion.query.filter(Preparacion.conjunto == conjunto)
        return [row.to_dict() for row in query.order_by(Preparacion.numero.desc()).all()]

    def get_preparador(preparador):
        query = Preparacion.query.filter(
            Preparacion.preparador == preparador).all()
        return [row.to_dict() for row in query]

    def _get_one(nombre):
        return Preparacion.query.filter(Preparacion.nombre == nombre).first_or_404()

    def get_one(nombre):
        return Preparacion._get_one(nombre).to_dict()

    def insert(fields):
        return DTO.insert(Preparacion, fields)

    def post_delete(nombre):
        return DTO.delete(Preparacion, nombre)

    def delete_conjunto(conjunto):
        return Preparacion.__table__.delete().where(Preparacion.conjunto == conjunto)

    def update(nombre, fields):
        return DTO.update(
            update(Preparacion).where(
                Preparacion.nombre == nombre).values(**fields)
        )


class Ejecucion(db.Model, SerializerMixin):
    __tablename__ = 'executions'
    serialize_only = (
        'ejecutor',
        'conjunto',
        'nombre',
        'numero',
        'fechaInicial',
        'fechaFinal',
        'estado',
        'precision_model',
        'resultados',
        'duracion'
    )

    ejecutor = db.Column(db.String, nullable=False)
    student_set = db.Column(db.String, nullable=False)
    nombre = db.Column(db.String, primary_key=True, nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    fechaInicial = db.Column(db.DateTime, nullable=False)
    fechaFinal = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String, nullable=False)
    precision_model = db.Column(db.Float, nullable=False)
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
        query = Ejecucion.query.filter(Ejecucion.conjunto == conjunto).all()
        return [row.to_dict() for row in query]

    def get_consecutivo(conjunto):
        query = Ejecucion.query.filter(Ejecucion.conjunto == conjunto)
        return [row.to_dict() for row in query.order_by(Ejecucion.numero.desc()).all()]

    def get_ejecutor(ejecutor):
        query = Ejecucion.query.filter(Ejecucion.ejecutor == ejecutor).all()
        return [row.to_dict() for row in query]

    def get_ejecutor_one(ejecutor, conjunto):
        query = Ejecucion.query.filter(
            Ejecucion.ejecutor == ejecutor, Ejecucion.conjunto == conjunto).all()
        return [row.to_dict() for row in query]

    def _get_one(nombre):
        return Ejecucion.query.filter(Ejecucion.nombre == nombre).first_or_404()

    def get_one(nombre):
        return Ejecucion._get_one(nombre).to_dict()

    def insert(fields):
        return DTO.insert(Ejecucion, fields)

    def post_delete(nombre):
        return DTO.delete(Ejecucion, nombre)

    def delete_conjunto(conjunto):
        return Ejecucion.__table__.delete().where(Ejecucion.conjunto == conjunto)

    def update(nombre, fields):
        return DTO.update(
            update(Ejecucion).where(
                Ejecucion.nombre == nombre).values(**fields)
        )
