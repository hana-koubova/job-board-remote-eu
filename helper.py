import re
from tables import User, PersonalProfile, Company, Job, Applicant
from flask_login import current_user
from sqlalchemy import and_

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

def load_applicants():
    applicants = Applicant.query.filter_by(administrator_id=current_user).all()
    return applicants

def get_categories(input):
    result=[]
    for item in input:
        if item != "csrf_token" and item != 'submitcategory' and item != 'searchfield' and item != 'submitindustry':
            result.append(item)
    return result

def is_company_full(company):
    if company.url == '' or company.about == '' or company.contact == '' or company.address == '':
        print("You need to fill up some info")
        return False
    else:
        print(f"{company.name} has information full")
        return True
    
def is_profile_full(profile):
    if profile.f_name == '' or profile.l_name == '' or profile.role == '' or profile.about == '':
        print("User needs to finish profile")
        return False
    else:
        print("User has profile full")
        return True
    