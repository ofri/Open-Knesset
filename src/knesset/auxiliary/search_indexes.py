import datetime
from haystack import indexes
from haystack import site
from django.contrib.comments import Comment


class CommentIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='userinfo')
    comment = indexes.CharField(model_attr='comment')
    submit_date = indexes.DateTimeField(model_attr='submit_date')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Comment.objects.filter(is_public=True) 


site.register(Comment, CommentIndex)


