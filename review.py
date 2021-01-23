from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'hard to guess string'

class FaceForm(FlaskForm):
    face_pic = FileField('YOUR FACE PHOTO', validators=[DataRequired()])
    submit = SubmitField('Submit!')

@app.route('/', methods=['GET', 'POST'])
def index():
    face_file = None
    form = FaceForm()
    if form.validate_on_submit():
        face_file = form.name.data
        form.name.data = ''
    return render_template('index.html', form=form, face_file=face_file)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

