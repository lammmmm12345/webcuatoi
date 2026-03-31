from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum           # <-- Đã thêm thư viện tính tổng
from django.contrib import messages        # <-- Đã thêm thư viện bắn thông báo
from .models import User, DatTour, Tour
from .models import KhachSan, DatKhachSan 
from .models import LienHe

# 1. Cấu hình hiển thị cho User tùy chỉnh
class MyUserAdmin(UserAdmin):
    model = User
    # Những cột sẽ hiển thị ở trang danh sách người dùng
    list_display = ['username', 'email', 'so_dien_thoai', 'is_staff', 'is_active']
    
    # Thêm các trường tùy chỉnh vào trang sửa thông tin User
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('so_dien_thoai', 'dia_chi')}),
    )
    
    # Thêm các trường tùy chỉnh vào trang thêm mới User
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {'fields': ('so_dien_thoai', 'dia_chi')}),
    )

# Đăng ký model User với cấu hình MyUserAdmin
admin.site.register(User, MyUserAdmin)


# 2. Cấu hình hiển thị cho Đơn đặt tour (Có tính doanh thu)
@admin.register(DatTour)
class DatTourAdmin(admin.ModelAdmin):
    list_display = ('dat_tour_id', 'hien_thi_khach_hang', 'hien_thi_tour', 'ngay_khoi_hanh', 'tong_tien', 'trang_thai')
    list_editable = ('trang_thai',)
    list_filter = ('trang_thai', 'ngay_dat')

    def hien_thi_khach_hang(self, obj):
        return obj.nguoi_dung.username if obj.nguoi_dung else "N/A"
    hien_thi_khach_hang.short_description = 'Khách hàng'

    def hien_thi_tour(self, obj):
        return obj.tour.ten_tour if obj.tour else "N/A"
    hien_thi_tour.short_description = 'Tên Tour'

    # --- HÀM TỰ ĐỘNG TÍNH DOANH THU TOUR ---
    def changelist_view(self, request, extra_context=None):
        # Tính tổng tiền các đơn 'Đã xác nhận'
        tong_doanh_thu = DatTour.objects.filter(trang_thai='Đã xác nhận').aggregate(total=Sum('tong_tien'))['total']
        
        if tong_doanh_thu is None:
            tong_doanh_thu = 0
            
        doanh_thu_str = f"{int(tong_doanh_thu):,}đ".replace(',', '.')
        
        # Hiển thị thông báo trên cùng trang Admin
        messages.info(request, f" TỔNG DOANH THU ĐẶT TOUR (ĐÃ XÁC NHẬN): {doanh_thu_str}")
        
        return super().changelist_view(request, extra_context=extra_context)


# 3. Đăng ký các model khác
admin.site.register(Tour)


@admin.register(LienHe)
class LienHeAdmin(admin.ModelAdmin):
    list_display = ('ho_ten', 'email', 'so_dien_thoai', 'tieu_de', 'noi_dung', 'trang_thai', 'ngay_gui')
    list_editable = ('trang_thai',)
    list_filter = ('trang_thai', 'ngay_gui')
    search_fields = ('ho_ten', 'email', 'noi_dung')
    ordering = ('-ngay_gui',)


@admin.register(KhachSan)
class KhachSanAdmin(admin.ModelAdmin):
    list_display = ['khach_san_id', 'ten_khach_san', 'dia_diem', 'gia_mot_dem', 'trang_thai']
    search_fields = ['ten_khach_san', 'dia_diem']
    list_filter = ['dia_diem', 'trang_thai']
    list_editable = ['trang_thai'] 
    list_per_page = 20


# 4. Cấu hình hiển thị cho Đơn đặt khách sạn (Có tính doanh thu)
@admin.register(DatKhachSan)
class DatKhachSanAdmin(admin.ModelAdmin):
    list_display = ['dat_khach_san_id', 'khach_san', 'nguoi_dung', 'ngay_nhan', 'ngay_tra', 'tong_tien', 'trang_thai']
    search_fields = ['khach_san__ten_khach_san', 'nguoi_dung__username', 'nguoi_dung__email']
    list_filter = ['trang_thai', 'ngay_nhan']
    list_editable = ['trang_thai'] 
    list_per_page = 20

    # --- HÀM TỰ ĐỘNG TÍNH DOANH THU KHÁCH SẠN ---
    def changelist_view(self, request, extra_context=None):
        # Tính tổng tiền các đơn phòng 'Đã xác nhận'
        tong_doanh_thu = DatKhachSan.objects.filter(trang_thai='Đã xác nhận').aggregate(total=Sum('tong_tien'))['total']
        
        if tong_doanh_thu is None:
            tong_doanh_thu = 0
            
        doanh_thu_str = f"{int(tong_doanh_thu):,}đ".replace(',', '.')
        
        # Hiển thị thông báo trên cùng trang Admin
        messages.info(request, f" TỔNG DOANH THU KHÁCH SẠN (ĐÃ XÁC NHẬN): {doanh_thu_str}")
        
        return super().changelist_view(request, extra_context=extra_context)