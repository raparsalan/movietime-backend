# MovieTime App Backend Services

## Deskripsi
API berbasis Flask untuk aplikasi MovieTime. API ini berfungsi sebagai backend untuk media integrasi model rekomendasi deeplearning untuk rekomendasi film dan komunikasi dengan database Aplikasi MovieTime. API ini juga mencakup dokumentasi API Swagger untuk pengujian dan interaksi dengan API secara mudah.

---

## Prasyarat

Pastikan Python versi 3.x terinstal di sistem Anda. Anda bisa memeriksa apakah Python sudah terinstal dengan menjalankan perintah:

```bash
python --version
```

## Instalasi Dependensi
### Clone repositori
Pertama, clone repositori ke mesin lokal Anda:
```bash
git clone https://github.com/username-anda/nama-repositori-anda.git
cd nama-repositori-anda
```

### Buat lingkungan virtual ( Opsional )
Disarankan untuk membuat lingkungan virtual untuk mengelola dependensi. Jalankan perintah berikut:
```bash
python -m venv venv
```

### Aktifkan lingkungan virtual
Aktifkan lingkungan virtual:  
Di Windows : 
```bash
.\venv\Scripts\activate
```
Di MacOs
```bash
source venv/bin/activate
```

### Instal dependensi yang dibutuhkan
Instal dependensi yang tercantum dalam file requirements.txt dengan menjalankan:
```bash
pip install -r requirements.txt
```

## Menjalankan Flask API
### Jalankan server
Setelah dependensi terinstal, Anda bisa menjalankan server Flask dengan perintah berikut:
```bash
python app.py
```
Server Flask akan dimulai, dan Anda akan melihat output seperti ini:
```bash
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

### Akses API
Anda sekarang dapat mengakses API dengan membuka alamat berikut di browser:
```bash
http://127.0.0.1:5000/
```

## Mengakses Dokumentasi API dengan Swagger
### Buka Dokumentasi API Swagger
Setelah server berjalan, buka browser Anda dan pergi ke:
```bash
http://127.0.0.1:5000/apidocs
```
Anda akan diarahkan ke Swagger UI, tempat Anda dapat melihat dan berinteraksi dengan endpoint API.
