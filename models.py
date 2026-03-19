from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # ข้อมูลโปรไฟล์ตามที่คุณออกแบบไว้ใน HTML
    nickname = db.Column(db.String(50))
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    movies = db.relationship('Movie', backref='author', lazy=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100))
    rating = db.Column(db.Float)
    note = db.Column(db.Text)
    image_file = db.Column(db.String(20), nullable=False, default='default_movie.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # เชื่อมว่าใครเป็นคนเพิ่มหนังเรื่องนี้ (อ้างอิงจาก id ของ User)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)