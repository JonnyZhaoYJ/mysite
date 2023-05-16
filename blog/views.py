from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import read_statistics_once_read
from .models import Blog,BlogType
from comment.models import Comment
from comment.forms import CommentForm

def get_blog_list_common_data(request,blogs_list):
    paginator = Paginator(blogs_list,settings.BLOGS_NUMBER_EACH_PAGE)
    page_num=request.GET.get('page',1)  # 获取url页码参数（GET请求）
    page_of_blogs=paginator.get_page(page_num)
    page_num_current=page_of_blogs.number   # 获取当前页码
    page_num_count = paginator.num_pages    # 获取最大页数
    # 获取当前页码前后2页
    page_range=list(range(max(page_num_current-2,1),page_num_current)) + \
                list(range(page_num_current,min(page_num_current+2,page_num_count)+1))
    if page_range[0] > 1+1:
        page_range.insert(0,'...')
    if page_range[-1] < page_num_count-1:
        page_range.append('...')   
    if page_range[0] != 1:
        page_range.insert(0,1)  # List第0位（即第一位），insert插入数字1
    if page_range[-1] != page_num_count:   # -1代表最后一位
        page_range.append(page_num_count)  # append添加

    # 获取日期对应的博客数量
    blog_dates= Blog.objects.dates('created_time','month',order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                        created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    ''' # annotate解决
    blog_types=BlogType.objects.all()
    blog_type_list=[]
    for blog_type in blog_types
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_type_list.append(blog_type)'''

    # 获取context信息
    context={}
    context['page_of_blogs']=page_of_blogs
    context['page_range']=page_range
    context['blogs']=page_of_blogs.object_list
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_list=Blog.objects.all()
    context=get_blog_list_common_data(request,blogs_list)
    return render(request,'blog/blog_list.html',context)

def blogs_with_type(request,blog_type_pk):
    blog_type=get_object_or_404(BlogType,pk=blog_type_pk)
    blogs_list=Blog.objects.filter(blog_type=blog_type)
    context=get_blog_list_common_data(request,blogs_list)
    context['blog_type']=blog_type
    return render(request,'blog/blogs_with_type.html',context)

def blogs_with_date(request,year,month):
    blogs_list=Blog.objects.filter(created_time__year=year,created_time__month=month)
    context=get_blog_list_common_data(request,blogs_list)
    context['blogs_with_date']='%s年%s月' % (year,month)
    return render(request,'blog/blogs_with_date.html',context)

def blog_detail(request,blog_pk):
    blog = get_object_or_404(Blog,pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request,blog)
 
    context={}
    context['blog_previous']=Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['blog_next']=Blog.objects.filter(created_time__lt=blog.created_time).first()   
    context['blog']=blog
    context['user']=request.user
    response = render(request,'blog/blog_detail.html',context)  # 相应
    response.set_cookie(read_cookie_key,'true') # 阅读次数cookie标记
    return response

