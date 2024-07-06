# main.py

from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        return f'<URL {self.short_url}>'


def generate_short_url():
    characters = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(characters, k=6))
        if not URL.query.filter_by(short_url=short_url).first():
            return short_url


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']
        if URL.query.filter_by(original_url=original_url).first():
            short_url = URL.query.filter_by(
                original_url=original_url).first().short_url
        else:
            short_url = generate_short_url()
            new_url = URL()
            new_url.original_url = original_url
            new_url.short_url = short_url
            db.session.add(new_url)
            db.session.commit()
        return render_template('home.html', short_url=short_url)
    return render_template('home.html')


@app.route('/<short_url>')
def redirect_to_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.original_url)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=8080)
