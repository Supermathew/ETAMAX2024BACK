from django.contrib import admin
from django.http.response import HttpResponse
from django.template.defaultfilters import slugify
import csv

from .models import User, UserRequest , Participation
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  list_filter = ('is_phone_no_verified', 'has_filled_profile', 'is_from_fcrit','email_send') #'money_owed')
  search_fields = ('roll_no', 'name', 'email', 'phone_no')
  list_display=['roll_no','email_send']
  actions = ['emailuser','export_as_csv',]

  @admin.action(description="Download Csv")
  def export_as_csv(self, request, queryset):
    model = queryset.model
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    writer = csv.writer(response)
    fields= None
    # Write headers to CSV file
    if fields:
        headers = fields
    else:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
    writer.writerow(headers)
    # Write data to CSV file
    for obj in queryset:
      row = []
      for field in headers:
          if field in headers:
              val = getattr(obj, field)
              if callable(val):
                  val = val()
              row.append(val)

      writer.writerow(row)
    # Return CSV file to browser as download
    return response
 

  @admin.action(description="Send Email To User")
  def emailuser(self, request, queryset):
        for user in queryset:
            password = user.password
            print(password)
            subject = "Your User Credentials ETAMAX 2024"
            message = format_html(
                "Dear {},<br><br>"
                "Here are your login credentials:<br>"
                "User ID: {}<br>"
                "Password: {}<br><br>"
                "You can log in <a href='{}'>here</a>.<br><br>"
                "Best regards,<br>Students Council",
                user.name,
                user.roll_no,
                user.userpassword,
                "etamax.fcrit.ac.in",  # Change this URL to the login page URL
            )
            from_email = "etamax@fcrit.ac.in"  # Change this to your email address
            recipient_list = [user.email]

            try:
               send_mail(subject, '', from_email, recipient_list, html_message=message)
               user.email_send = True
               user.save()
            except Exception as e:
                print(e)
            
        self.message_user(request, "Email sent successfully to selected users.")

@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
  search_fields = ('name', 'email', 'phone_no')
  list_filter = ('is_approved', 'department', 'semester')

  actions = ['approve_user_request']

  @admin.action(description='Approve user request')
  def approve_user_request(modeladmin, request, queryset):
    for user_request in queryset:
      user_request.is_approved = True
      user_request.save()

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
  search_fields = ('part_id', 'team_name', 'transaction__upi_transaction_id', 'transaction__transaction_id', 'members__name', 'members__roll_no', 'members__email', 'event__title')
  list_display = ['team_name', 'event','seats','day','category','amount','display_members','is_verified', 'transaction']
  list_filter = ('is_verified', 'event__title')
  actions = ['export_as_csv']
  
  def day(self, obj):
    return obj.event.day
  def seats(self, obj):
    return str(obj.event.seats)+"/"+str(obj.event.max_seats)
  def category(self, obj):
    return obj.event.category
  def amount(self, obj):
    return obj.event.entry_fee
  def display_members(self, obj):
    return ', '.join([str(member.roll_no) for member in obj.members.all()])
  display_members.short_description = 'Members'

  @admin.action(description="Download Csv")
  def export_as_csv(self, request, queryset):
    model = queryset.model
    qs = Participation.objects.prefetch_related(
        'members'
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    writer = csv.writer(response)
    writer.writerow(['timestamp', 'transaction_id', 'event', 'Team name','day', 'Members_name','Members_rollno','Members_phone_no', 'Verified','entry_fee'])
    for rule in qs:
      
        writer.writerow(["-" if rule.transaction is None else rule.transaction.timestamp,rule.transaction,rule.event.title, rule.team_name, rule.event.day
             ,','.join(str(c.name) for c in rule.members.all())
             ,','.join(str(c.roll_no) for c in rule.members.all())
             ,','.join(str(c.phone_no) for c in rule.members.all()),rule.is_verified,rule.event.entry_fee])
    return response
  
import json
import random
from uuid import uuid4
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from transactions.models import Transaction
from django.core.mail import EmailMessage


from events.models import Event
from .managers import UserManager
# admin.py
from django.contrib import admin, messages 
from .models import ExcelData
import pandas as pd 

def make_roll_no() -> int:
  return random.randint(9000000, 10000000)

def make_password() -> str:
    return str(uuid4())[-8:]

@admin.register(ExcelData)
class ExcelDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'upload_date')
    actions = ['create_users_from_excel','create_nonfcritusers_from_excel']
    # create_users_from_excel.short_description = "Create Users from Excel Entries"


    def create_users_from_excel(self, request, queryset):
        for excel_data in queryset:
            try:
                # Load the Excel file
                excel_df = pd.read_excel(excel_data.excel_file)

                # Iterate through the rows and create user objects
                # for _, row in excel_df.iterrows():
                #     username = row['username']
                #     email = row['email']
                #     password = row['password']  # You should handle password hashing properly

                #     User.objects.create_user(username=username, email=email, password=password)
                for _, row in excel_df.iterrows():
                        # User.objects.create(
                        #     email=row['Email Id'],
                        #     name=row['name'],
                        #     department=row['Department'],
                        #     semester=row['semester'],
                        #     phone_no=row['phone no'],
                        #     roll_no=row['Roll No']
                        # )
                        pwd = make_password()
                        print(pwd)
                        user = User(
                            roll_no=row['Roll No'],
                            email=row['Email ID'],
                            name=row['Name'],
                            department=row['Department'],
                            semester=row['Semester'],
                            phone_no=row['Phone No'],
                            gender = row['Gender'],
                            userpassword = pwd,
                            is_phone_no_verified=True,
                            has_filled_profile=True,
                            is_from_fcrit=True,
                        )
                        user.set_password(pwd)
                        print("mathew")
                        # user = User()
                        # user.name = row['Name']
                        # user.roll_no = row['Roll No']
                        # user.email = row['Email ID']
                        # user.department = row['Department']
                        # user.semester = row['Semester']
                        # user.phone_no = row['Phone No']
                        # user.set_password(pwd)
                        try:
                          user.save()
                        # can send email for login details here
                        # but sending throught mail merge in google sheeets
                        except Exception as e:
                            print(e)
                            roll_no = row['Roll No']  # Define the variables here
                            email = row['Email ID']
                            text_password = pwd
                            department = row['Department']
                            semester = row['Semester']

                            print(roll_no, email, text_password, department, semester)
                            print(user)
                self.message_user(request, f"Users created from {excel_data.excel_file.name}")
            except Exception as e:
                self.message_user(request, f"Error processing {excel_data.excel_file.name}: {str(e)}", level=messages.ERROR)
                
    def create_nonfcritusers_from_excel(self, request, queryset):
        for excel_data in queryset:
            try:
                # Load the Excel file
                excel_df = pd.read_excel(excel_data.excel_file)
                for _, row in excel_df.iterrows():
                      u = [1]
                      while len(u) > 0:
                        new_roll_no = make_roll_no()
                        u = User.objects.filter(roll_no=new_roll_no)
                      try:
                        pwd = make_password()
                        user = User(
                            roll_no=row['Roll No'],
                            email=row['Email ID'],
                            name=row['Name'],
                            department=row['Department'],
                            semester=row['Semester'],
                            phone_no=row['Phone No'],
                            gender = row['Gender'],
                            userpassword = pwd,
                            is_phone_no_verified=True,
                            has_filled_profile=True,
                            is_from_fcrit=False,
                        )
                        user.set_password(pwd)
                        print(user)
                        user.save()
                      except Exception as e:
                          print(e)
                          roll_no = row['Roll No']  # Define the variables here
                          email = row['Email ID']
                          text_password = pwd
                          department = row['Department']
                          semester = row['Semester']
                          print(roll_no, email, text_password, department, semester)
                          print(user)
                self.message_user(request, f"Users created from {excel_data.excel_file.name}")
            except Exception as e:
                self.message_user(request, f"Error processing {excel_data.excel_file.name}: {str(e)}", level=messages.ERROR)

    create_users_from_excel.short_description = "Create Users from Excel Entries"
    
    create_nonfcritusers_from_excel.short_description = "Create Non Fcrit Users from Excel Entries"