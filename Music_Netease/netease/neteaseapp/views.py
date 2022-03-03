from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseServerError
from . import models
import random
import time
from .models import Question, Choice


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:5]


# 登录方法
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        # 如果登录成功绑定登录参数到cookie中 set_cookies
        name = request.POST.get('name')
        password = request.POST.get('password')
        # 查询用户是否在数据库中
        if models.Users.objects.filter(u_name=name).exists():
            user = models.Users.objects.get(u_name=name)
            if check_password(password, user.u_pass):
                ticket = ''
                for i in range(15):
                    s = 'abcdefghijklmnopqrstuvwxyz'
                    # 获取随机的字符串
                    ticket += random.choice(s)
                now_time = time.time()
                ticket = 'TK:' + ticket + str(now_time)
                # 绑定令牌到cookie里面,关于cookie的参数，均可在这里设置。
                response = HttpResponseRedirect('/neteaseapp/')
                response.set_cookie('name', name)
                response.set_cookie('ticket', ticket, max_age=10000)
                user.u_ticket = ticket
                user.save()
                print('登录成功！')
                return response
            else:
                return render(request, 'login.html', {'password': '用户密码错误，请仔细检查'})
        else:
            return render(request, 'login.html', {'name': '该用户不存在'})


def register(request):
    if request.method == 'GET':
        return render(request, 'neteaseapp/register.html')
    if request.method == 'POST':
        # 注册
        name = request.POST.get('name')
        if models.Users.objects.filter(u_name=name).exists():
            return render(request, 'neteaseapp/register.html', {'name': '该用户已存在'})
        else:
            password = request.POST.get('password')
            # 对密码加密
            password = make_password(password)
            models.Users.objects.create(u_name=name, u_pass=password)
            return HttpResponseRedirect('/neteaseapp/login')


def logout(request):
    if request.method == 'GET':
        response = HttpResponseRedirect('/neteaseapp/login')
        response.delete_cookie('ticket')
        return response


def index(request):  # 首页方法
    # if request.method == 'GET':
    #     ticket = request.COOKIES.get('ticket')
    #     if not ticket:
    #         return HttpResponseRedirect('/neteaseapp/login')
    #     if models.Users.objects.filter(u_ticket=ticket).exists():
    #         return render(request, 'neteaseapp/index.html')
    #     else:
    #         return HttpResponseRedirect('/neteaseapp/login')
    return render(request, 'index.html')


def test_index(request):  # 测试页方法
    return render(request, 'test.html')


# 以下为index页面的后台逻辑方法:
# @api_view(["GET"])  # 首页爬虫状态
def crawler_status(request):
    result_json = {}
    start_time = int(request.GET.get('start_time'))
    end_time = int(request.GET.get('end_time'))

    spider_status = models.status_record.objects.filter(start_time__range=(start_time, end_time)) \
        .values().order_by('-id')
    result_json['data'] = list(spider_status)[0]
    result_json['data']['id'] = len(list(spider_status))
    return JsonResponse(result_json)


# @api_view(['GET'])  # 首页种子列表采集信息
def crawler_seed(request):
    result_json = {}
    spider_seed = models.run_record.objects.all().values().order_by('-round_id')
    all_seed = models.run_record.objects.all().values().order_by('round_id')
    result_json['list'] = index_core.sort_seed(list(spider_seed))
    result_json['all'] = index_core.sort_all(list(all_seed))
    return JsonResponse(result_json)


# @api_view(['GET'])  # 首页爬虫统计 曲线图
def crawler_statistics(request):
    result_json = {}
    start_time = int(request.GET.get("start_time"))
    end_time = int(request.GET.get("end_time"))
    spider_statistics = models.run_record.objects.filter(start_time__range=(start_time, end_time)). \
        values().order_by('start_time')
    result_json['list'] = index_core.sort_all_time(list(spider_statistics))
    return JsonResponse(result_json)


# @api_view(['GET'])  # 首页爬虫占比统计 pie
def crawler_amount(request):
    start_time = int(request.GET.get("start_time"))
    end_time = int(request.GET.get("end_time"))
    top_num = int(request.GET.get("top_num"))  # top榜  eg：5、10....
    result_json = index_core.seed_site(start=start_time, end=end_time, top_num=top_num)
    return JsonResponse(result_json)


# @api_view(['GET'])  # 首页爬虫占比统计 table
def crawler_table(request):
    start_time = int(request.GET.get("start_time"))
    end_time = int(request.GET.get("end_time"))
    if request.GET.get('balance_time'):  # balance_time：环比时间 进入环比方法
        balance_time = request.GET.get('balance_time')
        result_json = index_core.seed_table(start=start_time, end=end_time, balance_time=balance_time)
    else:
        result_json = index_core.seed_table(start=start_time, end=end_time, balance_time=None)
    return JsonResponse(result_json)
