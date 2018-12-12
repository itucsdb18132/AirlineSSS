from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Email
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed, FileRequired

images = UploadSet('images', IMAGES)

class formSendPost(FlaskForm):
    title = StringField('Title:', validators=[InputRequired()], render_kw={"placeholder": "Title"})
    content = TextAreaField('Your post:', validators=[InputRequired()], render_kw={"rows": 5, "placeholder": "Enter something..."})
    image = FileField('Upload an image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    def validate(self):

        firstValidation = FlaskForm.validate(self)
        if not firstValidation:
            if not self.title.data.strip():
                self.title.errors.append('Title can not be empty')
            if not self.content.data.strip():
                self.content.errors.append('Content can not be empty')
            return False
        hasErrors = False
        if not self.title.data.strip():
            hasErrors = True
            self.title.errors.append('Title can not be empty')
        if not self.content.data.strip():
            hasErrors = True
            self.content.errors.append('Content can not be empty')
        if hasErrors:
            return False
        else:
            return True

class formForgotPass(FlaskForm):
    username = StringField('Username:', validators=[InputRequired()], render_kw={"placeholder": "Enter your username"})
    def validate(self):

        firstValidation = FlaskForm.validate(self)
        if not firstValidation:
            return False
        if not self.username.data.strip():
            self.username.errors.append('Please enter a username')
            return False
        return True


class formLogin(FlaskForm):
    username = StringField('Username:', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = StringField('Password:', validators=[InputRequired()], render_kw={"placeholder": "Password"})

class formRegister(FlaskForm):
    name = StringField('Fullname:', validators=[InputRequired()], render_kw={"placeholder": "Your fullname"})
    username = StringField('Username:', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    email = StringField('Email:', validators=[InputRequired(), Email(message='Use a valid email address')], render_kw={"placeholder": "Your email address"})
    password = PasswordField('Password:', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')], render_kw={"placeholder": "Password"})
    confirm = PasswordField('Confirm Password:', validators=[InputRequired()], render_kw={"placeholder": "Confirm password"})

    def validate(self):

        firstValidation = FlaskForm.validate(self)
        if not firstValidation:
            if not self.name.data.strip():
                self.name.errors.append('Fullname can not be empty')
            if not self.username.data.strip():
                self.username.errors.append('Username can not be empty')
            if not self.email.data.strip():
                self.email.errors.append('Email can not be empty')
            if not self.password.data.strip():
                self.password.errors.append('Password can not be empty')
            return False
        hasErrors = False
        if not self.name.data.strip():
            hasErrors = True
            self.name.errors.append('Fullname can not be empty')
        if not self.username.data.strip():
            hasErrors = True
            self.username.errors.append('Username can not be empty')
        if not self.email.data.strip():
            hasErrors = True
            self.email.errors.append('Email can not be empty')
        if not self.password.data.strip():
            hasErrors = True
            self.password.errors.append('Password can not be empty')
        if hasErrors:
            return False
        else:
            return True

class formDiscount (FlaskForm):
    id = SelectField('ID:', validators=[InputRequired()])
    discount = StringField('Discount:', validators=[InputRequired()], render_kw={"placeholder": "Discount rate"})


class formEditUser(FlaskForm):
    fullname = StringField('Fullname:')
    email = StringField('Email:')
    password = PasswordField('Password:')
