# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView

from .filters import AnnounceFilter, FeedbackFilter
from .models import Announce, Feedback
from .forms import AnnounceForm, BaseRegisterForm, AnnounceUpdateForm, FeedbackForm, FeedbackUpdateForm

from django.core.cache import cache

import logging
logger = logging.getLogger('mmorpg_game.mmorpg_board.views')


# Список статей
class AnnounceList(ListView):
    model = Announce
    ordering = '-time_in'
    template_name = 'mmorpg_board.html'
    context_object_name = 'page'
    paginate_by = 10
    form_class = AnnounceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = AnnounceFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)

    # Фильтры со страницами вместе не работали, или одно или другое
    # Где ошиблась с описанием - не нашла.
    #
    # Решила сделать как тут (нашла в гугле)
    # https://stackoverflow.com/questions/44048156/django-filter-use-paginations
    #
    # В итоге фильтры и paginator вызваны руками в нужном порядке
    # и подставлены в результат - страница с данными, объект страницы, и фильтр для формы
    #
    # Также использовала query_transform для формирования правильных URL для перехода
    # между страницами paginator по результатам фильтра (подсмотрела там же)
    def get(self, request, *args, **kwargs):
        sfilter = AnnounceFilter(request.GET, queryset=self.get_queryset())
        filtered_qs = sfilter.qs
        paginator = Paginator(filtered_qs, self.paginate_by)
        page = request.GET.get('page', 1)

        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except EmptyPage:
            result = paginator.page(paginator.num_pages)
            logger.error("Hello! I'm error in your app. Enjoy:)")

        return render(request, 'mmorpg_board.html', {
            'page': result,
            'page_obj': result,
            'filter': sfilter
        })


# Одна статья в деталях
class AnnounceDetailView(DetailView):
    template_name = 'mmorpg_board/post_detail.html'
    queryset = Announce.objects.all()

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'announce-{self.kwargs["pk"]}', None)

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'announce-{self.kwargs["pk"]}', obj)

        return obj

    def get(self, request, *args, **kwargs):
        announce = self.get_object(self.queryset)

        return render(request, self.template_name, {
            'announce': announce,
        })


# Создание новой статьи
class AnnounceCreateView(CreateView):
    template_name = 'mmorpg_board/post_create.html'
    form_class = AnnounceForm
    request_user = None
    success_url = '/board/'

    def post(self, request, *args, **kwargs):
        self.request_user = request.user
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request_user = self.request_user
        return form


# Редактирование статьи
class AnnounceUpdateView(UpdateView):
    template_name = 'mmorpg_board/post_update.html'
    form_class = AnnounceUpdateForm
    model = Announce
    success_url = '/board/'

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся
    # редактировать
    def get_object(self, **kwargs):
        sid = self.kwargs.get('pk')
        return Announce.objects.get(pk=sid)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.request_user = request.user
        return super().post(request, *args, **kwargs)


class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'mmorpg_board/post_create.html'


# Удаление статьи с запросом подтверждения
class AnnounceDeleteView(DeleteView):
    template_name = 'mmorpg_board/post_delete.html'
    queryset = Announce.objects.all()
    success_url = '/board/'


# class AnnounceIndexView(LoginRequiredMixin, AnnounceList):
#     template_name = 'mmorpg_board/index.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/mmorpg_board/'


class AddAnnounce(LoginRequiredMixin, AnnounceCreateView):
    pass


class ChangeAnnounce(LoginRequiredMixin, AnnounceUpdateView):
    pass


class DeleteAnnounce(LoginRequiredMixin, AnnounceDeleteView):
    pass


# @login_required


class FeedbackList(ListView):
    model = Feedback
    ordering = '-time_in'
    template_name = 'feedback.html'
    context_object_name = 'page'
    paginate_by = 10
    form_class = FeedbackForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = FeedbackFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)

    # Фильтры со страницами вместе не работали, или одно или другое
    # Где ошиблась с описанием - не нашла.
    #
    # Решила сделать как тут (нашла в гугле)
    # https://stackoverflow.com/questions/44048156/django-filter-use-paginations
    #
    # В итоге фильтры и paginator вызваны руками в нужном порядке
    # и подставлены в результат - страница с данными, объект страницы, и фильтр для формы
    #
    # Также использовала query_transform для формирования правильных URL для перехода
    # между страницами paginator по результатам фильтра (подсмотрела там же)
    def get(self, request, *args, **kwargs):
        my_articles = Announce.objects.filter(author=request.user)
        feeds = Feedback.objects.filter(announce__in=my_articles)

        sfilter = FeedbackFilter(request.GET, queryset=feeds)
        filtered_qs = sfilter.qs
        paginator = Paginator(filtered_qs, self.paginate_by)
        page = request.GET.get('page', 1)

        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except EmptyPage:
            result = paginator.page(paginator.num_pages)
            logger.error("Hello! I'm error in your app. Enjoy:)")

        return render(request, 'feedback.html', {
            'page': result,
            'page_obj': result,
            'filter': sfilter
        })


# Одна статья в деталях
class FeedbackDetailView(DetailView):
    template_name = 'feedback/feedback_detail.html'
    queryset = Feedback.objects.all()

    def get_object(self, *args: object, **kwargs: object) -> object:  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'feedback-{self.kwargs["pk"]}', None)

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'feedback-{self.kwargs["pk"]}', obj)

        return obj

    def get(self, request, *args, **kwargs):
        feedback = self.get_object(self.queryset)

        return render(request, self.template_name, {
            'feedback': feedback,
        })


# Создание новой статьи
class FeedbackCreateView(CreateView):
    template_name = 'feedback/feedback_create.html'
    form_class = FeedbackForm
    request_user = None
    announce = None

    def post(self, request, *args, **kwargs):
        self.request_user = request.user
        announce_id = request.POST['announce']
        self.announce = Announce.objects.get(pk=announce_id)
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request_user = self.request_user
        form.announce = self.announce
        return form


class FeedbackUpdateView(UpdateView):
    template_name = 'feedback/feedback_update.html'
    form_class = FeedbackUpdateForm
    model = Feedback
    success_url = '/board/feedback/'

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся
    # редактировать
    def get_object(self, **kwargs):
        sid = self.kwargs.get('pk')
        return Feedback.objects.get(pk=sid)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.request_user = request.user
        return super().post(request, *args, **kwargs)


# Удаление статьи с запросом подтверждения
class FeedbackDeleteView(DeleteView):
    template_name = 'feedback/feedback_delete.html'
    queryset = Feedback.objects.all()
    success_url = '/board/feedback/'


class FeedbackIndexView(LoginRequiredMixin, FeedbackList):
    template_name = 'feedback.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AddFeedback(LoginRequiredMixin, FeedbackCreateView):
    pass


class ChangeFeedback(LoginRequiredMixin, FeedbackUpdateView):
    pass


class DeleteFeedback(LoginRequiredMixin, FeedbackDeleteView):
    pass

