from django.db import models
from django.db.models import CharField, ManyToManyField, DateTimeField, ForeignKey, IntegerField, SmallIntegerField, BooleanField
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from apps.polls.utils import now_delta
from functools import partial
from django.urls import reverse


# Create your models here.


from .middleware import GlobalRequestMiddleware


class Poll(models.Model):
    title = CharField(max_length=128)
    pub_date = DateTimeField(default=timezone.now)
    end_date = DateTimeField(default=partial(now_delta, datetime.timedelta(days=7)))
    owner = ForeignKey(User, blank=True)         # 创建以后read only
    is_open = BooleanField(default=True, choices=((True, '公开结果'), (False, '不公开结果')))
    is_pub = BooleanField(default=False)
    description = CharField(max_length=500, null=True, blank=True)
    questions = ManyToManyField('Question', related_name='polls', through='PollQuestion')
    submit_num = IntegerField(default=0)

    def __str__(self):
        return 'poll %s' % self.title

    class Meta:
        ordering = ['-pub_date']

    def save(self, *args, **kwargs):
        request = GlobalRequestMiddleware.getRequest()
        if request:
            self.owner = request.user
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('polls:detail', args=(self.id,))


class Question(models.Model):
    choice_types = (
        (0, '单选'),
        (1, '多选'),
        (2, '回答')
    )
    content = CharField(max_length=128)
    choice_type = SmallIntegerField(choices=choice_types, default=1)

    def __str__(self):
        return '【%s】question %s' % (self.choice_types[self.choice_type][1], self.content)


class PollQuestion(models.Model):
    index = IntegerField(default=0)    # 排序
    poll = ForeignKey(Poll, on_delete=models.CASCADE, related_name='poll_questions')
    question = ForeignKey(Question, on_delete=models.CASCADE)
    choices = ManyToManyField('Choice', through='Vote')

    def __str__(self):
        return '{} {}'.format(self.poll, self.question)

    class Meta:
        unique_together = (('poll', 'question'),)


class Choice(models.Model):
    choices = (
        (False, '不需要用户输入'),
        (True, '还有其他未列出选项，请用户输入')
    )

    content = CharField(max_length=128)
    has_extra_data = BooleanField(choices=choices, default=False)   # 定义时

    def __str__(self):
        return 'choice {}'.format(self.content)


class Vote(models.Model):
    poll_question = ForeignKey(PollQuestion, on_delete=models.CASCADE, related_name='votes')
    choice = ForeignKey(Choice, on_delete=models.CASCADE)
    num = IntegerField(default=0)     # 计数
    users = ManyToManyField(User, related_name='user_votes', blank=True)
    index = IntegerField(default=0)      # 排序

    def __str__(self):
        return 'vote {} {}'.format(self.id, self.num)

    class Meta:
        unique_together = (('poll_question', 'choice'),)


class Answer(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    content = CharField(max_length=500)
    poll_question = ForeignKey(PollQuestion, on_delete=models.CASCADE, related_name='answers')

    def __str__(self):
        return 'answer {}'.format(self.content)


class ExtraData(models.Model):
    vote = ForeignKey(Vote, related_name='extra_data_list')
    content = CharField(max_length=128)



