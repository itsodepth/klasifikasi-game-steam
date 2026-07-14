# Klasifikasi Elektronik - Prediksi Minat Beli Pelanggan

Repository ini berisi aplikasi web berbasis **Flask** untuk memprediksi minat beli pelanggan terhadap produk elektronik konsumen berdasarkan beberapa parameter/fitur. Aplikasi menggunakan model Machine Learning **Decision Tree Classifier** yang dilatih menggunakan dataset penjualan barang elektronik.

---

## Prasyarat (Prerequisites)

Bagi pengguna awam yang baru pertama kali melakukan `git clone` repositori ini, berikut adalah hal-hal yang perlu disiapkan di komputer/laptop:

### 1. Python (Versi 3.8 s.d. 3.12 direkomendasikan)
Aplikasi ini dibangun menggunakan bahasa pemrograman Python. 
* **Download:** Kunjungi [python.org/downloads](https://www.python.org/downloads/) dan unduh versi terbaru untuk sistem operasi Anda.
* **PENTING saat Instalasi (Windows):** Pastikan untuk mencentang/memilih opsi **"Add Python to PATH"** di halaman awal installer sebelum menekan tombol *Install Now*. Ini agar perintah `python` dan `pip` dapat dikenali di Command Prompt (CMD)/PowerShell.

---

## Langkah-Langkah Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini secara berurutan:

### Langkah 1: Buka Terminal / Command Prompt
1. Buka aplikasi **Command Prompt (CMD)** atau **PowerShell** (di Windows) atau **Terminal** (di macOS/Linux).
2. Arahkan ke folder repositori hasil clone menggunakan perintah `cd`. Contoh:
   ```bash
   cd path/to/klasifikasi-elektronik
   ```

### Langkah 2: Membuat Virtual Environment (Sangat Direkomendasikan)
Virtual environment digunakan agar library/dependencies proyek ini terisolasi dan tidak mengganggu python global di laptop Anda.

* **Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

*Setelah aktif, Anda akan melihat tanda `(venv)` di sebelah kiri prompt terminal Anda.*

### Langkah 3: Menginstal Libraries / Dependencies
Instal semua pustaka pihak ketiga yang dibutuhkan oleh aplikasi (seperti Flask, Pandas, Scikit-Learn, dll.) dengan menjalankan perintah:
```bash
pip install -r requirements.txt
```
Tunggu hingga proses instalasi selesai.

### Langkah 4: Menjalankan Aplikasi Flask
Jalankan perintah berikut untuk memulai server aplikasi web:
```bash
python app.py
```
Setelah berjalan, terminal akan menampilkan pesan yang menyatakan server aktif, biasanya seperti ini:
`* Running on http://127.0.0.1:5001`

### Langkah 5: Membuka Aplikasi di Web Browser
1. Buka browser Anda (Google Chrome, Microsoft Edge, Mozilla Firefox, Safari, dll.).
2. Ketik atau kunjungi alamat berikut pada kolom URL:
   [http://127.0.0.1:5001](http://127.0.0.1:5001) atau [http://localhost:5001](http://localhost:5001)
3. Aplikasi web siap digunakan! Anda dapat memasukkan input pada form yang tersedia untuk melakukan klasifikasi/prediksi.

---

## Fitur Tambahan: Pengukuran Waktu Respons (Response Time Test)

Terdapat skrip opsional untuk mengukur performa/kecepatan respons dari API prediksi:
1. Pastikan aplikasi Flask utama Anda tetap berjalan di terminal pertama (`python app.py`).
2. Buka terminal baru, aktifkan kembali virtual environment (`venv\Scripts\activate` atau `source venv/bin/activate`).
3. Jalankan perintah:
   ```bash
   python ukur_waktu_respons.py
   ```
4. Hasil pengukuran waktu respons akan ditampilkan di terminal dan disimpan secara otomatis ke dalam file `hasil_waktu_respons.csv`.
