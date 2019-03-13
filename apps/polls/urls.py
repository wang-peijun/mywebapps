from django.conf.urls import url
from .views import detail, index, vote, result, gen_data, pub, search_question_list, \
    search_question_choices_list, preview, submit, mine, PollSearchView

# app_name = 'polls'
urlpatterns = [
    url(r'^$', index, name='index'),    # 返回问卷列表页
    url(r'^pub/$', pub, name='pub'),    # 发布问卷页
    url(r'^pub/question$', search_question_list),  # 搜索问题，ajax请求
    url(r'^pub/question_choices$', search_question_choices_list),  # 搜索选项， ajax请求
    url(r'^pub/preview', preview),   # 预览页
    url(r'^pub/submit/', submit),    # 提交要发布的文件
    url(r'^(?P<poll_id>\d+)/$', detail, name='detail'),   # 返回问卷
    url(r'^(?P<poll_id>\d+)/vote/$', vote, name='vote'),  # 完成问卷后，提交数据
    url(r'^(?P<poll_id>\d+)/result/$', result, name='result'),  # 展示结果
    url(r'^mine$', mine, name='mine'),
    url(r'^gen_data/', gen_data),  # 生成初始数据，测试用
    url(r'^search/$', PollSearchView(), name='search'),
]

