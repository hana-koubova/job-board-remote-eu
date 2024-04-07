from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, BooleanField, Form, IntegerField, SelectField, TextAreaField, HiddenField, RadioField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_ckeditor import CKEditor, CKEditorField

from categories import job_categories, job_types, company_industries_full, job_levels, job_categories_full, job_types_full, job_levels_full

class RegistrationForm(FlaskForm):
    #email = StringField(u'Email', validators=[DataRequired(), Email(message="Email format not valid")])
    email = StringField(u'Email', validators=[DataRequired()])
    password = PasswordField(u'Password', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField(u'Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password', message='Passwords must match')])
    company = StringField(u"Company / Organisation", validators=[DataRequired()])
    submit = SubmitField(u"Register")

class LoginForm(FlaskForm):
    #email = StringField(label='Email', validators=[DataRequired(), Email(message="Email format not valid")])
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Login")

class PersonalProfileForm(FlaskForm):
    f_name = StringField(label='First Name', validators=[Length(max=100)])
    l_name = StringField(label='Last Name', validators=[Length(max=100)])
    role = StringField(label='Role in your Company',validators=[Length(max=100)])
    about = StringField(label='About', validators=[Length(max=500)])
    submit = SubmitField(label='Submit Information')

class CompanyForm(FlaskForm):
    name = StringField(u"Company Name", validators=[Length(max=100)])
    url = StringField(u"Company URL", validators=[Length(max=300)])
    industry = SelectField(u"Industry", validators=[DataRequired()], choices=company_industries_full, coerce=str)
    contact = StringField(u"Contact", validators=[Length(max=100)])
    address = StringField(u"Address", validators=[Length(max=100)])
    about = CKEditorField(u"About", validators=[Length(max=3000)])
    submit = SubmitField(label='Submit Information')

class DeleteForm(FlaskForm):
    reason = StringField(u"Why do you go?", validators=[Length(max=100)])
    submit = SubmitField(label='Delete Account')
     

#class EditProfile(FlaskForm):
#    company = StringField(u"Company / Organisation", validators=[DataRequired()])
#    submit = SubmitField(label="Save")

class JobForm(FlaskForm):
    role = StringField(u"Role / Title", validators=[DataRequired(), Length(max=100)])
    salary = IntegerField(u"Salary", validators=[DataRequired()])
    start_date = StringField(u"Start date", validators=[DataRequired(), Length(max=100)])
    job_type = SelectField(u"Type of job", validators=[DataRequired()], choices=job_types_full)
    category = SelectField(u"Category", validators=[DataRequired()], choices=job_categories_full)
    skills = StringField(u"Skills", validators=[DataRequired(), Length(max=1000)])
    level = SelectField(u"Level", validators=[DataRequired()], choices=job_levels_full)
    job_info = CKEditorField(u"Job Description", validators=[DataRequired(), Length(max=2000)])
    contact = StringField(u"Contact", validators=[DataRequired(), Length(max=100)])
    active = RadioField(u"Active", choices=['Active (Publish right away)', 'Hidden (Will publish later)'], default='Active (Publish right away)', validators=[DataRequired()])
    submit = SubmitField(label="Save Job")

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[Length(0, 5000), DataRequired()])
    submit = SubmitField('Create a Post')

class SideToolbar(FlaskForm):
    analyst = BooleanField(u"Analyst")
    developer = BooleanField(u"Developer")
    hr = BooleanField(u"HR")
    other = BooleanField(u"Other")
    submit = SubmitField('Submit')


class SideCategoryToolbar(FlaskForm):
    analyst = BooleanField(u"Analyst")
    backenddeveloper = BooleanField(u"Backend Developer")
    businessdeveloper = BooleanField(u"Business Development")
    customerservice = BooleanField(u"Customer Service")
    datascience = BooleanField(u"Data Science")
    design = BooleanField(u"Design")
    devops = BooleanField(u"DevOps")
    softwareengineer = BooleanField(u"Software Engineer")
    finance = BooleanField(u"Finance")
    frontenddeveloper = BooleanField(u"Frontend Developer")
    fullstackdeveloper = BooleanField(u"Full-stack Developer")
    hr = BooleanField(u"HR")
    legal = BooleanField(u"Legal")
    marketing = BooleanField(u"Marketing")
    mobiledeveloper = BooleanField(u"Mobile Developer")
    productmanager = BooleanField(u"Product Manager")
    projectmanager = BooleanField(u"Project Manager")
    qa = BooleanField(u"QA")
    sales = BooleanField(u"Sales")
    uxui = BooleanField(u"UX / UI")
    other = BooleanField(u"Other")

    entrylevel = BooleanField(u"Entry Level")
    medium = BooleanField(u"Medium")
    mediumsenior = BooleanField(u"Medium-Senior")
    senior = BooleanField(u"Senior")

    fulltime = BooleanField(u"Full-Time")
    parttime = BooleanField(u"Part-Time")
    intership = BooleanField(u"Intership")
    freelance = BooleanField(u"Freelance")

    searchfield = StringField(u"Search Keyword")

    submitcategory = SubmitField('Submit')

class SideIndustryToolbar(FlaskForm):
    advertising = BooleanField(u"Advertising")
    agriculture = BooleanField(u"Agriculture")
    blockchain = BooleanField(u"Blockchain")
    comsumergoods = BooleanField(u"Comsumer Goods")
    education = BooleanField(u"Education")
    energygreentech = BooleanField(u"Energy / Greentech")
    fashionliving = BooleanField(u"Fashion / Living")
    fintech = BooleanField(u"Fintech")
    food = BooleanField(u"Food")
    gaming = BooleanField(u"Gaming")
    healthcare = BooleanField(u"Healthcare")
    hospitality = BooleanField(u"Hospitality")
    it = BooleanField(u"IT")
    legal = BooleanField(u"Legal")
    marketing = BooleanField(u"Marketing")
    transport = BooleanField(u"Transport")
    ecommerce = BooleanField(u"eCommerce")
    entertainment = BooleanField(u"Entertainment")
    recruitment = BooleanField(u"Recruitment")
    retail = BooleanField(u"Retail")
    robotics = BooleanField(u"Robotics")
    saas = BooleanField(u"SaaS")
    science = BooleanField(u"Science")
    service = BooleanField(u"Service")
    tourism = BooleanField(u"Tourism")
    other  = BooleanField(u"Other")

    activejobs = BooleanField(u"With Open Positions")

    searchfield = StringField(u"Search Keyword")

    submitindustry = SubmitField('Submit')




class SideLevelForm(FlaskForm):
    entrylevel = BooleanField(u"Entry Level")
    medium = BooleanField(u"Medium")
    mediumsenior = BooleanField(u"Medium-Senior")
    senior = BooleanField(u"Senior")
    submitlevel = SubmitField('Submit')

class SideTypeJobForm(FlaskForm):
    fulltime = BooleanField(u"Full-Time")
    parttime = BooleanField(u"Part-Time")
    intership = BooleanField(u"Intership")
    freelance = BooleanField(u"Freelance")
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    search = StringField(validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Search')

class ApplyForm(FlaskForm):
    a_first_name = StringField(u"First Name", validators=[DataRequired()])
    a_last_name = StringField(u"Last Name", validators=[DataRequired()])
    a_email = StringField(u"Email", validators=[DataRequired()])
    a_cv = FileField(u"Upload File", validators=[DataRequired()])
    a_comments = TextAreaField(u"First Name")
    agree = BooleanField(u"Blah", validators=[DataRequired()])
    submit = SubmitField('Submit Application')