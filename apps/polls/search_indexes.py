from haystack import indexes
from .models import Poll


class PollsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, model_attr='title')
    desc = indexes.CharField(model_attr='description')

    def get_model(self):
        return Poll

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_open=True)


