import datetime
from django.shortcuts import render,redirect
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from django.urls import reverse
from read_statistics.utils import get_seven_days_read_data,get_today_hot_data,get_yesterday_hot_data
from blog.models import Blog

def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today-datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date) \
                                .values('id','title') \
                                .annotate(read_num_sum=Sum('read_details__read_num')) \
                                .order_by('-read_num_sum')
    return blogs[:5]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    read_nums,dates = get_seven_days_read_data(blog_content_type)
    
    #获取7天热门博客缓存数据
    week_hot_blogs = cache.get('week_hot_blogs')
    if week_hot_blogs is None:
        week_hot_blogs = get_7_days_hot_blogs()
        cache.set('week_hot_blogs',week_hot_blogs,3600)

    context={}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['week_hot_blogs'] = week_hot_blogs
    return render(request,'home.html',context)
