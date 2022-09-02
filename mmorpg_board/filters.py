from django_filters import FilterSet
from .models import Announce, Feedback


class AnnounceFilter(FilterSet):
    class Meta:
        model = Announce
        fields = {
            'title': ['icontains'],
            'time_in': ['gt'],
            'author': ['exact'],
            'category': ['exact']
        }


class FeedbackFilter(FilterSet):
    class Meta:
        model = Feedback
        fields = {
            'text': ['icontains'],
        }


