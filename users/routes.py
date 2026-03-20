import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from extensions import db, bcrypt
from models import User, Movie

users_bp = Blueprint('users', __name__, template_folder='templates')

def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(7)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@users_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('รหัสผ่านไม่ตรงกัน กรุณาลองใหม่', 'danger')
            return redirect(url_for('users.register'))
        
        user_by_username = User.query.filter_by(username=username).first()
        if user_by_username:
            flash('ชื่อผู้ใช้นี้ถูกใช้งานแล้ว กรุณาใช้ชื่ออื่น', 'warning')
            return redirect(url_for('users.register'))

        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            flash('อีเมลนี้ถูกลงทะเบียนไว้แล้ว กรุณาเข้าสู่ระบบ', 'info')
            return redirect(url_for('users.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('สร้างบัญชีสำเร็จ! คุณสามารถเข้าสู่ระบบได้แล้ว', 'success')
        return redirect(url_for('users.login'))
        
    return render_template('users/register.html')

@users_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('core.index'))
        else:
            flash('ล็อกอินล้มเหลว ตรวจสอบชื่อและรหัสผ่าน', 'danger')
    return render_template('users/login.html')

@users_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('core.index'))

@users_bp.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        if request.files.get('image_file'):
            picture_file = save_profile_picture(request.files.get('image_file'))
            current_user.image_file = picture_file
            
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.nickname = request.form.get('nickname')
        current_user.full_name = request.form.get('full_name')
        current_user.bio = request.form.get('bio')
        
        db.session.commit()
        flash('อัปเดตข้อมูลเรียบร้อยแล้ว', 'success')
        return redirect(url_for('users.account'))
    
    user_movies = Movie.query.filter_by(author=current_user).all()
    total_movies = len(user_movies)
    avg_rating = round(sum(m.rating for m in user_movies) / total_movies, 1) if total_movies > 0 else 0
        
    return render_template('users/account.html', total_movies=total_movies, avg_rating=avg_rating)

@users_bp.route("/change-password", methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not bcrypt.check_password_hash(current_user.password, old_password):
            flash('รหัสผ่านเดิมไม่ถูกต้อง', 'danger')
        elif new_password != confirm_password:
            flash('รหัสผ่านใหม่ไม่ตรงกัน', 'danger')
        else:
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('เปลี่ยนรหัสผ่านสำเร็จแล้ว', 'success')
            return redirect(url_for('users.account'))
            
    return render_template('users/change_password.html')
