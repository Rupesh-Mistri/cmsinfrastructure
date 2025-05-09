from django.contrib import admin
from django.urls import path,include,re_path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('',index,name='index'),
    path('', login_view, name='login'),
    path('data', index, name='index'),
    path('home',home,name='home'),
    path('register/', register_view, name='register'),
    path('cascade_ajax/', cascade_ajax, name='cascade_ajax'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('test/', test, name='test'),
    path('profile/', profile, name='profile'),
    path('referral_list/', referral_list, name='referral_list'),
    path('referring_registration/', referring_registration, name='referring_registration'),
    path('land_sold_list/', land_sold_list, name='land_sold_list'),

    path('purchaser_detail_form/', purchaser_detail_form, name='purchaser_detail_form'),
    path('member_tree/<id>/', member_tree, name='member_tree'),

    path('plot_booking_details/<action>/<id>/', plot_booking_details, name='plot_booking_details'),
    path('get_sponser_name_ajax/', get_sponser_name_ajax, name='get_sponser_name_ajax'),

    path('earning_withrew/', earning_withrew, name='earning_withrew'),
    path('emi_payment/', emi_payment, name='emi_payment'),
    path('emi_payment_receipt/<payment_id>', emi_payment_receipt, name='emi_payment_receipt'),
    
    path('side_master_list/', side_master_list, name='side_master_list'),
    # path('side_master_manage/', side_master_manage, name='side_master_manage'),
    re_path(r'^side_master_manage/(?P<action>create|update)/(?P<id>\d+)?$', side_master_manage, name='side_master_manage'),

    path('plot_master_list/', plot_master_list, name='plot_master_list'),
    re_path(r'^plot_master_manage/(?P<action>create|update)/(?P<id>\d+)?$', plot_master_manage, name='plot_master_manage'),

    path('fetch_plot_details_by_side/', fetch_plot_details_by_side, name='fetch_plot_details_by_side'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

