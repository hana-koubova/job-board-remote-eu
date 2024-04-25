from database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from flask_login import UserMixin
from sqlalchemy import Integer, String, ForeignKey, Boolean, DateTime
import datetime

class User1(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    company: Mapped[str] = mapped_column(String(100))

    #profile_data: Mapped[list["PersonalProfile"]] = relationship(back_populates="status", passive_deletes=True, cascade="delete-orphan")

    #company_data: Mapped[list["Company"]] = relationship(back_populates="status", passive_deletes=True, cascade="delete-orphan")

    #job_data: Mapped[list["Job"]] = relationship(back_populates="status", passive_deletes=True, cascade="delete-orphan")

    #applicant_data: Mapped[list["Applicant"]] = relationship(back_populates="status", passive_deletes=True, cascade="delete-orphan")

    def remove(self):
        db.session.delete(self)


class PersonalProfile(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User1.id), primary_key=True)
    f_name: Mapped[str] = mapped_column(String(100))
    l_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100))
    about: Mapped[str] = mapped_column(String(500))
    #status: Mapped["User1"] = relationship(back_populates="profile_data", passive_deletes=True)

class Company(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    name_slug: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(300))
    industry: Mapped[str] = mapped_column(String(100))
    about: Mapped[str] = mapped_column(String(3000))
    contact: Mapped[str] = mapped_column(String(100))
    num_of_jobs: Mapped[int] = mapped_column(Integer)
    num_of_hidden_jobs: Mapped[int] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String(100))
    administrator_id: Mapped[int] = mapped_column(Integer, ForeignKey(User1.id))
    has_logo: Mapped[bool] = mapped_column(Boolean())
    #status: Mapped["User1"] = relationship(back_populates="company_data", passive_deletes=True)

    def add_job(self):
        self.num_of_jobs += 1

    def delete_job(self):
        self.num_of_jobs -= 1

    def delete_archived_job(self):
        self.num_of_hidden_jobs -=1

    def archive_new_job(self):
        self.num_of_hidden_jobs += 1

    def archive_published_job(self):
        self.num_of_hidden_jobs += 1
        self.num_of_jobs -= 1

    def recover_job(self):
        self.num_of_hidden_jobs -= 1
        self.num_of_jobs += 1

class Job(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(100))
    salary: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[str] = mapped_column(String(100))
    job_type: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))
    skills: Mapped[str] = mapped_column(String(1000))
    level: Mapped[str] = mapped_column(String(100))
    job_info: Mapped[str] = mapped_column(String(2000))
    contact: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean())
    time_publish: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User1.id))
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey(Company.id))
    #status: Mapped["User1"] = relationship(back_populates="job_data")

    def recover_job(self):
        self.time_publish = datetime.datetime.now()


class Applicant(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    a_first_name: Mapped[str] = mapped_column(String(100))
    a_last_name: Mapped[str] = mapped_column(String(100))
    a_email: Mapped[str] = mapped_column(String(100))
    a_cv_link: Mapped[str] = mapped_column(String(200))
    a_comments: Mapped[str] = mapped_column(String(300))
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey(Job.id))
    administrator_id: Mapped[int] = mapped_column(Integer, ForeignKey(User1.id,))
    time_applied: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    #status: Mapped["User1"] = relationship(back_populates="applicant_data")
    