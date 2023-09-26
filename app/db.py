from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, MetaData, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import orm
import aiohttp_sqlalchemy as ahsa


engine = create_async_engine('sqlite+aiosqlite:///app.db')
Session = orm.sessionmaker(engine, AsyncSession)
metadata = MetaData()
Base = orm.declarative_base(metadata=metadata)

class Users(Base):
    __tablename__ = 'users'
    metadata = metadata
    id = Column(Integer, primary_key=True)
    email = Column(String(32), index=True, unique=True)
    name = Column(String(64))
    password = Column(String(64), nullable=False)
    ads = relationship('Ads', backref='owner', lazy='dynamic')


class Ads(Base):
    __tablename__ = 'ads'
    metadata = metadata
    id = Column(Integer, primary_key=True)
    title = Column(String(32), index=True, unique=True)
    description = Column(String(255))
    adv_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

async def db_context(app):
    ahsa.setup(app, [
        ahsa.bind(Session),
    ])
    await ahsa.init_db(app, metadata)
    yield


async def auth_context(token: str):
    session = Session()
    user = await session.execute(select(Users).where(Users.password == token))
    user = user.fetchone()
    await session.close()
    if not user:
        user = None
    else:
        user = user[0]
    return user