from django.urls import path

from apps.match.views import MatchCrud, MatchCreation, MatchJoin, MatchPlay, MatchLeave, MatchStatus

urlpatterns = [
    path('match/', MatchCreation.as_view()),
    path('match/<int:match_id>/', MatchCrud.as_view()),
    path('match/status/<int:match_id>/', MatchStatus.as_view()),
    path('match/join/<int:match_id>/', MatchJoin.as_view()),
    path('match/leave/<int:match_id>/', MatchLeave.as_view()),
    path('match/play/<int:match_id>/', MatchPlay.as_view()),
]
