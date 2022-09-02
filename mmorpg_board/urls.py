from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import BaseRegisterView, DeleteAnnounce, ChangeAnnounce, AddAnnounce
from .views import AnnounceList
from .views import AnnounceDetailView, AnnounceCreateView, AnnounceUpdateView, AnnounceDeleteView
from .views import FeedbackIndexView
from .views import FeedbackDetailView, FeedbackCreateView, FeedbackUpdateView, FeedbackDeleteView
from .views import DeleteFeedback, ChangeFeedback, AddFeedback

from django.views.decorators.cache import cache_page


urlpatterns = [
    path('login/',
         LoginView.as_view(template_name='mmorpg_board/login.html'),
         name='login'),
    path('logout/',
         LogoutView.as_view(template_name='mmorpg_board/logout.html'),
         name='logout'),
    path('signup/',
         BaseRegisterView.as_view(template_name='mmorpg_board/signup.html'),
         name='signup'),
    path('', cache_page(1)(AnnounceList.as_view())),
    path('<int:pk>', cache_page(5)(AnnounceDetailView.as_view()), name='post_detail'),
    path('create/', AddAnnounce.as_view(), name='post_create'),
    path('create/<int:pk>', ChangeAnnounce.as_view(), name='post_update'),
    path('delete/<int:pk>', DeleteAnnounce.as_view(), name='post_delete'),

    path('feedback/', cache_page(1)(FeedbackIndexView.as_view())),
    path('feedback/<int:pk>', cache_page(5)(FeedbackDetailView.as_view()), name='feedback_detail'),
    path('feedback/create/<class>/', AddFeedback.as_view(), name='feedback_create'),
    path('feedback/update/<int:pk>', ChangeFeedback.as_view(), name='feedback_update'),
    path('feedback/delete/<int:pk>', DeleteFeedback.as_view(), name='feedback_delete'),
]
