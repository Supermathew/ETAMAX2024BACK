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


from events.models import Event
from .managers import UserManager

DEPARTMENTS = (
  ("Comp A", "Computer A"),
  ("Comp B", "Computer B"),
  ("IT", "IT"),
  ("EXTC", "EXTC"),
  ("Mech A", "Mechanical A"),
  ("Mech B", "Mechanical B"),
  ("Elec", "Electrical"),
  ("OTHER", "Other")
)

gender = (
  ("M", "Male"),
  ("F", "Female"),
  ("N", "Prefer Not to Say")
)
def make_roll_no() -> int:
  return random.randint(9000000, 10000000)

def make_password() -> str:
  return str(uuid4())[-8:]

class User(AbstractBaseUser, PermissionsMixin):

  roll_no = models.IntegerField(_("Roll Number"),unique=True, blank=False, primary_key=True)
  email = models.EmailField(_('email address'),unique=True, max_length=254)
  name = models.CharField(_('Name'), max_length=256,blank=True, null=True)
  avatar = models.CharField(_("Avatar Image"), max_length=256, blank=True ,null=True)
  department = models.CharField(_('Department'),max_length=10,blank=True, null=True, choices=DEPARTMENTS)
  semester = models.SmallIntegerField(_("Semester"),blank=True, null=True)
  college = models.CharField(_("College"), max_length=256, default="FCRIT, Vashi.")
  phone_no = models.CharField(_("Phone Number"),blank=True,  max_length=32)
  is_phone_no_verified = models.BooleanField(_("Is Phone Number Verified"), default=True)
  cart = models.TextField(_("Cart JSON (DONT FILL THIS)"), default="[]")
  is_from_fcrit = models.BooleanField(_("Is From FCRIT"), default=True)
  userpassword = models.TextField(blank=True, null=True)
  money_owed = models.DecimalField(_("Money Owed"),decimal_places=2,max_digits=10, default=0.00)
  has_filled_profile = models.BooleanField(_("Has Filled Profile"), default=True)
  criteria = models.TextField(_("Criteria JSON (DONT FILL THIS)"), default='{"C": 0, "T": 0, "S": 0}')
  daywise_criteria = models.TextField(_("daywise_Criteria JSON (DONT FILL THIS)"), default='{"1": 0, "2": 0, "3": 0}')
  email_send = models.BooleanField(_("Email Send"), default=False)
  is_staff = models.BooleanField(default=False)
  is_superuser = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)
  date_joined = models.DateTimeField(default=timezone.now)
  gender = models.CharField(_('Gender'),max_length=10,blank=True, null=True, choices=gender)


  USERNAME_FIELD = 'roll_no'
  REQUIRED_FIELDS = ['email',]

  objects = UserManager()

  def __str__(self) -> str:
      return f"{self.roll_no}#{self.email}"


class UserRequest(models.Model):
  email = models.EmailField(_('email address'),unique=True, max_length=254)
  name = models.CharField(_('Name'), max_length=256,blank=False)
  department = models.CharField(_('Department'),max_length=10,blank=False, choices=DEPARTMENTS)
  semester = models.SmallIntegerField(_("Semester"),blank=False)
  phone_no = models.CharField(_("Phone Number"),blank=False,  max_length=32)
  college = models.CharField(_("College"), max_length=256,blank=False)
  is_approved = models.BooleanField(_("Is Approved"), default=False)
  gender = models.CharField(_('Gender'),max_length=10,blank=True, null=True, choices=gender)


  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['email','name', 'department', 'semester', 'phone_no', 'college']

  def __str__(self) -> str:
      return f"{self.name}#{self.email}"


@receiver(post_save, sender=UserRequest)
def make_user_when_approved(sender, instance, created, **kwargs):
  print('yo works')
  print(created)
  print(instance.is_approved)
  if not created and instance.is_approved:
    print('in')
    if User.objects.filter(email=instance.email).exists():
      return

    u = [1]
    while len(u) > 0:
      new_roll_no = make_roll_no()
      u = User.objects.filter(roll_no=new_roll_no)

    try:
      pwd = make_password()
      user = User(
        roll_no=new_roll_no,
        email=instance.email,
        name=instance.name,
        department=instance.department,
        semester=instance.semester,
        college=instance.college,
        phone_no=instance.phone_no,
        is_phone_no_verified=True,
        has_filled_profile=True,
        is_from_fcrit=False,
      )
      user.set_password(pwd)
      print(user)
      user.save()
    except Exception as e:
      print(f"Error creating User: {instance.email}#{new_roll_no}")
      print(e)


class Participation(models.Model):
  part_id = models.CharField(_("Participation Id"), default=uuid4,max_length=36, unique=True, primary_key=True)
  team_name = models.CharField(_("Team Name"), max_length=256,blank=False)
  event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participations")
  captain_paid = models.BooleanField("captain paid", default=False)
  captain = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="captain", null=True, blank=True)
  members = models.ManyToManyField(User, related_name='participations')
  transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, related_name="participations", null=True, blank=True)
  is_verified = models.BooleanField(_("Is Verified"), default=False)

  def __str__(self) -> str:
    return f"{self.team_name}#{self.part_id}"

@receiver(pre_delete, sender=Participation)
def update_criteria_after_delete(sender, instance, using, **kwargs):
  def update_criteria(user, event):
    # criteria = json.loads(user.criteria)
    # criteria[event.category] -= 1
    # print(criteria, event.category)
    # user.criteria = json.dumps(criteria)
    criteria = json.loads(user.criteria)
    daywise_criteria = json.loads(user.daywise_criteria)
    print(event.category)
    print("mathewa laex hellloansfanfanfkj")
    print("daywise_Criteria",daywise_criteria)
    criteria[event.category] -= 1
    if event.day == 1:
        daywise_criteria["1"] -= 1
    elif event.day == 2:
        daywise_criteria["2"] -= 1
    elif event.day == 3:
        daywise_criteria["3"] -= 1
    user.daywise_criteria = json.dumps(daywise_criteria)
    print("mathewa laex hellloansfanfanfkj")
    print("daywise_Criteria",user.daywise_criteria)
    print("00event.dayunregister",event.day)
    user.criteria = json.dumps(criteria)
    user.save()


  members = instance.members.all()
  for m in members:
    update_criteria(m, instance.event)

@receiver(post_save, sender=Participation)
def update_criteria_after_save(sender, instance, created, **kwargs):

  if not created:
    if instance.is_verified:
      event = instance.event
      event.seats += 1
      event.save()

# @receiver(post_save, sender=Participation)
# def update_criteria_after_participation(sender, instance, created, **kwargs):
#   if created:
#     def update_criteria(user, event):
#       criteria = json.loads(user.criteria)
#       criteria[event.category] += 1
#       print(criteria, event.category)
#       user.criteria = json.dumps(criteria)
#       user.save()
#     print(instance.members)
#     print("mem", instance.members.first(), sender)
#     for m in instance.members.all():
#       update_criteria(m, instance.event)


class ExcelData(models.Model):
    excel_file = models.FileField(upload_to='excel_files/')
    upload_date = models.DateTimeField(auto_now_add=True)