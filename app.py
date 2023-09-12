# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, validators
from flask_wtf import FlaskForm
import string
import random
# for Caching [start]
import redis

# Initialize Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
# for Caching [end]

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Models


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(10), unique=True, nullable=False)

# Forms


class URLForm(FlaskForm):
    url = StringField(
        'Enter URL', [validators.DataRequired(), validators.URL()])

# Helper Functions


def generate_short_id(num_chars=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))

# Routes


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    short_url = None
    if form.validate_on_submit():
        original_url = form.url.data
        existing = URL.query.filter_by(original_url=original_url).first()
        if existing:
            short_url = request.host_url + existing.short_id
        else:
            short_id = generate_short_id()
            new_url = URL(original_url=original_url, short_id=short_id)
            db.session.add(new_url)
            db.session.commit()
            short_url = request.host_url + short_id
    return render_template('index.html', form=form, short_url=short_url)


""" @app.route('/<short_id>')
def redirect_url(short_id):
    url = URL.query.filter_by(short_id=short_id).first_or_404()
    return redirect(url.original_url) """


@app.route('/<short_id>')
def redirect_url(short_id):
    # Check cache first
    original_url = redis_client.get(f"short:{short_id}")
    if not original_url:
        url = URL.query.filter_by(short_id=short_id).first_or_404()
        original_url = url.original_url
        redis_client.setex(f"short:{short_id}", 86400,
                           original_url)  # Cache for 1 day
    return redirect(original_url)


@app.route('/dashboard')
def dashboard():
    urls = URL.query.all()
    return render_template('dashboard.html', urls=urls)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
