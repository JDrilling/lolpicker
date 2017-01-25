from django.contrib import admin
from picker.models import Game, PickBanRound, Team, Champion

admin.site.register(Team)
admin.site.register(Game)
admin.site.register(PickBanRound)
admin.site.register(Champion)
