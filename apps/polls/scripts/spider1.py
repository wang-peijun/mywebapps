import requests
import string
import random
from lxml import etree
import json
import time

# host = 'https://www.wjx.cn'
# url = 'https://www.wjx.cn/newwjx/mysojump/newselecttemplete.aspx'
# user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
# headers = {'user-agent': user_agent}
#
# r = requests.get(url, headers=headers)
# text = r.text
# # with open('text.html', encoding='utf-8') as f:
# #     text = f.read()
#
# html = etree.HTML(text)
# uls = html.xpath('//*[@id="ctl01_ContentPlaceHolder1_ulData1"]/*[@class="subject__listbox clearfix"]')
# urls = []
# for ul in uls:
#     urls.extend(ul.xpath('.//a[@href]/@href'))
#
# polls = []
# for u in urls:
#     poll = {}
#     u = host + u
#     res = requests.get(u, headers=headers)
#     text = res.text
#     # with open('test1.html', encoding='utf-8') as f:
#     #     text = f.read()
#     html = etree.HTML(text)
#     lis = html.xpath('//*[@id="ctl00_ContentPlaceHolder1_post_list"]/ul/li')
#     if not lis:
#         continue
#     li = random.choice(lis)
#     p = li.xpath('.//a[@href]/@href')
#     time.sleep(2)
#     if not p:
#         continue
#     u1 = host + p[0]
#     r2 = requests.get(u1, headers=headers)
#     text = r2.text
#     # with open('test2.html', encoding='utf-8') as f:
#     #     text = f.read()
#     html = etree.HTML(text)
#     title = html.xpath('//*[@id="htitle"]/text()')
#     poll['title'] = title[0].strip() if title else ''
#     des = html.xpath('//*[@class="topic__type-des"]/text()')
#     des = '\n'.join(des) if des else ''
#     poll['description'] = des.strip() or poll['title']
#     questions = []
#     qus = html.xpath('//*[@class="topic__type-body"]/fieldset')
#     for q in qus:
#         question = {}
#         q_title = q.xpath('./legend/text()')
#         if not q_title:
#             continue
#         q_title = q_title[0].strip().lstrip('0123456789 .'+string.ascii_letters)
#         # if not q_title.endswith(('?', '？', ':', '：')):
#         #     q_title += '？'
#         question['title'] = q_title
#
#         q_type = q.xpath('.//*[@class="topic__type-items"][1]//*[@class]/@class')
#         if not q_type:
#             continue
#         q_type = q_type[0][:-6]
#         question['type'] = q_type
#
#         choices = []
#         if q_type != 'textarea':
#             choices = q.xpath('.//*[@class="topic__type-items"]/label/text()')
#         question['choices'] = choices
#         questions.append(question)
#     poll['questions'] = questions
#     print(poll)
#     polls.append(poll)
#
#
# with open('polls.json', 'w') as f:
#     json.dump(polls, f)
#
#
from ..models import Poll, Question, Choice, PollQuestion, Vote
from django.contrib.auth.models import User
from apps.polls.utils import now_delta
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

owner = User.objects.first()
with open('./apps/polls/scripts/polls.json') as f:
    polls = json.load(f)
    for poll in polls:
        title = poll.get('title')
        desc = poll.get('description')
        questions = []
        for q in poll.get('questions'):
            if q.get('type') in ('radio', 'checkbox', 'textarea'):
                questions.append(q)
        if not questions:
            continue
        p = Poll(title=title, description=desc, owner=owner, end_date=now_delta(timedelta(days=random.randint(5, 30))))
        p.save()
        for i, question in enumerate(questions, 1):
            title = question.get('title')
            type_ = question.get('type')
            if type_ == 'radio':
                choice_type = 0
            elif type_ == 'checkbox':
                choice_type = 1
            else:
                choice_type = 2
            q, _ = Question.objects.get_or_create(content=title.lstrip('、'), choice_type=choice_type)
            try:
                pq = PollQuestion.objects.get(poll=p, question=q)
            except Exception as e:
                pq = PollQuestion(poll=p, question=q, index=i)
                pq.save()
            if type_ == 'radio' or (type_ == 'checkbox'):
                choices = question.get('choices')
                for j, choice in enumerate(choices or [], 1):
                    has_extra_data = False
                    if choice.startswith('其他') or choice.endswith('其他'):
                        has_extra_data = True
                    c, _ = Choice.objects.get_or_create(content=choice, has_extra_data=has_extra_data)
                    try:
                        vote = Vote.objects.get(poll_question=pq, choice=c)
                    except Exception as e:
                        vote = Vote(poll_question=pq, choice=c, index=j)
                        vote.save()
        print(p.title)

