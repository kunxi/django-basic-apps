import datetime, markdown
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from django.conf import settings
from tagging.fields import TagField
from markupfield.fields import MarkupField
from markupfield import markup

from markup import wordpress_renderer
from basic.blog.managers import PublicManager

class Category(models.Model):
    """Category model."""
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        db_table = 'blog_categories'
        ordering = ('title',)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog_category_detail', None, {'slug': self.slug})

MARKUP_TYPES = [
    ("wordpress", wordpress_renderer),
]
MARKUP_TYPES += markup.DEFAULT_MARKUP_TYPES

class Post(models.Model):
    """Post model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
        (2, _('Private')),
    )

    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique_for_date='publish')
    author = models.ForeignKey(User, blank=True, null=True)
    body = MarkupField(_('body'), markup_choices=MARKUP_TYPES, default_markup_type='markdown')
    tease = MarkupField(_('tease'), markup_choices=MARKUP_TYPES, default_markup_type='markdown', blank=True, help_text=_('Concise text suggested. Does not appear in RSS feed.'))
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    allow_comments = models.BooleanField(_('allow comments'), default=True)
    publish = models.DateTimeField(_('publish'), default=datetime.datetime.now)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    categories = models.ManyToManyField(Category, blank=True)
    tags = TagField()
    objects = PublicManager()

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        db_table  = 'blog_posts'
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog_detail', None, {
            'year': self.publish.year,
            'month': self.publish.strftime('%m'),
            'day': self.publish.strftime('%d'),
            'slug': self.slug
        })

    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)


class BlogRoll(models.Model):
    """Other blogs you follow."""
    name = models.CharField(max_length=100)
    url = models.URLField(verify_exists=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('sort_order', 'name',)
        verbose_name = _('blog roll')
        verbose_name_plural = _('blog roll')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.url

import unittest
class TestWordPressMarkup(unittest.TestCase):
    def setUp(self):
        self.spams = []

    def tearDown(self):
        for x in self.spams:
            x.delete()

    def testLinebreak(self):
        post = Post(title='linebreak', body='linebreak\n', body_markup_type='wordpress')
        post.save()
        self.spams.append(post)
        self.assertEqual(post.body.rendered, '<p>linebreak<br /></p>')

    def testPygments(self):
        post = Post(title='javascript rendeirng', body='<code class="javascript">var x = new Date(); alert(x)</code>', body_markup_type='wordpress')
        post.save()
        self.spams.append(post)
        self.assertEqual(post.body.rendered, '<p><div class="highlight"><pre><span class="kd">var</span> <span class="nx">x</span> <span class="o">=</span> <span class="k">new</span> <span class="nb">Date</span><span class="p">();</span> <span class="nx">alert</span><span class="p">(</span><span class="nx">x</span><span class="p">)</span><br /></pre></div><br /></p>') 

