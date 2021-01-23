from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'hard to guess string'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/uploads')

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
    submit = SubmitField('Upload!')

@app.route('/', methods=['GET', 'POST'])
def index():
    file_url = None
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        session['file_url'] = file_url = photos.url(filename)
        return redirect(url_for('index'))
    return render_template('index.html', form=form, file_url=session.get('file_url'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

