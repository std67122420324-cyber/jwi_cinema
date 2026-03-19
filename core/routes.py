from flask import Blueprint, render_template, request
from models import Movie

core_bp = Blueprint('core', __name__, template_folder='templates')

@core_bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search')
    
    if search_query:
        movies = Movie.query.filter(Movie.title.ilike(f'%{search_query}%')).order_by(Movie.date_posted.desc()).paginate(page=page, per_page=6)
    else:
        movies = Movie.query.order_by(Movie.date_posted.desc()).paginate(page=page, per_page=6)
        
    return render_template('core/index.html', movies=movies, search_query=search_query)