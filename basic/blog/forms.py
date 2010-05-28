import django.forms as forms
from basic.blog.models import Post
from basic.blog.widgets import AutoCompleteTagInput
from tagging.forms import TagField

class PostForm(forms.ModelForm):
    #body = forms.CharField(widget=MarkItUpWidget())
    #tease = forms.CharField(widget=MarkItUpWidget())
    tags = TagField(widget=AutoCompleteTagInput())

    class Meta:
        model=Post
        exclude=('author', 'slug', 'allow_comments', 'publish',)