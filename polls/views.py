from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpRequest, JsonResponse, HttpResponseRedirect
from django.views import generic
from .models import Poll, Question, Choice, Vote, Answer, PollQuestion, ExtraData
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.db.models import F
from django.contrib.sites import shortcuts
from django.utils import timezone
import json
from django_redis import get_redis_connection
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django import template
from django.contrib import messages
import polls.signals
from django.core.cache import cache
from django.views.decorators.http import require_http_methods

# redis连接池
con = get_redis_connection('default')

# Create your views here.


# class IndexView(generic.ListView):
#     model = Poll
#     template_name = 'polls/index.html'
#     context_object_name = 'polls'
#     paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
#     paginate_orphans = getattr(settings, 'BASE_PAGE_ORPHANS', 0)


def index(request: HttpRequest):
    key = request.get_full_path()
    res = cache.get(key)

    underway_page = request.GET.get('underway_page')
    finished_page = request.GET.get('finished_page')
    if underway_page:
        # use cache
        if res:
            print('use cache')
            return JsonResponse(res, safe=False)

        underway_polls = Poll.objects.filter(end_date__gt=timezone.now())
        paginator = Paginator(underway_polls, settings.BASE_PAGE_BY)

        try:
            underway_polls = paginator.page(underway_page)
        except PageNotAnInteger:
            underway_polls = paginator.page(1)
        except EmptyPage:
            underway_polls = paginator.page(paginator.num_pages)
        data = []
        for poll in underway_polls:
            data.append({'url': reverse('polls:detail', args=(poll.id,)), 'title': poll.title})

        cache.set(key, data, timeout=3600*24)
        return JsonResponse(data, safe=False)
    elif finished_page:
        # cache
        if res:
            print('use cache')
            return JsonResponse(res, safe=False)

        finished_polls = Poll.objects.filter(end_date__lte=timezone.now())
        paginator = Paginator(finished_polls, settings.BASE_PAGE_BY)

        try:
            finished_polls = paginator.page(finished_page)
        except PageNotAnInteger:
            finished_polls = paginator.page(1)
        except EmptyPage:
            finished_polls = paginator.page(paginator.num_pages)

        data = []
        for poll in finished_polls:
            data.append({'url': reverse('polls:result', args=(poll.id,)), 'title': poll.title})

        cache.set(key, data, timeout=3600*24)
        return JsonResponse(data, safe=False)
    else:
        if res:
            print('use cache')
            return render(request, 'jinja2/polls/index.html', res)
        underway_polls = Poll.objects.filter(end_date__gt=timezone.now())
        underway_polls_paginator = Paginator(underway_polls, settings.BASE_PAGE_BY)
        finished_polls = Poll.objects.filter(end_date__lte=timezone.now())
        finished_polls_paginator = Paginator(finished_polls, settings.BASE_PAGE_BY)
        first_underway_page_data = []  # 加入html
        for poll in underway_polls_paginator.page(1):
            first_underway_page_data.append({'url': reverse('polls:detail', args=(poll.id,)), 'title': poll.title})
        first_underway_page_data = json.dumps(first_underway_page_data)
        first_finished_page_data = []
        for poll in finished_polls_paginator.page(1):
            first_finished_page_data.append({'url': reverse('polls:result', args=(poll.id,)), 'title': poll.title})
        first_finished_page_data = json.dumps(first_finished_page_data)
        context = {'underway_polls': underway_polls_paginator.page(1),
                   'finished_polls': finished_polls_paginator.page(1),
                   'first_underway_page_data': first_underway_page_data,
                   'first_finished_page_data': first_finished_page_data}
        cache.set(key, context, timeout=3600*24)
        return render(request, 'jinja2/polls/index.html', context=context)


@login_required
def pub(request):
    questions = Question.objects.all()[:settings.BASE_PAGE_BY]
    choices = Choice.objects.all()[:settings.BASE_PAGE_BY]
    data = {}
    for q in questions:
        data.update({q.id: {'content': q.content, 'type': q.choice_type, 'index': 0}})
    questions_json = json.dumps(data)

    return render(request, 'jinja2/polls/pub.html', context={'question_list': questions,
                                                             'questions_json': questions_json,
                                                             'offset': settings.BASE_PAGE_BY})


def search_question_list(request):
    try:
        search = request.GET['search']
        if search:
            query_set = Question.objects.filter(content__contains=request.GET['search'])
        else:
            query_set = Question.objects.all()

        try:
            offset = int(request.GET['offset'])
        except KeyError:
            offset = 0

        questions = query_set[offset: offset + settings.BASE_PAGE_BY]

        if questions:
            data = {}
            for q in questions:
                data.update({q.id: {'content': q.content, 'type': q.choice_type, 'index': 0}})
            return JsonResponse({'questions': data, 'message': {'type': 'success', 'content': '请求成功'},
                                 'offset': offset + settings.BASE_PAGE_BY}, safe=False)
        else:
            return JsonResponse({'questions': {}, 'message': {'type': 'info', 'content': '没有跟多的数据'}})
    except KeyError:
        return JsonResponse({'questions': {}, 'message': {'type': 'error', 'content': '无效的请求'}}, safe=False)


def search_question_choices_list(request):
    try:
        search = request.GET['search']
        q_id = request.GET['q_id']
        if search:
            query_set = Choice.objects.filter(content__contains=search)
        else:
            if q_id:
                pq = PollQuestion.objects.filter(question__id=q_id).first()
                query_set = None
                if pq:
                    query_set = pq.choices.all()
                if not query_set:
                    query_set = Choice.objects.all()
            else:
                query_set = Choice.objects.all()

        try:
            offset = int(request.GET['offset'])
        except KeyError:
            offset = 0

        choices = query_set[offset: offset + settings.BASE_PAGE_BY]
        if choices:
            data = {}
            for c in choices:
                data.update({c.id: {'content': c.content, 'has_extra_data': 1 if c.has_extra_data else 0, 'index': 0}})
            return JsonResponse({'choices': data, 'message': {'type': 'success', 'content': '请求成功'},
                                 'offset': offset + settings.BASE_PAGE_BY}, safe=False)
        else:
            return JsonResponse({'message': {'type': 'info', 'content': '没有跟多的数据'}})
    except KeyError:
        return JsonResponse({'message': {'type': 'error', 'content': '无效的请求'}}, safe=False)


@require_http_methods(['GET', 'POST', 'DELETE'])
def detail(request: HttpRequest, poll_id):
    # key = request.path
    # 不能全部缓存，csrf_token会变化，jinja2片段缓存，env
    # html = con.get(key)
    # if html:
    #     return HttpResponse(html)
    if request.method == 'GET':
        vote_queryset = Vote.objects.select_related('choice').order_by('index')
        poll_questions_queryset = PollQuestion.objects.order_by('index').select_related('question').prefetch_related(Prefetch('votes', queryset=vote_queryset, to_attr='voteset'))
        poll = Poll.objects.prefetch_related(Prefetch('poll_questions',
                                                      queryset=poll_questions_queryset,
                                                      to_attr='pollquestions')).get(pk=poll_id)
        html = render_to_string('jinja2/polls/detail.html', {'poll': poll}, request=request)
        # con.set(key, html, ex=3600*24)
        return HttpResponse(html)
    elif request.method == 'POST':
        # 修改
        return HttpResponse('修改未实现')
    elif request.method == 'DELETE':
        # 删除
        poll = get_object_or_404(Poll, pk=poll_id)
        poll.delete()
        # pub数量减少，删除缓存
        cache.delete('/polls/')
        cache.delete_pattern('/polls/?*')
        return HttpResponse('删除成功')


def vote(request: HttpRequest, poll_id):
    post = request.POST
    print(post)
    poll = get_object_or_404(Poll, pk=poll_id)

    for k in post.keys():
        if k.startswith('csrf'):
            continue
        elif k.startswith('ex'):
            content = post.get(k)
            if content:
                _, vote_id = k.split(':')
                vote = get_object_or_404(Vote, pk=vote_id)
                extra_data = ExtraData(content=content, vote=vote)
                extra_data.save()
        elif k.startswith('pqq'):
            answer_content = post.get(k)
            if answer_content:
                _, pq_id = k.split(':')
                poll_question = get_object_or_404(PollQuestion, pk=pq_id)

                if request.user.is_authenticated:
                    answer = Answer(poll_question=poll_question, content=answer_content, user=request.user)
                else:
                    answer = Answer(poll_question=poll_question, content=answer_content)
                answer.save()
        elif k.startswith('pqc'):
            vote_id = post.get(k)
            vote = get_object_or_404(Vote, pk=vote_id)
            vote.num = F('num') + 1
            vote.save()
            if request.user.is_authenticated:
                vote.users.add(request.user)

    messages.add_message(request, messages.INFO, '谢谢参与')
    return HttpResponseRedirect(reverse('polls:result', args=(poll_id,)))

from django.views.decorators.cache import cache_page


def result(request, poll_id):
    vote_queryset = Vote.objects.select_related('choice').order_by('index')
    poll_questions_queryset = PollQuestion.objects.order_by('index').select_related('question').prefetch_related(Prefetch('votes', queryset=vote_queryset, to_attr='voteset'))
    poll = Poll.objects.prefetch_related(Prefetch('poll_questions',
                                                  queryset=poll_questions_queryset,
                                                  to_attr='pollquestions')).get(pk=poll_id)
    return render(request, 'jinja2/polls/result.html', {'poll': poll, 'ExtraData': ExtraData})


@login_required
def preview(request: HttpRequest):

    data = json.loads(request.body)
    poll = Poll()
    try:
        poll.title = data['title']
        poll.description = data['desc']
        poll.owner = request.user
        poll.pollquestions = []
        for k in data['questions']:
            if k.startswith('new'):
                question = Question()
                question.choice_type = data['questions'][k]['type']
                question.content = data['questions'][k]['content']

            else:
                question = get_object_or_404(Question, pk=k)
            poll_question = PollQuestion(poll=poll, question=question, index=data['questions'][k]['index'])
            poll.pollquestions.append(poll_question)
            poll_question.voteset = []
            if question.choice_type == 1 or question.choice_type == 0:
                for j in data['choices'][k]:
                    c = data['choices'][k][j]
                    if j.startswith('new'):
                        choice = Choice(content=c['content'], has_extra_data=bool(c['has_extra_data']))
                    else:
                        choice = get_object_or_404(Choice, pk=j)
                    vote = Vote(poll_question=poll_question, choice=choice, index=c['index'])
                    poll_question.voteset.append(vote)

            poll_question.voteset.sort(key=lambda x: x.index)

        poll.pollquestions.sort(key=lambda x: x.index)
        messages.add_message(request, messages.INFO, '预览成功')
        return JsonResponse({'type': 'success', 'html': render_to_string('jinja2/polls/preview.html', {'poll': poll}, request=request)}, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'type': 'error', 'info': '预览错误'})


@login_required
def submit(request):
    data = json.loads(request.body)
    poll = Poll()
    try:
        poll.title = data['title']
        poll.description = data['desc']
        poll.save()
        for k in data['questions']:
            if k.startswith('new'):
                question = Question()
                question.choice_type = data['questions'][k]['type']
                question.content = data['questions'][k]['content']
                question.save()
            else:
                question = get_object_or_404(Question, pk=k)
            poll_question = PollQuestion(poll=poll, question=question, index=data['questions'][k]['index'])
            poll_question.save()
            if question.choice_type == 1 or question.choice_type == 0:
                for j in data['choices'][k]:
                    c = data['choices'][k][j]
                    if j.startswith('new'):
                        choice = Choice(content=c['content'], has_extra_data=bool(c['has_extra_data']))
                        choice.save()
                    else:
                        choice = get_object_or_404(Choice, pk=j)
                    vote = Vote(poll_question=poll_question, choice=choice, index=c['index'])
                    vote.save()
        messages.add_message(request, messages.INFO, '提交成功')
        return JsonResponse({'type': 'success', 'redirect': reverse('polls:detail', args=(poll.id,))})
    except Exception as e:
        print(e)
        return JsonResponse({'type': 'error', 'info': '提交错误'})


import random
@login_required
def gen_data(request):
    choices = []
    for i in range(5):
        for j in range(5):
            choice = Choice(content='-选项'+str(i)+str(j), has_extra_data=random.choice([True, False]))
            choice.save()
            choices.append(choice)

    questions = []
    for i in range(5):
        for j in range(5):
            question = Question(content='问题-{}{}?'.format(i, j), choice_type=random.randint(0, 2))
            question.save()
            questions.append(question)

    poll_questions = []
    pq_index = 0
    for i in range(35):
        poll = Poll(title='调查-{}'.format(i), description='描述-{}'.format(i))

        if random.randint(0, 1):
            poll.end_date = timezone.now()
        poll.save()
        index = 1
        qs = random.sample(questions, random.randint(3, 5))
        for q in qs:
            poll_questions.append([])
            poll_question = PollQuestion(poll=poll, question=q, index=index)
            index += 1
            poll_question.save()
            poll_questions[pq_index].append(poll_question)
            vote_index = 1
            votes = []
            if poll_question.question.choice_type != 2:
                cs = random.sample(choices, random.randint(3, 5))
                for c in cs:
                    vote = Vote(poll_question=poll_question, choice=c, index=vote_index)
                    vote_index += 1
                    vote.save()
                    votes.append(vote)
            poll_questions[pq_index].append(votes)
            pq_index += 1


    answer_index = 1
    extra_data_index = 1
    for ij in range(10):
        for pq, votes in poll_questions:
            if pq.question.choice_type == 2:
                answer = Answer(poll_question=pq, content='回答-{}'.format(answer_index))
                answer.save()
                answer_index += 1
            elif pq.question.choice_type == 1:
                    for vote in random.sample(votes, random.randint(1, len(votes))):
                        vote.num += 1
                        if vote.choice.has_extra_data:
                            extra_data = ExtraData(vote=vote, content='其他-{}'.format(extra_data_index))
                            extra_data.save()
                            extra_data_index += 1
                        vote.save()
            else:
                vote = random.choice(votes)
                vote.num += 1
                if vote.choice.has_extra_data:
                    extra_data = ExtraData(vote=vote, content='其他-{}'.format(extra_data_index))
                    extra_data.save()
                    extra_data_index += 1
                vote.save()

    return HttpResponse('test')


