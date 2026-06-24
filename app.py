from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash, Response
import pymysql
import re  # Modul untuk Regular Expression (Regex)
import os  # Modul untuk manajemen lokasi File I/O (Penting untuk Hosting)
import time  # Modul untuk menghitung waktu eksekusi (Time Complexity)

app = Flask(__name__)
# Menggunakan kunci rahasia dari environment variable, jika tidak ada pakai fallback aman
app.secret_key = os.environ.get('SECRET_KEY', 'kunci_rahasia_sistem_manajemen_mahasiswa_aman') 

# KONFIGURASI HOSTING: Deteksi otomatis kredensial database dari server cloud
def get_db_connection():
    return pymysql.connect(
        host='mysql-125dfe61-dalilamaulina-8476.h.aivencloud.com',
        user='avnadmin',
        password='AVNS_ThFxexLujancyCB63QC',
        database='defaultdb',
        port=int('23340'),
        cursorclass=pymysql.cursors.DictCursor
    )

# =========================================================================
# 2. PENERAPAN OOP (CLASS, OBJECT, ENKAPSULASI, INHERITANCE, & POLIMORFISME)
# =========================================================================
class Orang:
    def __init__(self, nama):
        self._nama = nama  # Protected Variable (Enkapsulasi)

    def get_nama(self):
        return self._nama
    
    def deskripsi_peran(self):
        return "Ini adalah entitas manusia di lingkungan kampus."

class Mahasiswa(Orang):    # Pewarisan / Inheritance dari class Orang
    def __init__(self, id_mhs, nim, nama, jurusan, semester, ipk, email, no_hp, status=None):
        super().__init__(nama) 
        self.id = id_mhs
        self.nim = nim
        self.jurusan = jurusan
        self.semester = semester
        self.ipk = float(ipk) 
        self.email = email
        self.no_hp = no_hp
        self.status = status if status else "Aktif"

    def deskripsi_peran(self):
        return f"Mahasiswa bernama {self.get_nama()} dengan NIM {self.nim} aktif di jurusan {self.jurusan}."

# =========================================================================
# 3. IMPLEMENTASI ALGORITMA MANUAL (SORTING & SEARCHING) & TIME COMPLEXITY
# =========================================================================
def bubble_sort_ipk(list_objek_mahasiswa):
    start_time = time.time()
    n = len(list_objek_mahasiswa)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if list_objek_mahasiswa[j].ipk < list_objek_mahasiswa[j + 1].ipk:
                list_objek_mahasiswa[j], list_objek_mahasiswa[j + 1] = list_objek_mahasiswa[j + 1], list_objek_mahasiswa[j]
    end_time = time.time()
    waktu_eksekusi = end_time - start_time
    return list_objek_mahasiswa, waktu_eksekusi

def selection_sort_ipk(list_objek_mahasiswa):
    start_time = time.time()
    n = len(list_objek_mahasiswa)
    for i in range(n):
        max_idx = i
        for j in range(i + 1, n):
            if list_objek_mahasiswa[j].ipk > list_objek_mahasiswa[max_idx].ipk:
                max_idx = j
        list_objek_mahasiswa[i], list_objek_mahasiswa[max_idx] = list_objek_mahasiswa[max_idx], list_objek_mahasiswa[i]
    end_time = time.time()
    waktu_eksekusi = end_time - start_time
    return list_objek_mahasiswa, waktu_eksekusi

def linear_search_mahasiswa(list_objek_mahasiswa, keyword):
    hasil_pencarian = []
    keyword = keyword.lower()
    for mhs in list_objek_mahasiswa:
        if keyword in mhs.nim.lower() or keyword in mhs.get_nama().lower():
            hasil_pencarian.append(mhs)
    return hasil_pencarian

# =========================================================================
# 4. ROUTING FLASK (WEB INTERACTION)
# =========================================================================
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session.clear() 
            session['is_logged_in'] = 'YA' 
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Username atau Password salah!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'is_logged_in' not in session or session['is_logged_in'] != 'YA':
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM mahasiswa")
        total_mhs = cursor.fetchone()['total']
        
        cursor.execute("SELECT AVG(ipk) as rata FROM mahasiswa")
        rata_ipk_val = cursor.fetchone()['rata']
        rata_ipk = rata_ipk_val if rata_ipk_val is not None else 0.0
        
        cursor.close()
        conn.close()

        response = make_response(render_template('dashboard.html', total_mahasiswa=total_mhs, rata_ipk=rata_ipk))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
       
    except Exception as e:
        return f"Database Error: {e}"

@app.route('/dashboard/mahasiswa')
def data_mahasiswa():
    if 'is_logged_in' not in session or session['is_logged_in'] != 'YA':
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mahasiswa")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        daftar_mahasiswa_objek = []
        for r in rows:
            status_val = r.get('status', None)
            mhs_obj = Mahasiswa(
                r['id'], r['nim'], r['nama'], r['jurusan'], 
                r['semester'], r['ipk'], r['email'], r['no_hp'], status_val
            )
            daftar_mahasiswa_objek.append(mhs_obj)

        search_query = request.args.get('search')
        if search_query:
            daftar_mahasiswa_objek = linear_search_mahasiswa(daftar_mahasiswa_objek, search_query)

        sort_query = request.args.get('sort')
        if sort_query == 'bubble':
            daftar_mahasiswa_objek, waktu_sort = bubble_sort_ipk(daftar_mahasiswa_objek)
            flash(f"Bubble Sort sukses mengurutkan IPK dalam waktu: {waktu_sort:.6f} detik.", "success")
        elif sort_query == 'selection':
            daftar_mahasiswa_objek, waktu_sort = selection_sort_ipk(daftar_mahasiswa_objek)
            flash(f"Selection Sort sukses mengurutkan IPK dalam waktu: {waktu_sort:.6f} detik.", "success")

        response = make_response(render_template('index.html', mahasiswas=daftar_mahasiswa_objek, search_query=search_query))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response

    except Exception as e:
        return f"Terjadi Kesalahan Sistem: {e}"

@app.route('/dashboard/mahasiswa/tambah', methods=['POST'])
def tambah_mahasiswa():
    if 'is_logged_in' not in session or session['is_logged_in'] != 'YA':
        return redirect(url_for('login'))

    try:
        nim = request.form.get('nim')
        nama = request.form.get('nama')
        jurusan = request.form.get('jurusan')
        semester = request.form.get('semester')
        ipk = request.form.get('ipk')
        email = request.form.get('email')
        no_hp = request.form.get('no_hp')
        status = request.form.get('status', 'Aktif')

        if not re.match(r'^\d+$', nim):  
            flash("Gagal: NIM harus berupa angka seluruhnya!", "danger")
            return redirect(url_for('data_mahasiswa'))
        if not re.match(r'^[a-zA-Z\s]+$', nama): 
            flash("Gagal: Nama hanya boleh mengandung huruf dan spasi!", "danger")
            return redirect(url_for('data_mahasiswa'))
        
        try:
            float_ipk = float(ipk)
            if float_ipk < 0.0 or float_ipk > 4.0:
                flash("Gagal: IPK harus di antara rentang 0.0 sampai 4.0!", "danger")
                return redirect(url_for('data_mahasiswa'))
        except ValueError:
            flash("Gagal: Format angka IPK salah! Gunakan titik (.)", "danger")
            return redirect(url_for('data_mahasiswa'))

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO mahasiswa (nim, nama, jurusan, semester, ipk, email, no_hp, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (nim, nama, jurusan, semester, ipk, email, no_hp, status))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Data mahasiswa {nama} (NIM: {nim}) BERHASIL ditambahkan!", "success")
        return redirect(url_for('data_mahasiswa'))
    except Exception as e:
        flash(f"Gagal Input Data: {e}", "danger")
        return redirect(url_for('data_mahasiswa'))

@app.route('/dashboard/mahasiswa/edit/<nim>', methods=['POST'])
def edit_mahasiswa(nim):
    if 'is_logged_in' not in session or session['is_logged_in'] != 'YA':
        return redirect(url_for('login'))

    try:
        nama = request.form.get('nama')
        jurusan = request.form.get('jurusan')
        semester = request.form.get('semester')
        ipk = request.form.get('ipk')
        email = request.form.get('email')
        no_hp = request.form.get('no_hp')
        status = request.form.get('status', 'Aktif')

        if not re.match(r'^[a-zA-Z\s]+$', nama): 
            flash("Gagal: Nama hanya boleh mengandung huruf dan spasi!", "danger")
            return redirect(url_for('data_mahasiswa'))
        
        try:
            float_ipk = float(ipk)
            if float_ipk < 0.0 or float_ipk > 4.0:
                flash("Gagal: IPK harus di antara rentang 0.0 sampai 4.0!", "danger")
                return redirect(url_for('data_mahasiswa'))
        except ValueError:
            flash("Gagal: Format angka IPK salah! Gunakan titik (.)", "danger")
            return redirect(url_for('data_mahasiswa'))

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE mahasiswa SET nama=%s, jurusan=%s, semester=%s, ipk=%s, email=%s, no_hp=%s, status=%s WHERE nim=%s"
        cursor.execute(sql, (nama, jurusan, semester, ipk, email, no_hp, status, nim))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Data mahasiswa {nama} (NIM: {nim}) BERHASIL diperbarui!", "success")
        return redirect(url_for('data_mahasiswa'))
    except Exception as e:
        flash(f"Gagal Mengubah Data: {e}", "danger")
        return redirect(url_for('data_mahasiswa'))

@app.route('/dashboard/mahasiswa/hapus/<nim>')
def hapus_mahasiswa(nim):
    if 'is_logged_in' not in session or session['is_logged_in'] != 'YA':
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM mahasiswa WHERE nim = %s"
        cursor.execute(sql, (nim,))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Data mahasiswa dengan NIM {nim} BERHASIL dihapus secara permanen!", "success")
        return redirect(url_for('data_mahasiswa'))
    except Exception as e:
        flash(f"Gagal Menghapus Data: {e}", "danger")
        return redirect(url_for('data_mahasiswa'))

# =========================================================================
# 5. PERBAIKAN FILE I/O: Output dialihkan langsung sebagai Download File
# =========================================================================
@app.route('/dashboard/mahasiswa/backup')
def backup_data_ke_file():
    if 'is_logged_in' not in session or session['is_logged_in'] != 'YA':
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mahasiswa")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Generate teks backup langsung ke memori server
        output = []
        output.append("==================================================\n")
        output.append("            BACKUP DATA MAHASISWA SYSTEM           \n")
        output.append("==================================================\n")
        output.append("NIM          | NAMA               | JURUSAN        | IPK  \n")
        output.append("--------------------------------------------------\n")
        for r in rows:
            output.append(f"{r['nim']:<12} | {r['nama']:<18} | {r['jurusan']:<14} | {r['ipk']}\n")
        output.append("==================================================\n")
        
        response_text = "".join(output)

        # Mengembalikan sebagai file unduhan langsung (Sangat aman untuk cloud hosting)
        return Response(
            response_text,
            mimetype="text/plain",
            headers={"Content-disposition": "attachment; filename=backup_mahasiswa.txt"}
        )
        
    except Exception as e:
        flash(f"Penanganan Gagal pada File I/O: {e}", "danger")
        return redirect(url_for('data_mahasiswa'))

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('login'))

# =========================================================================
# OTOMATISASI PEMBUATAN TABEL SAAT SEEDING AWAL SERVER
# =========================================================================
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nim VARCHAR(20) UNIQUE NOT NULL,
            nama VARCHAR(100) NOT NULL,
            jurusan VARCHAR(100) NOT NULL,
            semester INT NOT NULL,
            ipk FLOAT NOT NULL,
            email VARCHAR(100),
            no_hp VARCHAR(20),
            status VARCHAR(20) DEFAULT 'Aktif'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print(" -> [Sistem] Pengecekan Database Berhasil.")
    except Exception as e:
        print(f" -> [Sistem Warning] Gagal memeriksa tabel: {e}")

# Inisialisasi database dijalankan secara global agar terpicu di Vercel
init_db()

# WAJIB UNTUK VERCEL HOSTING: Mengekspos objek wsgi Flask ke serverless environment
app = app
