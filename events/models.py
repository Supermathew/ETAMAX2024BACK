from django.db import models
# from django_markdown.models import MarkdownField
from martor.models import MartorField
# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _
from uuid import uuid4


class Club(models.Model):
    name = models.CharField(_("Club Name"), max_length=256)
    description = models.TextField(_("Club Description"))
  

    def __str__(self):
        return self.name
      
class Event(models.Model):

  DAYS = (
    (1, "One"),
    (2, "Two"),
    (3, "Three")
  )
  CATEGORIES = (
    ("C","Cultural"),
    ("T", "Technical"),
    ("S", "seminar "),
  )
  
  BRANCH = (
  ("Comp", "Computer"),
  ("IT", "IT"),
  ("EXTC", "EXTC"),
  ("Mech", "Mechanical"),
  ("Elec", "Electrical"),
  ("OTHER", "Other")
)
  

  event_code = models.CharField(_("Event Code"),max_length=36,default=uuid4, unique=True, primary_key=True)
  day = models.SmallIntegerField(_("Day"), choices=DAYS, blank=False)
  start = models.TimeField(_("Start Time"), max_length=5, blank=False)
  end = models.TimeField(_("End Time"), max_length=5, blank=False)
  title = models.CharField(_("Event Title"), max_length=256,blank=False)
  description = MartorField(_("Event Description"), blank=False)
  event_rules = models.TextField(_("Event Rules"), blank=False,default="null")
  is_featured = models.BooleanField("Is Featured", default=False)
  is_fcrit_only = models.BooleanField("Is Event only for FCRIT Students", default=False)
  whatsapp_link = models.URLField(_("Whatsapp Link"), blank=True, null=True)
  image = models.ImageField(_("Event Banner"), upload_to="uploads/")
  seats = models.IntegerField(_("Event Seats(0 at start)"),blank=False,default=0)
  image_googledrive = models.URLField(_("Image Google Drive"), blank=True, null=True)
  max_seats = models.IntegerField(_("Maximum Event Seats"),blank=False,default=0)
  category = models.CharField(_("Category"), choices=CATEGORIES, max_length=1, blank=False)
  is_seminar = models.BooleanField(_("Is Event a Seminar"), default=False, blank=False)
  is_seminar_department = models.BooleanField(_("Is Event a Seminar of Department"), default=False, blank=False)
  seminar_branch = models.CharField(_("Seminar Branch"), choices=BRANCH, max_length=125, blank=True)
  team_size = models.IntegerField(_("Team Size"), default=1)
  is_team_size_strict = models.BooleanField(_("Is Team Size Strict"), blank=False)
  entry_fee = models.IntegerField(_("Entry Fee"), blank=False, default=0)
  prize_money = models.TextField(_("Prize Money JSON"), blank=False, default=0)
  club = models.ForeignKey(Club, on_delete=models.CASCADE)



  def __str__(self) -> str:
    return f"{self.title}#{self.event_code}"
  


