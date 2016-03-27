# coding=utf-8
from django.shortcuts import render, redirect

# Create your views here.
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query


def index(request):
    # request.session.set_test_cookie()
    context_dict = {}
    category_list = Category.objects.order_by('-likes')[:]
    context_dict['categories'] = category_list
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    # cookie = request.COOKIES
    # print cookie
    # session = request.session
    # print session
    # print type(session)
    # print dir(session)

    # visits = int(request.COOKIES.get('visits', 1))
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], '%Y-%m-%d %H:%M:%S')
        if (datetime.now() - last_visit_time).seconds > 0:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits
    response = render(request, 'rango/index.html', context_dict)
    # context_dict['visits'] = visits
    # reset_last_visit_time = False
    # response = render(request, 'rango/index.html', context_dict)
    # if 'last_visit' in request.COOKIES:
    #     last_visit = request.COOKIES['last_visit']
    #     last_visit_time = datetime.strptime(last_visit[:-7], '%Y-%m-%d %H:%M:%S')
    #     if (datetime.now() - last_visit_time).seconds > 0:
    #         visits += 1
    #         reset_last_visit_time = True
    # else:
    #     reset_last_visit_time = True
    #     context_dict['visits'] = visits
    #     response = render(request, 'rango/index.html', context_dict)
    # if reset_last_visit_time:
    #     response.set_cookie('last_visit', datetime.now())
    #     response.set_cookie('visits', visits)

    return response


def about(request):
    return render(request, 'rango/about.html', {})
    # return HttpResponse('Rango says: Here is the about page. <a href="/rango/">Index</a>')


def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
        # context_dict['category_name_url'] = category_name_slug
    except Category.DoesNotExist:
        pass
    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # try:
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
            # except Exception as e:
            #     print e
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()
    context_dict = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # if request.session.test_cookie_worked():
    #     print '>>>> TEST COOKIE WORKED!'
    #     request.session.delete_test_cookie()
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            # if 'picture' in request.FILES:
            #     profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    content_dict = {'user_form': user_form, 'profile_form': profile_form,
                    'registered': registered}
    return render(request, 'rango/register.html', content_dict)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # 和对应模板文件中input的name属性名相同
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                msg = '登录成功,现在跳转'
                return HttpResponseRedirect('/rango/')
                # return index(request)
            else:
                msg = '你的账户被禁'
                return HttpResponse('Your Rango account is disabled.')
        else:
            msg = '用户名或密码错误'
            print 'Invalid login details: {0}, {1}'.format(username, password)
            return HttpResponse('Invalid login details supplied.')
    else:
        msg = '请输入用户名或密码'
        return render(request, 'rango/login.html', {'msg': msg})


@login_required
def restricted(request):
    return HttpResponse('Since you"re logged in, you can see this text!')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')


def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)

def suggest_category(request):
    pass