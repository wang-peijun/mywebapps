from django.contrib import admin
from .models import Poll, Question, Choice, PollQuestion, Vote, Answer
from myauth.models import User

# Register your models here.
# 未充分利用


class UserInline(admin.StackedInline):
    model = User
    extra = 1


class VoteInline(admin.StackedInline):
    model = Vote
    extra = 1
    exclude = ['n_vote', 'users']


class PollQuestionInline(admin.StackedInline):
    model = PollQuestion
    extra = 1
    inlines = (VoteInline,)


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    exclude = ('owner',)
    list_display = ('title', 'is_pub', 'end_date')
    list_display_links = ('title', )

    filter_vertical = ('questions',)
    inlines = (PollQuestionInline, )

    def get_queryset(self, request):
        if not request.user.is_superuser:
            polls = Poll.objects.filter(owner=request.user)
        else:
            polls = Poll.objects.all()
        return polls


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'choice_type', 'id')
    inlines = (PollQuestionInline, )


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    exclude = ('extra_data',)
    list_display = ('content', 'has_extra_data')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    filter_vertical = ('users',)


@admin.register(PollQuestion)
class PollQuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass
