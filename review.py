import io
import json

from flask import Flask, render_template, session, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired
import os
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
import ssl

import ipdb

ssl._create_default_https_context = ssl._create_unverified_context

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


imagenet_class_index = json.load(open('imagenet_class_index.json'))
model = models.densenet121(pretrained=True)
model.eval()


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]

@app.route('/', methods=['GET', 'POST'])
def index():
    file_url = None
    class_name = None
    form = UploadForm()
    if form.validate_on_submit():
        photo_data = form.photo.data
        filename = photos.save(photo_data)
        session['file_url'] = photos.url(filename)
        photo_data.seek(0)
        img_bytes = photo_data.read()
        class_id, class_name = get_prediction(image_bytes=img_bytes)
        session['class_name'] = class_name
        return redirect(url_for('index'))
    return render_template('index.html', form=form, file_url = session.get('file_url'), class_name = session.get('class_name'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

