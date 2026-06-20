from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FileField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length


class CaseSearchForm(FlaskForm):
    q = StringField("Search Cases", validators=[Length(max=255)])
    submit = SubmitField("Search")


class CaseCreateForm(FlaskForm):
    title = StringField(
        "Case Title",
        validators=[DataRequired(), Length(max=255)],
    )
    description = TextAreaField(
        "Description",
        validators=[Length(max=2000)],
    )
    client_id = StringField(
        "Client ID",
        validators=[DataRequired(), Length(max=36)],
    )
    submit = SubmitField("Create Case")


class CaseUpdateForm(FlaskForm):
    title = StringField(
        "Case Title",
        validators=[DataRequired(), Length(max=255)],
    )
    description = TextAreaField(
        "Description",
        validators=[Length(max=2000)],
    )
    status = SelectField(
        "Status",
        choices=[("open", "Open"), ("closed", "Closed")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Case")


class DocumentUploadForm(FlaskForm):
    title = StringField(
        "Document Title",
        validators=[DataRequired(), Length(max=255)],
    )
    file = FileField("File", validators=[DataRequired()])
    confidential = BooleanField("Confidential")
    submit = SubmitField("Upload Document")
