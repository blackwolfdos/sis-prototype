import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with the new, integrated schema and sample data."""
    
    DB_FILE = 'sis.db'
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"File database '{DB_FILE}' yang lama telah dihapus.")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # --- SKEMA DATABASE ---
    cursor.executescript('''
        CREATE TABLE User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'pengajar', 'siswa'))
        );
        
        CREATE TABLE Sekolah (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_sekolah TEXT UNIQUE NOT NULL,
            nama_sekolah TEXT NOT NULL,
            alamat TEXT,
            jenis_sekolah TEXT NOT NULL
        );
        
        CREATE TABLE Pengajar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_pengajar TEXT UNIQUE NOT NULL,
            nama_pengajar TEXT NOT NULL,
            program TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES User(id)
        );
        
        CREATE TABLE Siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_siswa TEXT NOT NULL,
            kelas_tingkat TEXT NOT NULL,
            program TEXT NOT NULL,
            sekolah_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (sekolah_id) REFERENCES Sekolah(id),
            FOREIGN KEY (user_id) REFERENCES User(id)
        );
        
        CREATE TABLE Program (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_program TEXT NOT NULL
        );
        
        CREATE TABLE Kelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_kelas TEXT NOT NULL UNIQUE,
            nama_kelas TEXT NOT NULL,
            program_id INTEGER,
            sekolah_id INTEGER,
            pengajar_id INTEGER,
            waktu_mulai TEXT NOT NULL,
            waktu_akhir TEXT NOT NULL,
            hari TEXT NOT NULL,
            tanggal_mulai TEXT NOT NULL,
            FOREIGN KEY (program_id) REFERENCES Program(id),
            FOREIGN KEY (sekolah_id) REFERENCES Sekolah(id),
            FOREIGN KEY (pengajar_id) REFERENCES Pengajar(id)
        );
        
        CREATE TABLE KelasSiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kelas_id INTEGER,
            siswa_id INTEGER,
            FOREIGN KEY (kelas_id) REFERENCES Kelas(id),
            FOREIGN KEY (siswa_id) REFERENCES Siswa(id),
            UNIQUE(kelas_id, siswa_id)
        );
        
        CREATE TABLE Materi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program TEXT NOT NULL,
            pertemuan_ke INTEGER NOT NULL,
            detail_materi TEXT NOT NULL
        );

        CREATE TABLE AbsensiSesi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kelas_id INTEGER,
            tanggal TEXT NOT NULL,
            pengajar_id INTEGER,
            pengajar_pengganti_id INTEGER,
            foto_selfie TEXT NOT NULL,
            materi_pembelajaran TEXT,
            capaian_pembelajaran TEXT,
            FOREIGN KEY (kelas_id) REFERENCES Kelas(id),
            FOREIGN KEY (pengajar_id) REFERENCES Pengajar(id),
            FOREIGN KEY (pengajar_pengganti_id) REFERENCES Pengajar(id)
        );

        CREATE TABLE AbsensiSiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sesi_id INTEGER,
            siswa_id INTEGER,
            kehadiran_mutu TEXT,
            kehadiran TEXT,
            kedisiplinan_mutu TEXT,
            kedisiplinan TEXT,
            materi_kreativitas_mutu TEXT,
            materi_kreativitas TEXT,
            kerjasama_mutu TEXT,
            kerjasama TEXT,
            FOREIGN KEY (sesi_id) REFERENCES AbsensiSesi(id),
            FOREIGN KEY (siswa_id) REFERENCES Siswa(id)
        );

        CREATE TABLE Gaji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pengajar_id INTEGER NOT NULL,
            periode TEXT NOT NULL, -- Format: YYYY-MM
            transport_pengajaran INTEGER,
            tunjangan_marketing INTEGER,
            tunjangan_tugas_tambahan INTEGER,
            tunjangan_lain_lain INTEGER,
            total_gaji INTEGER,
            tanggal_dibuat TEXT NOT NULL,
            FOREIGN KEY (pengajar_id) REFERENCES Pengajar(id)
        );

        CREATE TABLE PasswordResetTokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES User(id)
        );
    ''')
    print("Skema database baru berhasil dibuat.")
    
    # --- SAMPLE DATA LENGKAP ---
    
    # 1. User Admin
    admin_password = generate_password_hash('admin123')
    cursor.execute("INSERT INTO User (username, password, role) VALUES (?, ?, ?)", ('admin', admin_password, 'admin'))
    
    # 2. Sekolah Mitra
    schools = [
        ('S-FI', 'SD Fitrah Insani', 'Depok', 'Muslim'), 
        ('S-XA', 'SD Xaverius 1', 'Jakarta', 'Non Muslim'),
        ('S-AZ', 'SD Al Azhar 50', 'Bogor', 'Muslim'),
        ('S-PB', 'SD Permata Bunda', 'Tangerang', 'Non Muslim')
    ]
    cursor.executemany("INSERT INTO Sekolah (kode_sekolah, nama_sekolah, alamat, jenis_sekolah) VALUES (?, ?, ?, ?)", schools)
    
    # 3. Program
    programs = [('Robotik',), ('Bahasa Inggris',), ('Desain Grafis',)]
    cursor.executemany("INSERT INTO Program (nama_program) VALUES (?)", programs)
    
    # 4. Pengajar
    teachers_data = [
        ('iwan', 'P-RB01', 'Dr. Iwan Purwanto, S.Kom, MTI', 'Robotik'),
        ('adit', 'P-EN01', 'Adhitya Barkah, M.M.', 'Bahasa Inggris'),
        ('anung', 'P-DG01', 'Anung B. Ariwibowo, M.Kom', 'Desain Grafis')
    ]
    for username, kode, nama, program in teachers_data:
        hashed_password = generate_password_hash('teacher123')
        cursor.execute("INSERT INTO User (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, 'pengajar'))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO Pengajar (kode_pengajar, nama_pengajar, program, user_id) VALUES (?, ?, ?, ?)", (kode, nama, program, user_id))
    
    # 5. Siswa (Total 10)
    students_data = [
        ('dewanto', 'Dewanto', '4 SD', 'Robotik', 1),
        ('felix', 'Felix', '5 SD', 'Robotik', 2),
        ('rayyan', 'Rayyan', '4 SD', 'Robotik', 1),
        ('imam', 'Imam', '5 SD', 'Bahasa Inggris', 3),
        ('bayu', 'Bayu', '5 SD', 'Bahasa Inggris', 3),
        ('vira', 'Vira', '4 SD', 'Bahasa Inggris', 4),
        ('bambang', 'Bambang', '4 SD', 'Bahasa Inggris', 2),
        ('faiz', 'Faiz', '5 SD', 'Desain Grafis', 1),
        ('rombon', 'Rombon', '5 SD', 'Desain Grafis', 4),
        ('sarah', 'Sarah', '4 SD', 'Desain Grafis', 3)
    ]
    for username, nama, kelas_tingkat, program, sekolah_id in students_data:
        hashed_password = generate_password_hash('student123')
        cursor.execute("INSERT INTO User (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, 'siswa'))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO Siswa (nama_siswa, kelas_tingkat, program, sekolah_id, user_id) VALUES (?, ?, ?, ?, ?)", (nama, kelas_tingkat, program, sekolah_id, user_id))

    # 6. Kelas
    classes_data = [
        ('RB-FI-PAGI', 'Robotik Pagi Fitrah Insani', 1, 1, 1, 'Rabu', '09:00', '10:30', '2025-07-01'),
        ('EN-XA-SORE', 'English Sore Xaverius', 2, 2, 2, 'Selasa', '15:00', '16:30', '2025-07-01'),
        ('DG-AZ-SIANG', 'Desain Grafis Siang Al Azhar', 3, 3, 3, 'Jumat', '13:00', '14:30', '2025-07-01')
    ]
    cursor.executemany("INSERT INTO Kelas (kode_kelas, nama_kelas, program_id, sekolah_id, pengajar_id, hari, waktu_mulai, waktu_akhir, tanggal_mulai) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", classes_data)
    
    # 7. Penugasan Siswa ke Kelas
    class_student_assignments = [
        (1, 1), (1, 2), (1, 3), # Siswa 1,2,3 di Kelas Robotik
        (2, 4), (2, 5), (2, 6), (2, 7), # Siswa 4,5,6,7 di Kelas English
        (3, 8), (3, 9), (3, 10) # Siswa 8,9,10 di Kelas Desain
    ]
    cursor.executemany("INSERT INTO KelasSiswa (kelas_id, siswa_id) VALUES (?, ?)", class_student_assignments)

    # 8. Data Materi
    materi_data = [
        ('Robotik', 1, 'Pengenalan komponen dasar dan perakitan.'),
        ('Robotik', 2, 'Logika pemrograman dasar: maju, mundur, belok.'),
        ('Bahasa Inggris', 1, 'Introduction and Greetings.'),
        ('Bahasa Inggris', 2, 'Vocabulary: Things in the Classroom.'),
        ('Desain Grafis', 1, 'Pengenalan warna primer dan sekunder.'),
        ('Desain Grafis', 2, 'Menggambar bentuk dasar: kotak, lingkaran, segitiga.')
    ]
    cursor.executemany("INSERT INTO Materi (program, pertemuan_ke, detail_materi) VALUES (?, ?, ?)", materi_data)

    # 9. Data Absensi (untuk 2 sesi di kelas Robotik)
    sesi_robotik_1 = (1, '2025-07-02', 1, 'placeholder.jpg', 'Pengenalan Robotika', 'Siswa berhasil merakit robot dasar.')
    cursor.execute('INSERT INTO AbsensiSesi (kelas_id, tanggal, pengajar_id, foto_selfie, materi_pembelajaran, capaian_pembelajaran) VALUES (?, ?, ?, ?, ?, ?)', sesi_robotik_1)
    sesi_1_id = cursor.lastrowid
    penilaian_sesi_1 = [
        (sesi_1_id, 1, 'A', 'Hadir', 'A', 'Tepat waktu', 'B', 'Cukup kreatif', 'A', 'Memimpin kelompok'),
        (sesi_1_id, 2, 'A', 'Hadir', 'B', 'Sedikit ramai', 'A', 'Sangat kreatif', 'B', 'Bekerjasama'),
        (sesi_1_id, 3, 'C', 'Absen', '-', '-', '-', '-', '-', '-')
    ]
    cursor.executemany('INSERT INTO AbsensiSiswa (sesi_id, siswa_id, kehadiran_mutu, kehadiran, kedisiplinan_mutu, kedisiplinan, materi_kreativitas_mutu, materi_kreativitas, kerjasama_mutu, kerjasama) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', penilaian_sesi_1)

    sesi_robotik_2 = (1, '2025-07-09', 1, 'placeholder.jpg', 'Dasar Pergerakan', 'Siswa berhasil memprogram robot untuk bergerak.')
    cursor.execute('INSERT INTO AbsensiSesi (kelas_id, tanggal, pengajar_id, foto_selfie, materi_pembelajaran, capaian_pembelajaran) VALUES (?, ?, ?, ?, ?, ?)', sesi_robotik_2)
    sesi_2_id = cursor.lastrowid
    penilaian_sesi_2 = [
        (sesi_2_id, 1, 'A', 'Hadir', 'A', 'Sangat baik', 'A', 'Sangat baik', 'A', 'Sangat baik'),
        (sesi_2_id, 2, 'A', 'Hadir', 'A', 'Sangat baik', 'A', 'Sangat baik', 'A', 'Sangat baik'),
        (sesi_2_id, 3, 'A', 'Hadir', 'A', 'Sangat baik', 'A', 'Sangat baik', 'A', 'Sangat baik')
    ]
    cursor.executemany('INSERT INTO AbsensiSiswa (sesi_id, siswa_id, kehadiran_mutu, kehadiran, kedisiplinan_mutu, kedisiplinan, materi_kreativitas_mutu, materi_kreativitas, kerjasama_mutu, kerjasama) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', penilaian_sesi_2)
    
    # 10. Data Gaji (Contoh untuk 1 pengajar)
    cursor.execute("INSERT INTO Gaji (pengajar_id, periode, transport_pengajaran, total_gaji, tanggal_dibuat) VALUES (?, ?, ?, ?, ?)",
                   (1, '2025-07', 200000, 2500000, '2025-07-28'))

    conn.commit()
    conn.close()
    
    print("Data dummy lengkap berhasil dimasukkan.")
    print("\nSample login credentials:")
    print("Admin: username='admin', password='admin123'")
    print("Teachers: username='iwan', 'adit', 'anung'. Password='teacher123'")
    print("Students: username='dewanto', 'felix', 'rayyan', dll. Password='student123'")

if __name__ == '__main__':
    init_database()