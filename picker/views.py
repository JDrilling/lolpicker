from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.base import View
from django.db.models import F

from picker.models import Game, Champion, PickBanRound
from picker.forms import GameForm
from picker.utils import createNewTenBanGame


class IndexView(TemplateView):
    template_name = "picker/index.html"


class GameView(SingleObjectMixin, View):
    template_name = "picker/game_detail.html"
    model = Game

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = {'game': self.object}
        context['champions'] = Champion.objects.all().order_by("name")

        return render(request, self.template_name, context)
'''
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            responseData = {'error': "Please log in!"}
            return JsonResponse(responseData, status=403)

        self.object = self.get_object()
        postData = request.POST

        if 'id' not in postData:
            responseData = {'error': "No champion selected!"}
            return JsonResponse(responseData, status=400)

        lolID = postData['id']

        pbrs = PickBanRound.objects.filter(game=self.object)

        # Are there any Pick/Ban rounds for this game?
        if len(pbrs) == 0:
            responseData = {'error': "Couldn't find pick and ban metadata."}
            return JsonResponse(responseData, status=500)

        # Are all the Pick/Ban rounds completed?
        roundNumber = self.object.currentRound
        if roundNumber >= len(pbrs):
            responseData = {'error': "All rounds have been completed!"}
            return JsonResponse(responseData, status=400)

        # Not all rounds are completed, but this round wasn't found
        currentRound = pbrs.get(roundNumber=roundNumber)
        if currentRound is None:
            responseData = {'error': "Unexpected round!"}
            return JsonResponse(responseData, status=500)

        # Make sure it's the captain making the picks and bans
        if currentRound.side == PickBanRound.BLUE:
            if self.object.blueTeam.captain != request.user:
                responseData = {'error': "You are not the captian of this team!"}
                return JsonResponse(responseData, status=403)
        elif currentRound.side == PickBanRound.RED:
            if self.object.redTeam.captain != request.user:
                responseData = {'error': "You are not the captian of this team!"}
                return JsonResponse(responseData, status=403)


        championSelected = Champion.objects.get(lolID=lolID)
        championsUsed = [r.champion for r in pbrs]

        # Was the champion already picked or banned?
        if championSelected in championsUsed:
            responseData = {'error': "Champion was already picked or banned!"}
            return JsonResponse(responseData, status=400)

        # add champion
        currentRound.champion = championSelected
        currentRound.save()

        # signal next round
        self.object.currentRound = F('currentRound') + 1
        self.object.save()

        done = (roundNumber + 1) >= len(pbrs)

        responseData = {'success': "Champion picked or banned.",
                        'done': done}

        return JsonResponse(responseData)
'''

class NewGameView(FormView):
    template_name = "picker/game_form.html"
    form_class = GameForm
    model = Game

    def form_valid(self, form):
        redTeam = form.cleaned_data['redTeam']
        blueTeam = form.cleaned_data['blueTeam']

        newGame = Game(redTeam=redTeam, blueTeam=blueTeam)
        newGame.save()

        try:
            createNewTenBanGame(newGame)
        except:
            newGame.delete()
            redirect("new-game-view")


        return redirect("game-view", pk=newGame.pk)
