from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField, PasswordField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, InputRequired, ValidationError, EqualTo
from app.models import User


class AdminRegistrationForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()])
    date_joined = DateField('Date joined:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user is not None:
            raise ValidationError('Name already registered!')


class LoginForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class StaffRegistrationForm(FlaskForm):
    name = StringField('Full Name:', validators=[DataRequired()])
    position = SelectField('Position', validators=[InputRequired()], choices=[('Team lead', 'Team lead'), ('Member', 'Member'), ('New joiner', 'New Joiner')])
    date_joined = DateField('Date joined:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
    submit = SubmitField('Submit')


class EditStaffInfoForm(FlaskForm):
    name = StringField('Full Name:', validators=[DataRequired()])
    position = SelectField('Position', validators=[InputRequired()], choices=[('Team lead', 'Team lead'), ('Member', 'Member'), ('New joiner', 'New Joiner')])
    machine_certified = BooleanField('Machine certified')
    date_joined = DateField('Date joined:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
    submit = SubmitField('Submit')


class PrcessedSamplesForm(FlaskForm):
    date = DateField('Date:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
    shift = SelectField('Shift', coerce=int, validators=[InputRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Submit')
    

class RegisterStationsForm(FlaskForm):
    name = StringField('Station Name:', validators=[DataRequired()])
    assignments = IntegerField('Staff quantity:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterShiftForm(FlaskForm):
    name = StringField('Shift Name:', validators=[DataRequired()])
    submit = SubmitField('Submit')
	
	
class FilterPlateDateForm(FlaskForm):
	plate_date = SelectField('Plate date', coerce=str, validators=[InputRequired()])
	submit = SubmitField('Submit')
	
	
class RetestFileForm(FlaskForm):
	retest_file_name = FileField('File', validators=[InputRequired()])
	rff_submit = SubmitField('Submit')
	
	
class RunSummaryFileForm(FlaskForm):
	run_summary_file_name = FileField('File', validators=[InputRequired()])
	rsff_submit = SubmitField('Submit')