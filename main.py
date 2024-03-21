import uuid
import time
import datetime
import json
import os
import glob
import zipfile
import pandas as pd
from io import BytesIO

## Neon

import psycopg2
from sqlalchemy import create_engine


## Flask

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, session, jsonify, send_file, send_from_directory
import flask_excel as excel

## Login and security

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
#from flask_oauthlib.client import OAuth

## Databases

from database import db

## WTFORMS

from flask_wtf.csrf import CSRFProtect


## Others

from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField
from sqlalchemy import and_, select, or_, func, desc

## Modules

from helper import url_friendly, load_user, load_profile, load_company, load_jobs, load_applicants, get_categories, is_company_full, is_profile_full

## Tables and Forms

from tables import User1, PersonalProfile, Company, Job, Applicant
from forms import RegistrationForm, LoginForm, PersonalProfileForm, CompanyForm, DeleteForm, JobForm, SideCategoryToolbar, SearchForm, ApplyForm, SideIndustryToolbar

## Internal

from categories import company_industries_full, company_industries, all_categories, job_categories, job_types, job_levels, test_categories, two_word_categories, job_categories_full, job_categories_promo, job_promo_links, job_levels_full, job_types_full
from texts import toolpits, about_par

## App initiation

app = Flask(__name__)
ckeditor = CKEditor(app)

## Upload

UPLOAD_FOLDER = 'upload/cv'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1000 ## 1Mb

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## Bootsrap

bootstrap = Bootstrap5(app)
## To generate random key
#secret_key = uuid.uuid4().hex
#app.config.from_prefixed_env()
app.config['SECRET_KEY'] = "287286a1716e47b1a244016e3763fb22"

## CSFP protection
csrf = CSRFProtect(app)
csrf.init_app(app)

## CREATE DATABASE

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:4slSQ8XqNYxm@ep-sweet-mode-a2vbydq9.eu-central-1.aws.neon.tech/neondb?sslmode=require'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


## Configure logging manager

login_manager = LoginManager()
login_manager.init_app(app)

## Create a user_loader callback

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User1, user_id)

with app.app_context():
    db.create_all()

## Neon dat
#conn_str = "postgresql://neondb_owner:4slSQ8XqNYxm@ep-sweet-mode-a2vbydq9.eu-central-1.aws.neon.tech/neondb?sslmode=require"
#engine = create_engine(conn_str)


## Errors
    
@app.errorhandler(404)
def handle_404_error(err):
    return render_template('404.html')

@app.errorhandler(Exception)
def handle_exception(err):
    # pass through HTTP errors
    if isinstance(err, HTTPException):
        return err

    # now you're handling non-HTTP exceptions only
    return render_template("500.html",
                           err=err), 500


## Routing
#@app.route('/', methods=['GET', 'POST'])
#def home_old():
#    return 'Hello World'

@app.route('/', methods=['GET', 'POST'])
def home():
    print('HELLO')
    five_recent_jobs = Job.query.order_by(Job.time_publish).all()[:5]
    print(len(five_recent_jobs))
    form = SearchForm()

    if request.method == 'POST':
        search_keyword = request.form['job-title']
        print(search_keyword)
        return redirect(url_for('board', search=search_keyword))
    return render_template("index.html",
                           form=form,
                           jobs=five_recent_jobs,
                           job_categories=job_categories_promo,
                           links=job_promo_links,
                           logged_in = current_user.is_authenticated)

ITEMS = list(range(1, 101))

@app.route('/pagination', methods=['GET', 'POST'])
def pagination():
    page = request.args.get('page', 1, type=int)
    items_per_page = 20
    total_pages = (len(ITEMS) + items_per_page - 1) // items_per_page
    total_pages_list = list(range(1, total_pages+1))
    start = (page - 1) * items_per_page
    end = start + items_per_page

    items_on_page = ITEMS[start:end]
    return render_template('pagination.html',
                           items = ITEMS,
                           page = page,
                           items_on_page = items_on_page,
                           total_pages = total_pages,
                           total_pages_list = total_pages_list,
                           logged_in = current_user.is_authenticated)


@app.route('/board', methods=['GET', 'POST'])
def board():
    search = request.args.getlist('search')
    category = request.args.getlist('category')
    page = request.args.get('page', 1, type=int)
    dict_query = request.args.to_dict(flat=False)
    print('URL PARAMS: ', category)
    print('SEARCH PARAMS: ', search)
    print('CAT LEN: ', len(category))
    print('SEARCH LEN: ', len(search))
    print('URL DICT: ', dict_query)
    category_form = SideCategoryToolbar()


    filter_conditions_cat=[]
    filter_conditions_typ=[]
    filter_conditions_lev=[]

    if len(category) == 0 and len(search) == 0:
        print('NO PARAMS')
        jobs_intersection = Job.query.order_by(desc(Job.time_publish)).all()
    else:
        # Exsiting category
        if len(category) > 0:
            for q in category:
                if q in job_categories:
                    print("JOB CATEGORY DETECTED")
                    filter_condition_cat = func.lower(func.replace(func.replace(func.replace(Job.category, ' ', ''), '/', ''), '-', '')) == q
                    filter_conditions_cat.append(filter_condition_cat)
                if q in job_types:
                    print("JOB TYPE DETECTED")
                    filter_condition_typ = func.lower(func.replace(func.replace(func.replace(Job.job_type, ' ', ''), '/', ''), '-', '')) == q
                    filter_conditions_typ.append(filter_condition_typ)
                if q in job_levels:
                    print("JOB LEVEL DETECTED")
                    filter_condition_lev = func.lower(func.replace(func.replace(func.replace(Job.level, ' ', ''), '/', ''), '-', '')) == q
                    filter_conditions_lev.append(filter_condition_lev)
            jobs = Job.query.filter(or_(*filter_conditions_cat)).order_by(desc(Job.time_publish)).all()
            types = Job.query.filter(or_(*filter_conditions_typ)).order_by(desc(Job.time_publish)).all()
            levels = Job.query.filter(or_(*filter_conditions_lev)).order_by(desc(Job.time_publish)).all()
            
            # finding intersection based on IDs
            job_ids = {job.id for job in jobs}
            type_ids = {job.id for job in types}
            level_ids = {job.id for job in levels}

            common_category_ids = job_ids.intersection(type_ids, level_ids)

            jobs_intersection = Job.query.filter(Job.id.in_(common_category_ids)).order_by(desc(Job.time_publish)).all()
        
        # Existing search
        if len(search) > 0:
            print("SEARCH DETECTED")
            
            search_filtered = Job.query.order_by(
                (desc(Job.time_publish))).filter(or_(
                Job.role.like(f"%{search[0]}%"),
                Job.job_info.like(f"%{search[0]}%"),
                Job.skills.like(f"%{search[0]}%"),
                Job.category.like(f"%{search[0]}%")
                )).all()
            
            jobs_intersection = search_filtered

        # Both category and search
        if len(search) > 0 and len(category) > 0:
            search_ids = {job.id for job in search_filtered}
            common_all_ids = common_category_ids.intersection(search_ids)

            jobs_intersection = Job.query.filter(Job.id.in_(common_all_ids)).order_by(desc(Job.time_publish)).all()

    print('JOBS LEN: ', len(jobs_intersection))
    jobs_len = len(jobs_intersection)

    #Pagination
    items_per_page = 5
    total_pages = (len(jobs_intersection) + items_per_page - 1) // items_per_page
    total_pages_list = list(range(1, total_pages+1))
    start = (page - 1) * items_per_page
    end = start + items_per_page

    items_on_page = jobs_intersection[start:end]


    if request.method == 'POST':
            filters_by_user = get_categories(request.form)
            #search_by_user = request.form.get('searchfield')
            search_by_user = request.form['searchfield']
            print('POST:', filters_by_user, search_by_user)
            if search_by_user == '':
                print('POST ONLY CAT')
                return redirect(url_for('board', category=filters_by_user, page=page))
            if len(filters_by_user) == 0:
                print('POST ONLY SEARCH')
                return redirect(url_for('board', search=search_by_user, page=page))
            if search_by_user != '' and len(filters_by_user) > 0:
                print('POST CAT AND SEARCH')
                return redirect(url_for('board', category=filters_by_user, search=search_by_user, page=page))

    return render_template("board.html",
                            url_query=category,
                            search_query=search,
                            jobs=jobs_intersection,
                            jobs_len=jobs_len,
                            category_form=category_form,
                            categories=all_categories,
                            job_categories=job_categories,
                            categories_full=job_categories_full,
                            job_levels=job_levels,
                            job_types=job_types,
                            
                            page = page,
                            items_on_page = items_on_page,
                            total_pages = total_pages,
                            total_pages_list = total_pages_list,

                            logged_in = current_user.is_authenticated)


@app.route('/board_js', methods=['GET', 'POST'])
def board_js():
    jobs_intersection = Job.query.order_by(desc(Job.time_publish)).all()
    filter_conditions_cat=[]
    filter_conditions_typ=[]
    filter_conditions_lev=[]

    #try:
    if request.method == 'POST':
            ## recieving Ajax
            data = request.get_json('filters_dict')
            filters_to_apply = []
            for key, value in data.items():
                if value == True:
                    filters_to_apply.append(key)
            print(filters_to_apply)

            if filters_to_apply:
            
                for filter in filters_to_apply:
                    if filter in job_categories:
                        print("JOB CATEGORY DETECTED")
                        filter_condition = func.lower(func.replace(func.replace(func.replace(Job.category, ' ', ''), '/', ''), '-', '')) == filter
                        filter_conditions_cat.append(filter_condition)
                        print('LENGHT: ', len(filter_conditions_cat))
                    if filter in job_types:
                        print("JOB TYPE DETECTED")
                        filter_condition = func.lower(func.replace(func.replace(func.replace(Job.job_type, ' ', ''), '/', ''), '-', '')) == filter
                        filter_conditions_typ.append(filter_condition)
                    if filter in job_levels:
                        print("JOB LEVEL DETECTED")
                        filter_condition = func.lower(func.replace(func.replace(func.replace(Job.level, ' ', ''), '/', ''), '-', '')) == filter
                        filter_conditions_lev.append(filter_condition)

                jobs = Job.query.order_by(desc(Job.time_publish)).filter(or_(*filter_conditions_cat)).all()
                types = Job.query.order_by(desc(Job.job_type)).filter(or_(*filter_conditions_typ)).all()
                levels = Job.query.order_by(desc(Job.level)).filter(or_(*filter_conditions_lev)).all()
                jobs_intersection = set(jobs) & set(levels) & set(types)
                
    if request.method == 'POST':
        print("POST")
        jobs_intersection = Job.query.all()

    print("The End")
    return render_template("archived/board_js.html",
                            jobs=jobs_intersection,
                            categories=all_categories,
                            job_categories=job_categories,
                            categories_full=job_categories_full,
                            job_levels=job_levels,
                            job_types=job_types,
                            logged_in = current_user.is_authenticated)


#@app.route('/ajax', methods=['GET', 'POST'])
def ajax():
        if request.method == 'POST':
            data = request.json.get('data')
            result = sum(data)
            return jsonify({'result': result})
    #return render_template('min_ajax.html')

@app.route('/ajax', methods=['GET', 'POST'])
def ajax_route():
    return ajax()


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get("query") # here query will be the search inputs name
    search_match = Job.query.filter(Job.title.like("%"+query+"%")).all()
    return #render_template("search.html", query=query, allVideos=allVideos)


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    post_job_form = JobForm()
    company=load_company()
    profile=load_profile()
    company_full = is_company_full(company)
    profile_full = is_profile_full(profile)
    toolpits_to_send = toolpits['post_job']
    if post_job_form.validate_on_submit() and request.method == 'POST':
        existing_company = Company.query.filter_by(administrator_id=current_user.id).first()

        # Publish job or keep it hidden
        publish = False
        if bool(request.form['active'] == 'Active (Publish right away)'):
            publish = True

        new_job = Job(role=request.form['role'],
                    salary = request.form['salary'],
                    start_date = request.form['start_date'],
                    job_type = request.form['job_type'],
                    category = request.form['category'],
                    skills = request.form['skills'],
                    level = request.form['level'],
                    job_info = request.form['job_info'],
                    contact = request.form['contact'],
                    active = publish,
                    time_publish = datetime.datetime.now(),
                    user_id = current_user.id,
                    company_id = existing_company.id)
        db.session.add(new_job)
        #print(type(new_job.job_type))
        # only add job if in active status
        if publish == True:
            existing_company.add_job()

        else:
            existing_company.archive_new_job()
        db.session.commit()
        #return redirect(url_for('profile'))
        return redirect(url_for('success_message', message="Hey, this is success Yay!"))
    return render_template("post_job.html",
                           company=company,
                           company_full=company_full,
                           profile_full=profile_full,
                           form=post_job_form,
                           toolpits=toolpits_to_send,
                           logged_in = current_user.is_authenticated)

@app.route('/success/<string:message>')
def success_message(message):
    return render_template('success_message.html',
                           message=message), {"Refresh": "3; url=/profile"}

@app.route('/about')
def about():
    return render_template("about.html",
                           about_par=about_par,
                           logged_in = current_user.is_authenticated)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit() and request.method == 'POST':
            # Check if email exists
            email = request.form['email']
            exists = User1.query.filter_by(email=email).first()

            if exists != None:
                error = 'This Email already exists in our database.'

            if exists == None:
                hash_and_salted_password = generate_password_hash(
                    request.form.get('password'),
                    method='pbkdf2:sha256',
                    salt_length=8
                )
                new_user = User1(email=request.form['email'],
                    password=hash_and_salted_password,
                    company=request.form['company'])
            
                db.session.add(new_user)
                db.session.commit()

                # Log in and authenticate user after adding details to database
                login_user(new_user)
            
                return redirect(url_for('register_step2', logged_in = current_user.is_authenticated))
    return render_template("register.html",
                           error=error,
                           form=registration_form,
                           logged_in = current_user.is_authenticated)

@app.route('/register_step2', methods=['GET', 'POST'])
@login_required
def register_step2():
    # Create a company in the dat

    new_company = Company(name=current_user.company,
                        name_slug=url_friendly(current_user.company),
                        url='',
                        about='',
                        contact='',
                        address='',
                        num_of_jobs=0,
                        num_of_hidden_jobs=0,
                        administrator_id=current_user.id)
    db.session.add(new_company)
    db.session.commit()
    return redirect((url_for('register_step3',
                             logged_in = current_user.is_authenticated)))

@app.route('/register_step3', methods=['GET', 'POST'])
@login_required
def register_step3():
    new_person_profile = PersonalProfile(user_id=current_user.id,
                        f_name='',
                        l_name='',
                        role='',
                        about='')
    db.session.add(new_person_profile)
    db.session.commit()
    return redirect(url_for('profile',
                            logged_in = current_user.is_authenticated))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    login_form = LoginForm()
    if login_form.validate_on_submit() and request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
     
        # Find user by email
        result = db.session.execute(db.select(User1).where(User1.email == email))
        user = result.scalar()

        # Check password hash
        try:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('profile'))
            else:
                 error = 'Wrong password'
        except AttributeError:
            error = 'Email is not registered in database'
    return render_template('login.html',
                           form=login_form,
                           error=error,
                           logged_in = current_user.is_authenticated)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    existing_profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    existing_company = Company.query.filter_by(administrator_id=current_user.id).first()
    existing_jobs = Job.query.filter_by(company_id=existing_company.id).all()
    applicants = Applicant.query.filter_by(administrator_id=current_user.id).all()
    num_applicants = len(applicants)
    

    company_full = is_company_full(existing_company)
    profile_full = is_profile_full(existing_profile)
    print(company_full, profile_full)

    job = Job.query.filter_by(company_id=existing_company.id).first()
    return render_template('profile/profile.html',
                           num_applicants=num_applicants,
                           profile_full=profile_full,
                           company_full=company_full,
                           existing_profile=existing_profile,
                           comp=existing_company,
                           jobs=existing_jobs,
                           logged_in = current_user.is_authenticated)

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    existing_profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('profile/user.html',
                           existing_profile=existing_profile,
                           logged_in = current_user.is_authenticated)


@app.route('/profile/edit/user', methods=['GET', 'POST'])
@login_required
def edit_user():
        existing_profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
        personal_profile_form = PersonalProfileForm()
             
        if personal_profile_form.validate_on_submit() and request.method == 'POST':
            f_name_edited = request.form['f_name']
            l_name_edited = request.form['l_name']
            role_edited = request.form['role']
            about_edited = request.form['about']

            existing_profile.f_name = f_name_edited
            existing_profile.l_name = l_name_edited
            existing_profile.role = role_edited
            existing_profile.about = about_edited
            db.session.commit()
            return redirect(url_for('user'))
        return render_template('profile/edit_user.html',
                               form=personal_profile_form,
                               existing_profile=existing_profile,
                               logged_in = current_user.is_authenticated)
    
@app.route('/profile/company')
@login_required
def company_p():
    company = load_company()
    return render_template('profile/company_p.html',
                           company=company,
                           logged_in = current_user.is_authenticated)

@app.route('/profile/setting')
@login_required
def setting():
    return render_template('profile/setting.html',
                           logged_in = current_user.is_authenticated)

@app.route('/prifile/edit/company', methods=['GET', 'POST'])
@login_required
def edit_company():
        existing_company = Company.query.filter_by(administrator_id=current_user.id).first()
        company_form = CompanyForm()
        print(existing_company.industry)
        if company_form.validate_on_submit() and request.method == 'POST':
            existing_company.name = request.form['name']
            existing_company.name_slug = url_friendly(request.form['name'])
            existing_company.url = request.form['url']
            existing_company.industry = request.form['industry']
            existing_company.contact = request.form['contact']
            existing_company.address = request.form['address']
            existing_company.about = request.form['about']
            current_user.company = request.form['name']
            db.session.commit()
            return redirect(url_for('company_p'))

        return render_template('profile/edit_company.html',
                               form=company_form,
                               existing_company=existing_company,
                               industries=company_industries_full,
                               current_user=current_user,
                               logged_in = current_user.is_authenticated)

@app.route('/profile/job_listings', methods=['GET', 'POST'])
@login_required
def job_listings():
    company = load_company()
    profile = load_profile()
    jobs = load_jobs()
    jobs_order = Job.query.filter_by(company_id=company.id).order_by(desc(Job.active)).order_by(desc(Job.time_publish)).all()
    #if request.method == 'POST':
    #    print("POST TOGGLE")
    return render_template('profile/job_listings.html',
                           company=company,
                           profile=profile,
                           jobs=jobs_order,
                           logged_in = current_user.is_authenticated)

@app.route('/profile/applicants', methods=['GET', 'POST'])
@login_required
def applicants():
    company = load_company()
    # Ordered by first active/archived, then by time published
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(desc(Job.active)).order_by(desc(Job.time_publish)).all()
    jobs_applicants = {}
    for job in jobs:
        jobs_applicants[job.id] = len(Applicant.query.filter_by(job_id=job.id).all())
    print(jobs_applicants)
    return render_template('profile/applicants.html',
                           jobs_applicants=jobs_applicants,
                           company=company,
                           jobs=jobs,
                           logged_in = current_user.is_authenticated)


@app.route('/profile/applicants/<int:job_id>', methods=['GET', 'POST'])
@login_required
def applicants_list(job_id):
    job = Job.query.filter_by(id=job_id).first()
    applicants = Applicant.query.filter_by(job_id=job.id).all()

    order = request.args.get('order', None)

    if order == 'alph':
        applicants = Applicant.query.filter_by(job_id=job.id).order_by(Applicant.a_last_name).all()
    if order == 'time':
        applicants = Applicant.query.filter_by(job_id=job.id).order_by(Applicant.time_applied).all()
    num_applicants = len(applicants)
    return render_template('profile/applicants_list.html',
                           order=order,
                           job=job,
                           applicants=applicants,
                           num_applicants=num_applicants,
                           logged_in = current_user.is_authenticated)

@app.route('/profile/applicants/<int:job_id>order', methods=['GET', 'POST'])
@login_required
def order_alph(job_id):
    return redirect(url_for('applicants_list', job_id=job_id, order='alph'))

@app.route('/profile/applicants/<int:job_id>time', methods=['GET', 'POST'])
@login_required
def order_time(job_id):
    return redirect(url_for('applicants_list', job_id=job_id, order='time'))


@app.route('/profile/view_cv/<fileurl>', methods=['GET', 'POST'])
@login_required
def view_cv(fileurl):
    filename = f"{fileurl}.pdf"
    filepath = f"upload/cv/{filename}"
    return send_file(filepath, mimetype='application/pdf')

@app.route('/profile/download_cv/<fileurl>', methods=['GET', 'POST'])
@login_required
def download_cv(fileurl):
    filename = f"{fileurl}.pdf"
    filepath = f"upload/cv/{filename}"
    return send_file(filepath, as_attachment=True)

@app.route('/profile/download_all_cvs/<int:job_id>', methods=['GET', 'POST'])
@login_required
def download_all_cvs(job_id):
    cv_directory = f"upload/cv/"
    pattern = cv_directory + f"{job_id}*.pdf"
    cv_files = glob.glob(pattern)

    # Create temporal zip file
    zip_file_path=f'temporal_files/all_{job_id}_csv.zip'
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        for cv_file in cv_files:
            zip_file.write(cv_file, os.path.basename(cv_file))

    response = send_file(zip_file_path, as_attachment=True)
    # Remove zip file
    os.remove(zip_file_path)
    return response


@app.route('/profile/download_excel/<job_id>', methods=['GET', 'POST'])
@login_required
def download_excel(job_id):
    applicants = Applicant.query.filter_by(job_id=job_id).all()
    print(len(applicants))

    df = pd.DataFrame([{
        'First Name': applicant.a_first_name,
        'Last Name': applicant.a_last_name,
        'Email': applicant.a_email,
        'Personal Comment': applicant.a_comments,
        'Time Applied: ': applicant.time_applied.strftime('%d-%m-%Y')
    } for applicant in applicants])


    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    
    response = send_file(excel_buffer, as_attachment=True, download_name="applicants.xlsx")
    excel_buffer.close()
    return response


@app.route('/profile/manage_jobs', methods=['GET', 'POST'])
@login_required
def manage_jobs():
    existing_profile = load_profile()
    existing_company = load_company()
    jobs = load_jobs()
    existing_jobs = Job.query.filter_by(company_id=existing_company.id).order_by(desc(Job.active)).all()
    return render_template('manage_jobs.html',
                           existing_profile=existing_profile,
                           comp=existing_company,
                           jobs=existing_jobs,
                           logged_in = current_user.is_authenticated)

@app.route('/profile/manage_jobs/delete/<int:job_id>')
@login_required
def delete_job(job_id):
    existing_company = load_company()
    job_to_delete = Job.query.filter_by(id=job_id).first()
    is_active = bool(job_to_delete.active)
    db.session.delete(job_to_delete)
    if is_active:
        existing_company.delete_job()
    elif is_active == False:
        existing_company.delete_archived_job()
    db.session.commit()
    return redirect(url_for('job_listings'))

@app.route('/profile/manage_jobs/hide/<int:job_id>')
@login_required
def hide_job(job_id):
    existing_company = load_company()
    job_to_hide = Job.query.filter_by(id=job_id).first()
    job_to_hide.active = False
    existing_company.archive_published_job()
    db.session.commit()
    return redirect(url_for('job_listings'))

@app.route('/profile/manage_jobs/activate/<int:job_id>')
@login_required
def activate_job(job_id):
    existing_company = load_company()
    job_to_activate = Job.query.filter_by(id=job_id).first()
    job_to_activate.active = True
    job_to_activate.time_publish = datetime.datetime.now()
    existing_company.recover_job()
    db.session.commit()
    return redirect(url_for('job_listings'))

@app.route('/profile/manage_jobs/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job_to_edit = Job.query.filter_by(id=job_id).first()
    job_edit_form = JobForm()
    if job_edit_form.validate_on_submit() and request.method == 'POST':
        job_to_edit.role =request.form['role']
        job_to_edit.salary= request.form['salary']
        job_to_edit.start_date = request.form['start_date']
        job_to_edit.job_type = request.form['job_type']
        job_to_edit.category = request.form['category']
        job_to_edit.skills = request.form['skills']
        job_to_edit.level = request.form['level']
        job_to_edit.job_info = request.form['job_info']
        job_to_edit.contact = request.form['contact']
        db.session.commit()
        return redirect(url_for('job_listings'))
    return render_template('edit_job.html',
                           form=job_edit_form,
                           job=job_to_edit,
                           levels=job_levels_full,
                           categories=job_categories_full,
                           job_types=job_types_full,
                           logged_in = current_user.is_authenticated)


@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    delete_form = DeleteForm()
    if delete_form.validate_on_submit() and request.method == "POST":
        user_to_delete = User1.query.filter_by(id=current_user.id).first()
        db.session.delete(user_to_delete)
        # relevant company to delete
        if bool(Company.query.filter_by(administrator_id=current_user.id).first()):
            company_to_delete = Company.query.filter_by(administrator_id=current_user.id).first()
            db.session.delete(company_to_delete)
        # relevant profile to delete
        if bool(PersonalProfile.query.filter_by(user_id=current_user.id).first()):
            profile_to_delete = PersonalProfile.query.filter_by(user_id=current_user.id).first()
            db.session.delete(profile_to_delete)
        db.session.commit()
        logout_user()
        return redirect(url_for('home'))
    return render_template('profile/delete_account.html',
                           form=delete_form,
                           logged_in = current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/companies', methods=['GET', 'POST'])
def companies():
    search = request.args.getlist('search')
    industry = request.args.getlist('industry')

    filter_form = SideIndustryToolbar()

    filter_conditions_ind = []
    active_jobs_only = False

    # Companies with Full Information
    companies_full_info = Company.query.filter(and_(
        Company.url != '',
        Company.about != '',
        Company.contact != '',
        Company.address != ''
    )).all()
    companies_full_info_ids = {company.id for company in companies_full_info}

    if len(industry) == 0 and len(search) == 0:
        print('NO PARAMS')
        companies_intersection = Company.query.order_by(Company.name).filter(and_(
            Company.url != '',
            Company.about != '',
            Company.contact != '',
            Company.address != ''
        )).all()
    else:
        # Existing industry
        if len(industry) > 0:
            for ind in industry:
                print('INDUSTRY')
                print(ind)
                if ind == 'activejobs':
                    print('ACTIVE JOBS FILTER')
                    active_jobs_only = True
                if ind != 'activejobs':
                    filter_condition_ind = func.lower(func.replace(func.replace(func.replace(Company.industry, ' ', ''), '/', ''), '-', '')) == ind
                    filter_conditions_ind.append(filter_condition_ind)

            companies_industry = Company.query.filter(or_(*filter_conditions_ind)).order_by(Company.name).all()
            companies_ids = {company.id for company in companies_industry}
            common_industry_ids = companies_ids
            companies_intersection = companies_industry
            
            
            if active_jobs_only == True:
                companies_active_jobs = Company.query.filter(Company.num_of_jobs > 0).order_by(desc(Company.num_of_jobs)).all()
                comp_active_ids = {company.id for company in companies_active_jobs}
                common_industry_ids = companies_ids.intersection(comp_active_ids, companies_full_info_ids)
                companies_intersection = Company.query.filter(Company.id.in_(common_industry_ids)).order_by(desc(Company.num_of_jobs)).all()

        # Existing Seach
        if len(search) > 0:
            search_filtered = Company.query.filter(or_(
                Company.name.like(f"%{search[0]}%"),
                Company.about.like(f"%{search[0]}%"),
                Company.contact.like(f"%{search[0]}%"),
                Company.address.like(f"%{search[0]}%"),
                Company.industry.like(f"%{search[0]}%"),
            )).all()
            search_ids = {company.id for company in search_filtered}.intersection(companies_full_info_ids)
            companies_intersection = Company.query.filter(Company.id.in_(search_ids)).all()
        
        # Existing both industry and search
        if len(search) > 0 and len(industry) > 0:
            
            common_all_ids = common_industry_ids.intersection(search_ids)
            companies_intersection = Company.query.filter(Company.id.in_(common_all_ids)).all()

    companies_len = len(companies_intersection)

    

    ## ADD PAGINATION

    if request.method == 'POST':
        print('POST')
        filters_by_user = get_categories(request.form)
        search_by_user = request.form['searchfield']
        print(filters_by_user)
        if search_by_user == '':
            print('NO SEARCH')
            return redirect(url_for('companies', industry=filters_by_user))
        if len(filters_by_user) == 0:
            print('NO FILTERS')
            return redirect(url_for('companies', search=search_by_user))
        if search_by_user != '' and len(filters_by_user) > 0:
            print('FILTERS AND SEARCH')
            return redirect(url_for('companies', industry=filters_by_user, search=search_by_user))
        
    return render_template('companies.html',
                           companies_len=companies_len,
                           url_query=industry,
                           search_query=search,
                           form=filter_form,
                           industries = company_industries,
                           companies=companies_intersection,
                           logged_in = current_user.is_authenticated)



@app.route('/company/<int:comp_id>/<name>')
def company(comp_id, name):
    company = Company.query.filter_by(id=comp_id).first()
    company_jobs = Job.query.filter_by(company_id=company.id).where(Job.active==True).all()
    return render_template('company.html',
                           company=company,
                           company_jobs=company_jobs,
                           logged_in = current_user.is_authenticated)

@app.route('/company/<int:comp_id>/<name>/job/<int:job_id>')
def job(comp_id, name, job_id):
    company = Company.query.filter_by(id=comp_id).first()
    company_jobs = Job.query.filter_by(company_id=company.id).all()
    job = Job.query.filter_by(id=job_id).first()
    print(job.time_publish)
    return render_template('job.html',
                           company=company,
                           job=job,
                           logged_in = current_user.is_authenticated)

@app.route('/job/<int:job_id>')
def job_clean(job_id):
    job = Job.query.filter_by(id=job_id).first()
    company = Company.query.filter_by(id=job.company_id).first()
    return render_template('job.html',
                           job=job,
                           company=company,
                           logged_in = current_user.is_authenticated)

@app.route('/job/<int:job_id>/apply', methods=['GET', 'POST'])
def apply(job_id):
    job_id=job_id
    apply_form = ApplyForm()
    
    job = Job.query.filter_by(id=job_id).first()
    company = Company.query.filter_by(id=job.company_id).first()

    if request.method == 'POST' and apply_form.validate_on_submit():
        print('POST')
        applicant_number = str(uuid.uuid1())
        #cv_link_str = f"{job_id}_{company.id}_{company.administrator_id}_{applicant_number}"

        new_applicant = Applicant(
            a_first_name = request.form['a_first_name'],
            a_last_name = request.form['a_last_name'],
            a_email = request.form['a_email'],
            a_cv_link = f"{job_id}_{company.id}_{company.administrator_id}_{((request.form['a_email']).replace('@', '_')).replace('.', '_')}_{applicant_number}",
            a_comments = request.form['a_comments'],
            job_id = job_id,
            administrator_id = company.administrator_id,
            time_applied = datetime.datetime.now()
        )

        #CV file name: jobId_companyId_administratorId_email_gmail_com_specialCode.pdf

        db.session.add(new_applicant)
        db.session.commit()

        file = request.files['a_cv']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{company.id}_{company.administrator_id}_{((request.form['a_email']).replace('@', '_')).replace('.', '_')}_{applicant_number}.pdf"))

        return redirect(url_for('apply_success', job_id=job_id))

    return render_template('apply.html',
                            job_id=job_id,
                            form=apply_form,
                            job=job,
                            company=company,
                            logged_in = current_user.is_authenticated)

@app.route('/job/<int:job_id>/apply/success', methods=['GET', 'POST'])
def apply_success(job_id):
    job = Job.query.filter_by(id=job_id).first()
    company = Company.query.filter_by(id=job.company_id).first()
    
    return render_template('apply_success.html',
                           company=company,
                           logged_in = current_user.is_authenticated), {"Refresh": "3; url=/board"}


if __name__ == "__main__":
    app.run(debug=True)