from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView

from women.forms import AddPostForm, UploadFileForm, ContactForm
from women.models import Women, Category, TagPost, UploadFiles
from women.utils import DataMixin

# menu = [{'title': "О сайте", 'url_name': 'about'},
#         {'title': "Добавить статью", 'url_name': 'add_page'},
#         # {'title': "Редактировать статью", 'url_name': 'edit_page'},
#         {'title': "Обратная связь", 'url_name': 'contact'},
#         {'title': "Войти", 'url_name': 'login'}
# ]



cats_db = [
    {'id': 1, 'name': 'Актрисы'},
    {'id': 2, 'name': 'Певицы'},
    {'id': 3, 'name': 'Спортсменки'},
]

# def index(request):
#     posts = Women.published.all().select_related('cat')
#     data = {'title': 'Главная Страница',
#             'menu': menu,
#             'posts': posts,
#             'cat_selected': 0,
#             }
#     return render(request, 'women/index.html', data )


class WomenHome(DataMixin, ListView):
    # model = Women
    template_name = 'women/index.html'
    context_object_name = 'posts'
    title_page = 'Главная Страница'
    cat_selected = 0

    # extra_context = {
    #     'title': 'Главная Страница',
    #     'menu': menu,
    #     'posts': Women.published.all().select_related('cat'),
    #     'cat_selected': 0,
    # }
    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = 'Главная страница'
    #     context['menu'] = menu
        # context['posts'] = Women.published.all().select_related('cat')
        # context['cat_selected'] = int(self.request.GET.get('cat_id', 0))
        # return context
    def get_queryset(self):
        return Women.published.all().select_related('cat')



# def show_post(request, post_slug):
#     post = get_object_or_404(Women, slug=post_slug)
#     data = {
#         'title': post.title,
#         'menu': menu,
#         'post': post,
#         'cat_selected': 1,
#     }
#     return render(request, 'women/post.html', context=data)


class ShowPost(DataMixin, DetailView):
    model = Women
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['post'])
        # context['title'] = context['post']
        # context['menu'] = menu
        # return context

    def get_object(self, queryset=None):
        return get_object_or_404(Women, slug=self.kwargs[self.slug_url_kwarg], is_published=1)



def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


@login_required
def about(request):
    contact_list = Women.published.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'women/about.html', {'page_obj': page_obj, 'title': 'О сайте'})


# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             # print(form.cleaned_data)
#             # try:
#             #      Women.objects.create(**form.cleaned_data)
#             #      return redirect('home')
#             # except:
#             #      form.add_error(None, 'Ошибка добавления поста')
#             form.save()
#             return redirect('home')
#     else:
#         form = AddPostForm()
#     return render(request, 'women/addpage.html', {'menu': menu, 'title': 'Добавление статьи', 'form': form})


# class AddPage(View):
#     def get(self, request):
#         form = AddPostForm()
#         return render(request, 'women/addpage.html', {'menu': menu, 'title': 'Добавление статьи', 'form': form})
#
#     def post(self, request):
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#         return render(request, 'women/addpage.html', {'menu': menu, 'title': 'Добавление статьи', 'form': form})


# class AddPage(FormView):
#     form_class = AddPostForm
#     template_name = 'women/addpage.html'
#     success_url = reverse_lazy('home')
#     extra_context = {
#         'menu': menu,
#         'title': 'Добавление статьи',
#     }
#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)


class AddPage(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, CreateView):
    # model = Women
    form_class = AddPostForm
    # fields = '__all__'
    template_name = 'women/addpage.html'
    # success_url = reverse_lazy('home')
    title_page = 'Добавление статьи'
    # extra_context = {
    #     'menu': menu,
    #     'title': 'Добавление статьи',
    # }
    permission_required = 'women.add_women'

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)


class UpdatePage(PermissionRequiredMixin, DataMixin, UpdateView):
    model = Women
    fields = ['title', 'content', 'photo', 'is_published', 'cat']
    template_name = 'women/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование статьи'
    # extra_context = {
    #     'menu': menu,
    #     'title': 'Редактирование статьи',
    # }
    permission_required = 'women.change_women'


class ContactFormView(LoginRequiredMixin, DataMixin, FormView):
    form_class = ContactForm
    template_name = 'women/contact.html'
    success_url = reverse_lazy('home')
    title_page = "Обратная связь"

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


def login(request):
    return HttpResponse("Авторизация5")


# def show_category(request, cat_slug):
#     category = get_object_or_404(Category, slug=cat_slug)
#     posts = Women.published.filter(cat_id=category.pk).select_related('cat')
#     data = {
#         'title': f'Рубрика: {category.name}',
#         'menu': menu,
#         'posts': posts,
#         'cat_selected': category.pk,
#     }
#     return render(request, 'women/index.html', context=data)


class WomenCategory(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        return self.get_mixin_context(context,
                                      title='Категория - ' + cat.name,
                                      cat_selected=cat.id,
                                      )
        # context['title'] = 'Категория - ' + cat.name
        # context['menu'] = menu
        # context['cat_selected'] = cat.id
        # return context

    def get_queryset(self):
        return Women.published.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')


# def show_tag_postlist(request, tag_slug):
#     tag = get_object_or_404(TagPost, slug=tag_slug)
#     posts = tag.tags.filter(is_published=Women.Status.PUBLISHED).select_related('cat')
#     data = {
#         'title': f'Тег: {tag.tag}',
#         'menu': menu,
#         'posts': posts,
#         'cat_selected': None,
#     }
#     return render(request, 'women/index.html', context=data)

class TagPostList(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag)
        # context['title'] = 'Тег - ' + tag.tag
        # context['menu'] = menu
        # context['cat_selected'] = None
        # return context

    def get_queryset(self):
        return Women.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')