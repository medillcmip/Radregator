from django.contrib import admin
from core.models import Summary,Topic,Comment,UserProfile,\
    CommentType,CommentRelation,CommentResponse
from tagger.models import Tag
from clipper.models import Article, NewsOrganization, Clip
from django.contrib.auth.models import User

class SummaryAdmin(admin.ModelAdmin):
    search_fields = ['text']
    
class TopicAdmin(admin.ModelAdmin):
    search_fields = ['curators__username', 'topic_tags__name', 'title']
    prepopulated_fields = {"slug": ("title",)}

class CommentAdmin(admin.ModelAdmin):
    search_fields = ['text', 'related__text', 'user__user__username', 'comment_type__name', 'tags__name']

class CommentTypeAdmin(admin.ModelAdmin):
    pass

class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']

class CommentRelationAdmin(admin.ModelAdmin):
    pass

class CommentResponseAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'type') 

class ArticleAdmin(admin.ModelAdmin):
    pass

class NewsOrganizationAdmin(admin.ModelAdmin):
    pass

class ClipAdmin(admin.ModelAdmin):
    pass

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']

admin.site.register(Summary, SummaryAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentType, CommentTypeAdmin)
admin.site.register(CommentRelation, CommentRelationAdmin)
admin.site.register(CommentResponse, CommentResponseAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Clip, ClipAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(NewsOrganization, NewsOrganizationAdmin)
