from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

engine = create_engine('sqlite:///Data_Base.db', echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    nickname = Column(String,nullable=True)
    avatar = Column(Boolean)
    videos = relationship('Video', back_populates='author')  
    likes = relationship('Likes', back_populates='user')
    subscribe = relationship('Subscribe', back_populates='user')

class Video(Base):
    __tablename__ = 'videos' 
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    new_filename = Column(String, nullable=True)
    preview = Column(Boolean)
    author = relationship('User', back_populates='videos')
    likes = relationship('Likes', back_populates='video')
    subscribe = relationship('Subscribe', back_populates='video')
    

class Likes(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    video_id = Column(Integer, ForeignKey('videos.id'))
    is_liked = Column(Boolean)
    user = relationship('User', back_populates='likes')
    video = relationship('Video', back_populates='likes')

class Subscribe(Base):
    __tablename__ = 'Subscribes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    author_id = Column(Integer, ForeignKey('videos.id'))
    subscribed = Column(Boolean)
    user = relationship('User', back_populates='subscribe')
    video = relationship('Video', back_populates='subscribe')


class Comments(Base):
    __tablename__ = 'Comments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    video_id = Column(Integer, ForeignKey('videos.id'))
    text = Column(String, nullable=False)


# Session = sessionmaker(bind=engine)
# session=Session()
# third=session.query(Video).filter_by(id=8).first()
# third.preview=True
# session.commit()
# session.close()

Base.metadata.create_all(engine)
