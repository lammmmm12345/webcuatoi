from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# --- 1. Model User (Kế thừa AbstractUser) ---
class User(AbstractUser):
    so_dien_thoai = models.CharField(max_length=20, blank=True, null=True)
    dia_chi = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.username

# --- 2. Model Tour ---
class Tour(models.Model):
    tour_id = models.AutoField(primary_key=True)
    ten_tour = models.CharField(max_length=200)
    mo_ta = models.TextField(blank=True, null=True)
    diem_khoi_hanh = models.CharField(max_length=100, blank=True, null=True)
    diem_den = models.CharField(max_length=100, blank=True, null=True)
    gia = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    so_ngay = models.IntegerField(blank=True, null=True)
    so_cho = models.IntegerField(blank=True, null=True)
    trang_thai = models.BooleanField(default=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    anh_dai_dien = models.CharField(max_length=500, blank=True, null=True)
    link_chi_tiet = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False  
        db_table = 'tour'

    def __str__(self):
        return self.ten_tour

# --- 3. Model Khách Sạn ---
class KhachSan(models.Model):
    khach_san_id = models.AutoField(primary_key=True)
    ten_khach_san = models.CharField(max_length=200)
    dia_diem = models.CharField(max_length=200)
    gia_mot_dem = models.DecimalField(max_digits=15, decimal_places=2)
    gia_cu = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    mo_ta = models.TextField(null=True, blank=True)
    anh_dai_dien = models.TextField(null=True, blank=True)
    link_chi_tiet = models.CharField(max_length=100, null=True, blank=True)
    trang_thai = models.BooleanField(default=True)

    class Meta:
        db_table = 'khach_san'
        managed = False 
        verbose_name = 'Khách sạn'
        verbose_name_plural = 'Danh sách Khách sạn'

    def __str__(self):
        return self.ten_khach_san

# --- 4. Model Đặt Tour ---
class DatTour(models.Model):
    STATUS_CHOICES = [
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Đã xác nhận', 'Đã xác nhận'),
        ('Đã hủy', 'Đã hủy'),
    ]

    dat_tour_id = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='nguoi_dung_id')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, db_column='tour_id') 
    so_nguoi = models.IntegerField(blank=True, null=True)
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    trang_thai = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Chờ xác nhận')
    ngay_dat = models.DateTimeField(auto_now_add=True)
    ngay_khoi_hanh = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'dat_tour'
        verbose_name = "Đơn đặt tour"
        verbose_name_plural = "Danh sách đặt tour"

    def __str__(self):
        return f"Đơn #{self.dat_tour_id} - {self.nguoi_dung.username}"

# --- 5. Model Đặt Khách Sạn ---
class DatKhachSan(models.Model):
    STATUS_CHOICES = [
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Đã xác nhận', 'Đã xác nhận'),
        ('Đã hủy', 'Đã hủy'),
    ]

    dat_khach_san_id = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='nguoi_dung_id')
    khach_san = models.ForeignKey(KhachSan, on_delete=models.CASCADE, db_column='khach_san_id')
    ngay_nhan = models.DateField()
    ngay_tra = models.DateField()
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2)
    trang_thai = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Chờ xác nhận')

    class Meta:
        db_table = 'dat_khach_san'
        managed = False
        verbose_name = 'Đơn đặt Khách Sạn'
        verbose_name_plural = 'Quản lý Đặt Khách sạn'

    def __str__(self):
        return f"Đơn KS #{self.dat_khach_san_id} - {self.nguoi_dung.username}"

# --- 6. Model Đánh Giá ---
class DanhGia(models.Model):
    danh_gia_id = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='nguoi_dung_id')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, db_column='tour_id', blank=True, null=True)
    khach_san = models.ForeignKey(KhachSan, on_delete=models.CASCADE, db_column='khach_san_id', blank=True, null=True)
    so_sao = models.IntegerField(blank=True, null=True)
    noi_dung = models.TextField(blank=True, null=True)
    ngay_danh_gia = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'danh_gia'

# --- 7. Model Liên Hệ ---
class LienHe(models.Model):
    lien_he_id = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='nguoi_dung_id')
    ho_ten = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    so_dien_thoai = models.CharField(max_length=20)
    tieu_de = models.CharField(max_length=200)
    noi_dung = models.TextField()
    trang_thai = models.CharField(max_length=50, default='Chưa xử lý')
    ngay_gui = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lien_he' 
        managed = False       
        verbose_name = "Liên hệ từ khách"
        verbose_name_plural = "Danh sách liên hệ"

    def __str__(self):
        return f"{self.ho_ten} - {self.tieu_de}"