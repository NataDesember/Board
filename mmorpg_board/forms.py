from smtplib import SMTPDataError

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.forms import ModelForm, CharField
from django.template.loader import render_to_string

from .models import Announce, Feedback

from django import forms

from allauth.account.forms import SignupForm, BaseSignupForm
from django.contrib.auth.models import Group


class AnnounceForm(ModelForm):
    request_user = None

    class Meta:
        model = Announce
        fields = ['author', 'title', 'text', 'category']

    def save(self):
        announce = super(AnnounceForm, self).save()
        return announce


class AnnounceUpdateForm(ModelForm):
    class Meta:
        model = Announce
        fields = ['title', 'text', 'category']


class BaseRegisterForm(SignupForm):
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = ["username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", ]

    def save(self, request):
        user = super(BaseRegisterForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)

        html_content = render_to_string(
            'user_registered.html',
            {
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
        )

        try:
            msg = EmailMultiAlternatives(
                subject=f'Registration',
                body='Thank you for registration',
                from_email='green-malahit@yandex.ru',
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")  # добавляем html
            msg.send()  # отсылаем
        except SMTPDataError:
            pass

        return user


class FeedbackForm(ModelForm):
    request_user = None

    class Meta:
        model = Feedback
        fields = ['user', 'announce', 'text']

        def __init__(self, *args, **kwargs):
            from django.forms.widgets import HiddenInput

            super(FeedbackForm, self).__init__(*args, **kwargs)
            self.fields['user'].widget = HiddenInput()
            self.fields['announce'].widget = HiddenInput()

    def save(self):
        feedback = super(FeedbackForm, self).save()

        user = feedback.announce.author

        html_content = render_to_string(
            'post_notified.html',
            {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'category': feedback.announce.category,
                'announce': feedback.announce,
                'feedback': feedback

            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Новый отклик на {{ feedback.announce.title }}',
            body=f'Здравствуй, {{ first_name }} {{ last_name }}. Получен новый отклик на ваше объявление. <br/>  {{ feedback.text }} <br/>',
            from_email='green-malahit@yandex.ru',
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        msg.send()  # отсылаем
        return feedback


class FeedbackUpdateForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ['text']
