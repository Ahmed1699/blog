from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,HiddenField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
    # csrf_token=HiddenField(default=csrf.generate_csrf())

class RegisterForm(FlaskForm):
    name=StringField("name",validators=[DataRequired()])
    email=StringField("email",validators=[DataRequired()])
    password=PasswordField("password",validators=[DataRequired()])
    submit = SubmitField("Sign Up")
    # csrf_token=HiddenField(default=csrf.generate_csrf())


class LoginForm(FlaskForm):
    email=StringField("email",validators=[DataRequired()])
    password=PasswordField("password",validators=[DataRequired()])
    submit = SubmitField("Login")
    # csrf_token=HiddenField(default=csrf.generate_csrf())

class CommentForm(FlaskForm):
    comment_text=CKEditorField("comment",validators=[DataRequired()])
    submit = SubmitField("comment")
    # csrf_token=HiddenField(default=csrf.generate_csrf())

