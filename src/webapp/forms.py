from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, FloatField
from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import NumberRange
from wtforms.validators import DataRequired, Email


class TeamRegisterForm(FlaskForm):
    teamname = StringField("Teamname", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Telefonnummer", validators=[DataRequired()])
    street = StringField("Adresse", validators=[DataRequired()])
    streetnumber = StringField("Hausnummer", validators=[DataRequired()])
    zipno = StringField("Postleitzahl", validators=[DataRequired()])
    address_info = StringField("Adresszusatz", default="")
    lat = FloatField("Lat", validators=[DataRequired()])
    lon = FloatField("Lon", validators=[DataRequired()])
    member1 = StringField("Teammitglied 3", validators=[DataRequired()])
    member2 = StringField("Teammitglied 3", validators=[DataRequired()])
    member3 = StringField("Teammitglied 3", validators=[DataRequired()])
    allergies = StringField("Allergien", default="")
    vegetarians = IntegerField("Vegetarier", validators={NumberRange(min=0, max=3)}, default=0)
    legal_accepted = BooleanField("Datenschutzbestimmungen", validators=[DataRequired()])
    want_information = BooleanField("Informationen", default=False)


class AdminLoginForm(FlaskForm):
    login = StringField("Login")
    password = PasswordField("Passwort")


class TeamEditForm(FlaskForm):
    name = StringField("Teamname", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Telefonnummer", validators=[DataRequired()])
    address = StringField("Adresse", validators=[DataRequired()])
    zipno = StringField("Postleitzahl", validators=[DataRequired()])
    address_info = StringField("Adresszusatz", default="")
    lat = FloatField("Lat", validators=[DataRequired()])
    lon = FloatField("Lon", validators=[DataRequired()])
    member1 = StringField("Teammitglied 3", validators=[DataRequired()])
    member2 = StringField("Teammitglied 3", validators=[DataRequired()])
    member3 = StringField("Teammitglied 3", validators=[DataRequired()])
    allergies = StringField("Allergien", default="")
    vegetarians = IntegerField("Vegetarier", validators={NumberRange(min=0, max=3)}, default=0)
    backup = BooleanField("Warteliste")


class ConfirmForm(FlaskForm):
    confirmed = BooleanField(u"Bestaetigen")
