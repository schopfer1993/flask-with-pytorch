from flask import render_template, session, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
import json
import ssl
import io
#import ipdb

from config import config
from .. import photos
from . import main

ssl._create_default_https_context = ssl._create_unverified_context

class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
    submit = SubmitField('Upload!')

import os
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = 'imagenet_class_index.json'
abs_file_path = os.path.join(script_dir, rel_path)

imagenet_class_index = json.load(open(abs_file_path))
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

@main.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))
    return render_template('index.html', form=form, file_url = session.get('file_url'), class_name = session.get('class_name'))