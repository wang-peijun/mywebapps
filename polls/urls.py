from django.conf.urls import url
from .views import detail, index, vote, result, test, pub, search_question_list, \
    search_question_choices_list, preview, submit


# app_name = 'polls'
urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^pub/$', pub, name='pub'),
    url(r'^pub/question$', search_question_list),
    url(r'^pub/question_choices$', search_question_choices_list),
    url(r'^pub/preview', preview),
    url(r'^pub/submit/', submit),
    url(r'^(?P<poll_id>\d+)/$', detail, name='detail'),
    url(r'^(?P<poll_id>\d+)/vote/$', vote, name='vote'),
    url(r'^(?P<poll_id>\d+)/result/$', result, name='result'),
    url(r'^test/', test)
]

