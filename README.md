# 🗳️ Voting Online LAN Berbasis Web
### Tugas Besar Jaringan Komputer

Sistem **Voting Online LAN** adalah aplikasi berbasis web yang dirancang untuk melakukan proses voting secara **aman, sederhana, dan real-time** di lingkungan **jaringan lokal (LAN)**.  
Aplikasi ini dikembangkan sebagai **tugas besar mata kuliah Jaringan Komputer** untuk memahami konsep **client-server, autentikasi, database, dan komunikasi jaringan**.

---

## 👩‍🎓 Identitas Pengembang
- **Nama** : Al Yasmin Assa'diyah  
- **NPM** : 714240014  
- **Program Studi** : D4 Teknik Informatika  
- **Mata Kuliah** : Jaringan Komputer  

---

## 🎯 Tujuan Aplikasi
- Menerapkan konsep **client–server berbasis TCP/IP**
- Membangun sistem **voting satu kali per user**
- Mengimplementasikan **autentikasi user & admin**
- Menyimpan data secara permanen menggunakan **database**
- Menampilkan hasil voting secara **real-time**

---

## 🛠️ Teknologi yang Digunakan
- **Backend** : Python (Flask)
- **Frontend** : HTML, CSS, Chart.js
- **Database** : SQLite
- **Keamanan** : Hash password (Werkzeug)
- **Jaringan** : Local Area Network (LAN)

---

## ✨ Fitur Utama

### 👤 User
- Registrasi akun (nama, NPM, jurusan, username, password)
- Login menggunakan username & password
- Voting **hanya satu kali**
- Melihat hasil voting

### 👑 Admin
- Login admin
- Dashboard monitoring hasil voting
- Grafik voting **real-time**
- Export hasil voting ke CSV
- Reset hasil voting

---

## 🔐 Keamanan Sistem
- Password disimpan dalam bentuk **hash**
- Pembatasan hak akses menggunakan **role-based access**
- Status voting user disimpan di database (`has_voted`)
- User tidak dapat melakukan voting lebih dari satu kali

---

## 📊 Grafik Voting Real-Time
Aplikasi menampilkan grafik hasil voting secara real-time menggunakan **Chart.js**,  
yang diperbarui secara berkala melalui API Flask tanpa perlu refresh halaman.

---


