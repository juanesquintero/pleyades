import traceback
from api.app.utils.constants import Roles
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import update
from sqlalchemy.ext.hybrid import hybrid_property
from api.app.main import db


class DTO():
    @staticmethod
    def insert(_class, fields):
        row = _class(**fields)
        db.session.add(row)
        db.session.commit()
        return row

    @staticmethod
    def post_delete(_class, field):
        row = _class._get_one(field)
        db.session.delete(row)
        db.session.commit()
        return row

    @staticmethod
    def update(sql):
        row = db.session.execute(sql)
        db.session.commit()
        return row

    @staticmethod
    def delete(_class, field):
        row = _class._get_one(field)
        db.session.delete(row)
        db.session.commit()


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    email = db.Column(db.String, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

    @staticmethod
    def get_all():
        return [row.to_dict() for row in User.query.all()]

    @staticmethod
    def _get_one(email):
        return User.query.filter(User.email == email).first_or_404()

    @staticmethod
    def get_one(email):
        return User._get_one(email).to_dict()

    @staticmethod
    def get_role(role):
        query = User.query.filter(User.role == role).all()
        return [row.to_dict() for row in query]

    @staticmethod
    def get_login(email, password):
        row = User.query.filter(
            User.email == email,
            User.password == password
        )
        if not row:
            return None
        try:
            return row.one().to_dict()
        except Exception as e:
            print(e, traceback.format_exc(), flush=True)
            return None

    @staticmethod
    def insert(fields):
        return DTO.insert(User, fields)

    @staticmethod
    def post_delete(email):
        return DTO.delete(User, email)

    @staticmethod
    def update(email, fields):
        return DTO.update(
            update(User).where(User.email == email).values(**fields)
        )


class Dataset(db.Model, SerializerMixin):
    __tablename__ = 'datasets'

    program = db.Column(db.Integer, nullable=False)
    manager = db.Column(db.String, nullable=False)
    name = db.Column(db.String, primary_key=True, nullable=False)
    type = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    initialPeriod = db.Column(db.Integer, nullable=False)
    finalPeriod = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)

    @staticmethod
    def get_all():
        return [row.to_dict() for row in Dataset.query.all()]

    @staticmethod
    def get_status(status):
        query = Dataset.query.filter(Dataset.status == status)
        return [row.to_dict() for row in query.all()]

    @staticmethod
    def get_type(type):
        query = Dataset.query.filter(Dataset.type == type)
        return [row.to_dict() for row in query.all()]

    @staticmethod
    def get_program(program):
        query = Dataset.query.filter(Dataset.program == program)
        return [row.to_dict() for row in query.all()]

    @staticmethod
    def get_range(start, end):
        query = Dataset.query.filter(
            Dataset.initialPeriod == start,
            Dataset.finalPeriod == end,
        )
        return [row.to_dict() for row in query.all()]

    @staticmethod
    def get_number(program, start, end):
        query = Dataset.query.filter(
            Dataset.program == program,
            Dataset.initialPeriod == start,
            Dataset.finalPeriod == end
        ).order_by(Dataset.number.desc())
        return [row.to_dict() for row in query.all()]

    @staticmethod
    def get_manager(manager, status=None):
        query = Dataset.query.filter(Dataset.manager == manager)
        if status:
            query = query.filter(Dataset.status == status)
        return [row.to_dict() for row in query.all()]

    @staticmethod
    def _get_one(name):
        return Dataset.query.filter(Dataset.name == name).first_or_404()

    @staticmethod
    def get_one(name):
        return Dataset._get_one(name).to_dict()

    @staticmethod
    def insert(fields):
        return DTO.insert(Dataset, fields)

    @staticmethod
    def post_delete(name):
        return DTO.delete(Dataset, name)

    @staticmethod
    def update(name, fields):
        return DTO.update(
            update(Dataset).where(
                Dataset.name == name).values(**fields)
        )


class Preparation(db.Model, SerializerMixin):
    __tablename__ = 'preparations'
    serialize_only = (
        Roles.PROCESSOR,
        'dataset',
        'name',
        'number',
        'startDate',
        'endDate',
        'status',
        'observations',
        'duration'
    )

    processor = db.Column(db.String, nullable=False)
    dataset = db.Column(db.String, nullable=False)
    name = db.Column(db.String, primary_key=True, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    observations = db.Column(JSON, nullable=True)

    @hybrid_property
    def duration(self):
        return int((self.endDate - self.startDate).total_seconds())

    @duration.expression
    def duration(cls):
        return int((cls.endDate - cls.startDate).total_seconds())

    @staticmethod
    def get_all():
        return [row.to_dict() for row in Preparation.query.all()]

    @staticmethod
    def get_dataset(dataset):
        query = Preparation.query.filter(
            Preparation.dataset == dataset).all()
        return [row.to_dict() for row in query]

    @staticmethod
    def get_consecutive(dataset):
        query = Preparation.query.filter(Preparation.dataset == dataset)
        return [row.to_dict() for row in query.order_by(Preparation.number.desc()).all()]

    @staticmethod
    def get_preparer(processor):
        query = Preparation.query.filter(
            Preparation.processor == processor).all()
        return [row.to_dict() for row in query]

    @staticmethod
    def _get_one(name):
        return Preparation.query.filter(Preparation.name == name).first_or_404()

    @staticmethod
    def get_one(name):
        return Preparation._get_one(name).to_dict()

    @staticmethod
    def insert(fields):
        return DTO.insert(Preparation, fields)

    @staticmethod
    def post_delete(name):
        return DTO.delete(Preparation, name)

    @staticmethod
    def delete_dataset(dataset):
        return Preparation.__table__.delete().where(Preparation.dataset == dataset)

    @staticmethod
    def update(name, fields):
        return DTO.update(
            update(Preparation).where(
                Preparation.name == name).values(**fields)
        )


class Execution(db.Model, SerializerMixin):
    __tablename__ = 'executions'
    serialize_only = (
        Roles.EXECUTOR,
        'dataset',
        'name',
        'number',
        'startDate',
        'endDate',
        'status',
        'modelPrecision',
        'results',
        'duration'
    )

    executor = db.Column(db.String, nullable=False)
    dataset = db.Column(db.String, nullable=False)
    name = db.Column(db.String, primary_key=True, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    modelPrecision = db.Column(db.Float, nullable=False)
    results = db.Column(db.String, nullable=False)

    @hybrid_property
    def duration(self):
        return int((self.endDate - self.startDate).total_seconds())

    @duration.expression
    def duration(cls):
        return int((cls.endDate - cls.startDate).total_seconds())

    @staticmethod
    def get_all():
        return [row.to_dict() for row in Execution.query.all()]

    @staticmethod
    def get_dataset(dataset):
        query = Execution.query.filter(Execution.dataset == dataset).all()
        return [row.to_dict() for row in query]

    @staticmethod
    def get_consecutive(dataset):
        query = Execution.query.filter(Execution.dataset == dataset)
        return [row.to_dict() for row in query.order_by(Execution.number.desc()).all()]

    @staticmethod
    def get_executor(executor):
        query = Execution.query.filter(Execution.executor == executor).all()
        return [row.to_dict() for row in query]

    @staticmethod
    def get_executor_one(executor, dataset):
        query = Execution.query.filter(
            Execution.executor == executor, Execution.dataset == dataset).all()
        return [row.to_dict() for row in query]

    @staticmethod
    def _get_one(name):
        return Execution.query.filter(Execution.name == name).first_or_404()

    @staticmethod
    def get_one(name):
        return Execution._get_one(name).to_dict()

    @staticmethod
    def insert(fields):
        return DTO.insert(Execution, fields)

    @staticmethod
    def post_delete(name):
        return DTO.delete(Execution, name)

    @staticmethod
    def delete_dataset(dataset):
        return Execution.__table__.delete().where(
            Execution.dataset == dataset
        )

    @staticmethod
    def update(name, fields):
        return DTO.update(
            update(Execution).where(
                Execution.name == name
            ).values(**fields)
        )
