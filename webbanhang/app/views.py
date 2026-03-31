from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from .models import User  # Custom User Model
from django.core.paginator import Paginator

# 1. HÀM DÙNG CHUNG (HELPER FUNCTIONS CHO NAVBAR)

def get_fav_tours(user):
    if not user.is_authenticated:
        return []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT t.tour_id, t.ten_tour, t.gia, t.anh_dai_dien, t.link_chi_tiet
            FROM yeu_thich_tour yt
            JOIN tour t ON yt.tour_id = t.tour_id
            WHERE yt.nguoi_dung_id = %s
            ORDER BY yt.ngay_thêm DESC
        """, [user.id])
        rows = cursor.fetchall()
    
    fav_tours = []
    for row in rows:
        fav_tours.append({
            'id': row[0], 'name': row[1],
            'price': f"{int(row[2]):,}đ".replace(',', '.') if row[2] else '',
            'anh_dai_dien': row[3] if row[3] else "https://placehold.co/100x100?text=Tour",
            'link_chi_tiet': row[4]
        })
    return fav_tours

def get_booked_tours(user):
    if not user.is_authenticated:
        return []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT d.dat_tour_id, t.ten_tour, t.anh_dai_dien, t.link_chi_tiet, d.tong_tien, d.trang_thai, d.ngay_khoi_hanh, t.tour_id,
                   (SELECT COUNT(*) FROM danh_gia dg WHERE dg.dat_tour_id = d.dat_tour_id) as da_danh_gia
            FROM dat_tour d
            JOIN tour t ON d.tour_id = t.tour_id
            WHERE d.nguoi_dung_id = %s
            ORDER BY d.ngay_dat DESC
        """, [user.id])
        rows = cursor.fetchall()
        
    booked_tours = []
    for row in rows:
        booked_tours.append({
            "id": row[0], "name": row[1],
            "anh_dai_dien": row[2] if row[2] else "https://placehold.co/100x100?text=Tour",
            "link_chi_tiet": row[3],
            "tong_tien": f"{int(row[4]):,}đ".replace(',', '.') if row[4] else "0đ",
            "trang_thai": row[5],
            "ngay_khoi_hanh": row[6].strftime('%d/%m/%Y') if row[6] else "Chưa rõ",
            "da_danh_gia": row[8] > 0
        })
    return booked_tours

def get_booked_hotels(user):
    if not user.is_authenticated:
        return []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ks.ten_khach_san, ks.anh_dai_dien, ks.link_chi_tiet, 
                   dks.ngay_nhan, dks.ngay_tra, dks.tong_tien, dks.trang_thai
            FROM dat_khach_san dks
            JOIN khach_san ks ON dks.khach_san_id = ks.khach_san_id
            WHERE dks.nguoi_dung_id = %s
            ORDER BY dks.dat_khach_san_id DESC
        """, [user.id])
        rows = cursor.fetchall()
    
    booked_hotels = []
    for row in rows:
        booked_hotels.append({
            'name': row[0],
            'anh_dai_dien': row[1] if row[1] else "https://placehold.co/400x300",
            'link_chi_tiet': row[2],
            'ngay_nhan': row[3].strftime('%d/%m/%Y') if row[3] else '',
            'ngay_tra': row[4].strftime('%d/%m/%Y') if row[4] else '',
            'tong_tien': f"{int(row[5]):,}đ".replace(',', '.') if row[5] else '',
            'trang_thai': row[6]
        })
    return booked_hotels


# 2. CÁC TRANG HIỂN THỊ CHÍNH

def dashboard(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tour_id, ten_tour, gia, gia_cu, so_ngay, anh_dai_dien, link_chi_tiet 
            FROM tour WHERE trang_thai = TRUE ORDER BY tour_id LIMIT 3
        """)
        hot_deals = [{ 'ten_tour': r[1], 'gia': f"{int(r[2]):,}đ".replace(',', '.') if r[2] else "Liên hệ", 'gia_cu': f"{int(r[3]):,}đ".replace(',', '.') if r[3] else None, 'so_ngay': r[4], 'anh_dai_dien': r[5] if r[5] else "https://placehold.co/400x300", 'link_chi_tiet': r[6] } for r in cursor.fetchall()]

        cursor.execute("""
            SELECT tour_id, ten_tour, gia, so_ngay, anh_dai_dien, link_chi_tiet 
            FROM tour WHERE trang_thai = TRUE ORDER BY tour_id DESC LIMIT 4
        """)
        featured_tours = [{ 'ten_tour': r[1], 'gia': f"{int(r[2]):,}đ".replace(',', '.') if r[2] else "Liên hệ", 'so_ngay': r[3], 'anh_dai_dien': r[4] if r[4] else "https://placehold.co/400x300", 'link_chi_tiet': r[5] } for r in cursor.fetchall()]

    return render(request, 'app/dashboard.html', {
        'fav_tours': get_fav_tours(request.user),
        'booked_tours': get_booked_tours(request.user),
        'booked_hotels': get_booked_hotels(request.user), 
        'hot_deals': hot_deals,        
        'featured_tours': featured_tours 
    })

def tour(request):
    tu_khoa = request.GET.get('tu_khoa', '')
    diem_den_list = request.GET.getlist('diem_den')
    so_ngay_list = request.GET.getlist('so_ngay')

    query = "SELECT tour_id, ten_tour, gia, diem_khoi_hanh, so_ngay, anh_dai_dien, gia_cu, link_chi_tiet FROM tour WHERE trang_thai = TRUE"
    params = []

    if tu_khoa:
        query += " AND (ten_tour ILIKE %s OR diem_den ILIKE %s)"
        params.extend([f"%{tu_khoa}%", f"%{tu_khoa}%"])

    if diem_den_list:
        placeholders = ', '.join(['%s'] * len(diem_den_list))
        query += f" AND diem_den IN ({placeholders})"
        params.extend(diem_den_list)

    if so_ngay_list:
        placeholders = ', '.join(['%s'] * len(so_ngay_list))
        query += f" AND so_ngay IN ({placeholders})"
        params.extend([int(i) for i in so_ngay_list]) 

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    tours_data = [{ "id": row[0], "name": row[1], "price": f"{int(row[2]):,}đ".replace(',', '.') if row[2] else "Liên hệ", "diem_khoi_hanh": row[3], "so_ngay": f"{row[4]} ngày", "anh_dai_dien": row[5] if row[5] else "https://placehold.co/300x200?text=Tour", "gia_cu": f"{int(row[6]):,}đ".replace(',', '.') if row[6] else "", "link_chi_tiet": row[7] } for row in rows]

    paginator = Paginator(tours_data, 3)
    page_obj = paginator.get_page(request.GET.get('page'))

    data = request.GET.copy()
    if 'page' in data: del data['page']

    liked_tour_ids = []
    if request.user.is_authenticated:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tour_id FROM yeu_thich_tour WHERE nguoi_dung_id = %s", [request.user.id])
            liked_tour_ids = [r[0] for r in cursor.fetchall()]

    return render(request, 'app/tour.html', {
        'tours': page_obj, 'tu_khoa': tu_khoa, 'query_string': data.urlencode(),
        'fav_tours': get_fav_tours(request.user),
        'booked_tours': get_booked_tours(request.user),
        'booked_hotels': get_booked_hotels(request.user), 
        'liked_tour_ids': liked_tour_ids
    })

def hotel(request):
    tu_khoa = request.GET.get('tu_khoa', '')
    diem_den_list = request.GET.getlist('dia_diem') 

    query = "SELECT khach_san_id, ten_khach_san, dia_diem, gia_mot_dem, anh_dai_dien, gia_cu, link_chi_tiet FROM khach_san WHERE trang_thai = TRUE"
    params = []

    if tu_khoa:
        query += " AND (ten_khach_san ILIKE %s OR dia_diem ILIKE %s)"
        params.extend([f"%{tu_khoa}%", f"%{tu_khoa}%"])

    if diem_den_list:
        placeholders = ', '.join(['%s'] * len(diem_den_list))
        query += f" AND dia_diem IN ({placeholders})"
        params.extend(diem_den_list)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    hotels_data = [{ "id": row[0], "name": row[1], "dia_diem": row[2], "price": f"{int(row[3]):,}đ".replace(',', '.') if row[3] else "Liên hệ", "anh_dai_dien": row[4] if row[4] else "https://placehold.co/400x300", "gia_cu": f"{int(row[5]):,}đ".replace(',', '.') if row[5] else "", "link_chi_tiet": row[6] } for row in rows]

    paginator = Paginator(hotels_data, 3) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    data = request.GET.copy()
    if 'page' in data: del data['page']

    return render(request, 'app/hotel.html', {
        'hotels': page_obj, 'tu_khoa': tu_khoa, 'query_string': data.urlencode(),
        'fav_tours': get_fav_tours(request.user),
        'booked_tours': get_booked_tours(request.user),
        'booked_hotels': get_booked_hotels(request.user),
    })


# 3. TRANG CHI TIẾT (TOUR & HOTEL)

def chi_tiet_tour(request, link_chi_tiet):
    with connection.cursor() as cursor:
        cursor.execute("SELECT tour_id, gia FROM tour WHERE link_chi_tiet = %s", [link_chi_tiet])
        row = cursor.fetchone()
        if not row: return render(request, 'app/404.html') 
        tour_id = row[0]
        gia_goc = int(row[1])

        cursor.execute("""
            SELECT u.last_name, u.first_name, dg.so_sao, dg.noi_dung, dg.ngay_danh_gia 
            FROM danh_gia dg
            JOIN auth_user u ON dg.nguoi_dung_id = u.id
            WHERE dg.tour_id = %s
            ORDER BY dg.ngay_danh_gia DESC
        """, [tour_id])
        danh_sach_danh_gia = [{ 'ho_ten': f"{dg[0]} {dg[1]}".strip(), 'so_sao': dg[2], 'noi_dung': dg[3], 'ngay_danh_gia': dg[4].strftime('%d/%m/%Y') if dg[4] else "" } for dg in cursor.fetchall()]

        cho_phep_danh_gia = False
        booking_id = request.GET.get('booking_id') 

        if request.user.is_authenticated and booking_id:
            cursor.execute("SELECT COUNT(*) FROM dat_tour WHERE dat_tour_id = %s AND nguoi_dung_id = %s AND trang_thai = 'Đã xác nhận'", [booking_id, request.user.id])
            hop_le = cursor.fetchone()[0] > 0
            
            cursor.execute("SELECT COUNT(*) FROM danh_gia WHERE dat_tour_id = %s", [booking_id])
            da_danh_gia = cursor.fetchone()[0] > 0

            if hop_le and not da_danh_gia:
                cho_phep_danh_gia = True

    return render(request, f'app/{link_chi_tiet}.html', {
        'tour_id': tour_id, 'gia_goc': gia_goc, 'gia_hien_thi': f"{gia_goc:,}đ".replace(',', '.'),
        'danh_sach_danh_gia': danh_sach_danh_gia, 'cho_phep_danh_gia': cho_phep_danh_gia, 'booking_id': booking_id,
        'fav_tours': get_fav_tours(request.user),
        'booked_tours': get_booked_tours(request.user),
        'booked_hotels': get_booked_hotels(request.user) 
    })

def chi_tiet_khach_san(request, link_chi_tiet):
    with connection.cursor() as cursor:
        cursor.execute("SELECT khach_san_id, ten_khach_san, gia_mot_dem FROM khach_san WHERE link_chi_tiet = %s", [link_chi_tiet])
        row = cursor.fetchone()
        if not row: return render(request, 'app/404.html')
        
        khach_san_id, ten_khach_san, gia_mot_dem = row[0], row[1], int(row[2])
        
    return render(request, f'app/{link_chi_tiet}.html', {
        'khach_san_id': khach_san_id, 'ten_khach_san': ten_khach_san,
        'gia_mot_dem': gia_mot_dem, 'gia_hien_thi': f"{gia_mot_dem:,}đ".replace(',', '.'),
        'fav_tours': get_fav_tours(request.user),
        'booked_tours': get_booked_tours(request.user),
        'booked_hotels': get_booked_hotels(request.user)
    })


# 4. CHỨC NĂNG XỬ LÝ (POST DATA)

def luu_dat_tour(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            so_nguoi = int(request.POST.get('nguoi_lon', 0)) + int(request.POST.get('tre_em', 0))
        except:
            so_nguoi = 1
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO dat_tour (nguoi_dung_id, tour_id, so_nguoi, tong_tien, trang_thai, ngay_dat, ngay_khoi_hanh)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """, [request.user.id, request.POST.get('tour_id'), so_nguoi, request.POST.get('tong_tien_so'), 'Chờ xác nhận', request.POST.get('ngay_khoi_hanh')])
        messages.success(request, "🎉 Đặt tour thành công!")
    return redirect('dashboard')

def xac_nhan_dat_tour(request, link_chi_tiet):
    if not request.user.is_authenticated: return redirect('dn')
    if request.method == 'POST':
        tong_tien_so = request.POST.get('tong_tien_so')
        with connection.cursor() as cursor:
            cursor.execute("SELECT tour_id, ten_tour, anh_dai_dien FROM tour WHERE link_chi_tiet = %s", [link_chi_tiet])
            t = cursor.fetchone()
        if not t: return render(request, 'app/404.html')

        return render(request, 'app/xac_nhan_tour.html', {
            'tour_id': t[0], 'ten_tour': t[1], 'anh_dai_dien': t[2],
            'ngay_khoi_hanh': request.POST.get('ngay_khoi_hanh'),
            'nguoi_lon': request.POST.get('nguoi_lon'), 'tre_em': request.POST.get('tre_em'),
            'tong_tien_hien_thi': f"{int(tong_tien_so):,}đ".replace(',', '.'), 'tong_tien_so': tong_tien_so,
            'fav_tours': get_fav_tours(request.user),
            'booked_tours': get_booked_tours(request.user),
            'booked_hotels': get_booked_hotels(request.user) 
        })
    return redirect('dashboard')

def luu_dat_khach_san(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Vui lòng đăng nhập để đặt phòng khách sạn!")
        return redirect('dn') 

    if request.method == 'POST':
        khach_san_id = request.POST.get('khach_san_id')
        ngay_nhan = request.POST.get('ngay_nhan')
        ngay_tra = request.POST.get('ngay_tra')
        tong_tien = request.POST.get('tong_tien_so') 
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO dat_khach_san (nguoi_dung_id, khach_san_id, ngay_nhan, ngay_tra, tong_tien, trang_thai)
                VALUES (%s, %s, %s, %s, %s, 'Chờ xác nhận')
            """, [request.user.id, khach_san_id, ngay_nhan, ngay_tra, tong_tien])
        
        messages.success(request, "🎉 Đặt phòng thành công! Chúng tôi sẽ liên hệ lại sớm nhất.")
        return redirect('dashboard') 
    return redirect('hotel')

def gui_lien_he(request):
    if request.method == 'POST' and request.user.is_authenticated:
        ho_ten = request.POST.get('ho_ten')
        email = request.POST.get('email')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        tieu_de = request.POST.get('tieu_de')
        noi_dung = request.POST.get('noi_dung')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO lien_he (nguoi_dung_id, ho_ten, email, so_dien_thoai, tieu_de, noi_dung, trang_thai, ngay_gui)
                VALUES (%s, %s, %s, %s, %s, %s, 'Chưa xử lý', NOW())
            """, [request.user.id, ho_ten, email, so_dien_thoai, tieu_de, noi_dung])
            
        messages.success(request, "Cảm ơn bạn! Yêu cầu của bạn đã được gửi đến bộ phận hỗ trợ.")
        return redirect('lienhe')
    return redirect('dn') 

def toggle_yeu_thich(request):
    if request.method == "POST" and request.user.is_authenticated:
        tour_id = request.POST.get('tour_id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT yeu_thich_id FROM yeu_thich_tour WHERE nguoi_dung_id = %s AND tour_id = %s", [request.user.id, tour_id])
            if cursor.fetchone():
                cursor.execute("DELETE FROM yeu_thich_tour WHERE nguoi_dung_id = %s AND tour_id = %s", [request.user.id, tour_id])
                return JsonResponse({'status': 'unliked', 'tour_id': tour_id})
            else:
                cursor.execute("INSERT INTO yeu_thich_tour (nguoi_dung_id, tour_id) VALUES (%s, %s)", [request.user.id, tour_id])
                cursor.execute("SELECT ten_tour, gia, anh_dai_dien, link_chi_tiet FROM tour WHERE tour_id = %s", [tour_id])
                t = cursor.fetchone()
                return JsonResponse({'status': 'liked', 'tour': {
                    "id": tour_id, "name": t[0], "price": f"{int(t[1]):,}đ".replace(',', '.'),
                    "anh_dai_dien": t[2] if t[2] else "https://placehold.co/100x100?text=Tour", "link_chi_tiet": t[3]
                }})
    return JsonResponse({'status': 'error'}, status=400)

def gui_danh_gia(request):
    if request.method == 'POST' and request.user.is_authenticated:
        tour_id = request.POST.get('tour_id')
        link_chi_tiet = request.POST.get('link_chi_tiet')
        booking_id = request.POST.get('booking_id') 
        so_sao = request.POST.get('so_sao')
        noi_dung = request.POST.get('noi_dung')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO danh_gia (tour_id, nguoi_dung_id, dat_tour_id, so_sao, noi_dung, ngay_danh_gia)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, [tour_id, request.user.id, booking_id, so_sao, noi_dung])
        
        messages.success(request, "Cảm ơn bạn đã đánh giá! Ý kiến của bạn đã được ghi nhận.")
        return redirect('chi_tiet_tour', link_chi_tiet=link_chi_tiet)
    return redirect('dashboard')


# 5. TRANG TĨNH & AUTH

def gioi_thieu(request): return render(request, 'app/gioi_thieu.html', {'fav_tours': get_fav_tours(request.user), 'booked_tours': get_booked_tours(request.user), 'booked_hotels': get_booked_hotels(request.user)})
def lienhe(request): return render(request, 'app/lienhe.html', {'fav_tours': get_fav_tours(request.user), 'booked_tours': get_booked_tours(request.user), 'booked_hotels': get_booked_hotels(request.user)})
def uudai(request): return render(request, 'app/uu_dai.html', {'fav_tours': get_fav_tours(request.user), 'booked_tours': get_booked_tours(request.user), 'booked_hotels': get_booked_hotels(request.user)})    
def tourcombo(request): return render(request, 'app/tourcombo-phuquoc.html', {'fav_tours': get_fav_tours(request.user), 'booked_tours': get_booked_tours(request.user), 'booked_hotels': get_booked_hotels(request.user)})
def HTmelia(request): return render(request, 'app/HTmelia.html', {'fav_tours': get_fav_tours(request.user), 'booked_tours': get_booked_tours(request.user), 'booked_hotels': get_booked_hotels(request.user)})

def dk(request):
    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        so_dien_thoai = request.POST.get('so_dien_thoai')

        # 1. Kiểm tra Email đã tồn tại chưa
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email này đã được đăng ký. Vui lòng sử dụng email khác!")
            
        # 2. Kiểm tra mật khẩu xác nhận có khớp không
        elif password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp. Vui lòng nhập lại!")
            
        # 3. Nếu vượt qua hết các lỗi trên thì mới cho phép tạo tài khoản
        else:
            name_parts = ho_ten.split(' ')
            first_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            last_name = name_parts[0]
            
            User.objects.create_user(
                username=email, 
                email=email, 
                password=password, 
                first_name=first_name, 
                last_name=last_name, 
                so_dien_thoai=so_dien_thoai
            )
            messages.success(request, "🎉 Đăng ký thành công! Vui lòng đăng nhập.")
            return redirect('dn')
            
    # Nếu là GET request hoặc có lỗi (POST nhưng tạch IF), sẽ render lại form dk kèm dữ liệu navbar
    return render(request, 'app/dk.html', {
        'fav_tours': get_fav_tours(request.user), 
        'booked_tours': get_booked_tours(request.user), 
        'booked_hotels': get_booked_hotels(request.user)
    })
def dn(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Sai tài khoản hoặc mật khẩu!")
    return render(request, 'app/dn.html', {'fav_tours': get_fav_tours(request.user), 'booked_tours': get_booked_tours(request.user), 'booked_hotels': get_booked_hotels(request.user)})

def dx(request):
    logout(request)
    return redirect('dashboard')