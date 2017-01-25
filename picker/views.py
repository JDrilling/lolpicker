from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from picker.models import Game

class IndexView(TemplateView):
    templateName = "picker/index.html"

    def get(self, request):
        return render(request, self.templateName, {})

class GameView(DetailView):
    templateName = "picker/game.html"
    model = Game

    '''
    def get(self, request):
        return render(request, self.templateName, {})
    '''

    def get_context_data(self, **kwargs):
        conext = super(GameView, self).get_context_data(**kwargs)

        return context
