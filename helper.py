import re
from tables import User, PersonalProfile, Company, Job
from flask_login import current_user

def url_friendly(str):
    new_str = (re.sub("\W", "", str)).lower()
    return new_str

def load_user():
    user = User.query.filter_by(id=current_user.id).first()
    return user

def load_profile():
    existing_profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    return existing_profile

def load_company():
    existing_company = Company.query.filter_by(administrator_id=current_user.id).first()
    return existing_company

def load_jobs():
    existing_company = load_company()
    existing_jobs = Job.query.filter_by(company_id=existing_company.id).all()
    return existing_jobs

def get_categories(input):
    result=[]
    for item in input:
        if item != "csrf_token" and item != 'submitcategory' and item != 'searchfield':
            result.append(item)
    return result
