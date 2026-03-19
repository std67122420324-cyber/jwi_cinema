import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Movie

movies_bp = Blueprint('movies', __name__, template_folder='templates')

def save_movie_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/movie_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@movies_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_movie():
    if request.method == 'POST':
        movie = Movie(
            title=request.form.get('title'),
            genre=request.form.get('genre'),
            rating=request.form.get('rating'),
            note=request.form.get('note'),
            author=current_user
        )
        
        if request.files.get('image_file'):
            picture_file = save_movie_picture(request.files.get('image_file'))
            movie.image_file = picture_file 
        
        db.session.add(movie)
        db.session.commit()
        flash('เพิ่มหนังเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('core.index'))
        
    return render_template('movies/create_movie.html')

@movies_bp.route("/<int:movie_id>")
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template('movies/movie_detail.html', movie=movie)

@movies_bp.route("/<int:movie_id>/update", methods=['GET', 'POST'])
@login_required
def update_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.author != current_user:
        flash('คุณไม่มีสิทธิ์แก้ไข', 'danger')
        return redirect(url_for('core.index'))
    
    if request.method == 'POST':
        if request.files.get('image_file'):
            picture_file = save_movie_picture(request.files.get('image_file'))
            movie.image_file = picture_file
            
        movie.title = request.form.get('title')
        movie.genre = request.form.get('genre')
        movie.rating = request.form.get('rating')
        movie.note = request.form.get('note')
        db.session.commit()
        flash('อัปเดตสำเร็จ!', 'success')
        return redirect(url_for('movies.movie_detail', movie_id=movie.id))
        
    return render_template('movies/update_movie.html', movie=movie)

@movies_bp.route("/<int:movie_id>/delete", methods=['POST'])
@login_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.author == current_user:
        db.session.delete(movie)
        db.session.commit()
        flash('ลบหนังเรียบร้อย', 'success')
    return redirect(url_for('core.index'))