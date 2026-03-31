from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('gioi_thieu/', views.gioi_thieu, name='gioi_thieu'),
    path('lienhe/', views.lienhe, name='lienhe'),
    path('uu_dai/', views.uudai, name='uu_dai'),
    path('tour/', views.tour, name='tour'),
    path('hotel/', views.hotel, name='hotel'),
    path('dn/', views.dn, name='dn'),
    path('dk/', views.dk, name='dk'),
    path('htmelia/', views.HTmelia, name='Htmelia'),
    path('dx/', views.dx, name='dx'),
    path('gui-lien-he/', views.gui_lien_he, name='gui_lien_he'),
    path('tourcombo/', views.tourcombo, name='tourcombo'),
    path('toggle-yeu-thich/', views.toggle_yeu_thich, name='toggle_yeu_thich'),
    path('luu-dat-tour/', views.luu_dat_tour, name='luu_dat_tour'),
    path('gui-danh-gia/', views.gui_danh_gia, name='gui_danh_gia'),
    path('luu-dat-khach-san/', views.luu_dat_khach_san, name='luu_dat_khach_san'),
    path('khach-san/<str:link_chi_tiet>/', views.chi_tiet_khach_san, name='chi_tiet_khach_san'),
    path('luu-dat-khach-san/', views.luu_dat_khach_san, name='luu_dat_khach_san'),
    path('<str:link_chi_tiet>/', views.chi_tiet_tour, name='chi_tiet_tour'),
    path('xac-nhan-dat-tour/<str:link_chi_tiet>/', views.xac_nhan_dat_tour, name='xac_nhan_dat_tour'),
]