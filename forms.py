from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, validators

class LogParseForm(FlaskForm):
    file_name = FileField(label='Choose file', 
        validators=[
            validators.regexp('.json$')
        ]
    )
    submit = SubmitField(label='Upload')

class GraphicGeneratorForm(FlaskForm):
    race_title = StringField(label='Race title',
        validators= [
            validators.InputRequired()
        ]
    )
    json_file_name = StringField(label='Results path',
        validators= [
            validators.InputRequired()
        ]
    )
    submit = SubmitField(label='Submit')
