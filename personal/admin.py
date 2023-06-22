from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Position)
admin.site.register(Area)
admin.site.register(AreaxPosicion)
admin.site.register(Functions)
admin.site.register(HiringProcess)
admin.site.register(EmployeeXHiringProcess)
admin.site.register(StageType)
admin.site.register(ProcessStage)
admin.site.register(JobOffer)
admin.site.register(TrainingType)
admin.site.register(TrainingLevel)
admin.site.register(TrainingxLevel)
admin.site.register(TrainingxAreaxPosition)

