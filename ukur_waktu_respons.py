"""
Skrip Pengukuran Waktu Respons - Sistem Prediksi Minat Beli
=============================================================
Skrip ini mengukur waktu respons endpoint prediksi pada aplikasi Flask
dengan mengirim beberapa request berturut-turut dan menghitung statistik
waktu respons (rata-rata, minimum, maksimum, median).

CARA PAKAI:
1. Pastikan aplikasi Flask kalian sudah berjalan (python app.py)
2. Sesuaikan variabel di bagian "KONFIGURASI" di bawah jika diperlukan
3. Jalankan: pip install requests  (jika belum ada)
4. Jalankan: python ukur_waktu_respons.py
"""

import time
import statistics
import requests
import csv

# ============================================================
# KONFIGURASI - SESUAIKAN DENGAN APLIKASI FLASK KALIAN
# ============================================================

# Alamat endpoint prediksi. Sesuai app.py Anda, Flask berjalan di port 5001
# dan route prediksi bernama "/api/predict"
URL = "http://127.0.0.1:5001/api/predict"

# Contoh data input sesuai field yang ada di form Prediksi kalian.
# Kolom "CustomerGender" menggunakan integer (0: Laki-laki, 1: Perempuan)
PAYLOAD = {
    "ProductCategory": "Smartphones",
    "ProductBrand": "Samsung",
    "ProductPrice": 1500.0,
    "CustomerAge": 35,
    "CustomerGender": 0,  # 0 untuk Laki-laki, 1 untuk Perempuan
    "PurchaseFrequency": 8,
    "CustomerSatisfaction": 4,
}

# Jumlah percobaan yang akan dilakukan
JUMLAH_PERCOBAAN = 30

# Nama file untuk menyimpan hasil detail (opsional, untuk lampiran/bukti)
OUTPUT_CSV = "hasil_waktu_respons.csv"

# ============================================================
# PROSES PENGUKURAN - TIDAK PERLU DIUBAH
# ============================================================

def ukur_satu_request():
    """Mengirim satu request JSON dan mengembalikan waktu respons dalam milidetik."""
    mulai = time.perf_counter()
    try:
        # Menggunakan json=PAYLOAD karena app.py Anda memproses data dengan request.get_json()
        response = requests.post(URL, json=PAYLOAD, timeout=10)
        status_ok = response.status_code == 200
        if not status_ok:
            print(f"  [Gagal] Status code: {response.status_code}, Respon: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"  Gagal request: {e}")
        return None, False
    selesai = time.perf_counter()
    durasi_ms = (selesai - mulai) * 1000
    return durasi_ms, status_ok


def main():
    print(f"Memulai pengukuran waktu respons ke {URL}")
    print(f"Jumlah percobaan: {JUMLAH_PERCOBAAN}\n")

    hasil = []
    gagal = 0

    for i in range(1, JUMLAH_PERCOBAAN + 1):
        durasi, sukses = ukur_satu_request()
        if durasi is None:
            gagal += 1
            continue
        status_txt = "OK" if sukses else "GAGAL (bukan status 200)"
        if sukses:
            print(f"Percobaan {i:2d}: {durasi:7.2f} ms  [{status_txt}]")
            hasil.append(durasi)
        else:
            gagal += 1

    if not hasil:
        print("\nTidak ada request yang berhasil. Periksa apakah Flask sudah berjalan di port 5001 dan siap menerima request.")
        return

    print("\n" + "=" * 50)
    print("RINGKASAN HASIL PENGUKURAN")
    print("=" * 50)
    print(f"Jumlah request berhasil : {len(hasil)} dari {JUMLAH_PERCOBAAN}")
    print(f"Jumlah request gagal    : {gagal}")
    print(f"Rata-rata waktu respons : {statistics.mean(hasil):.2f} ms")
    print(f"Median waktu respons    : {statistics.median(hasil):.2f} ms")
    print(f"Waktu tercepat          : {min(hasil):.2f} ms")
    print(f"Waktu terlambat         : {max(hasil):.2f} ms")
    if len(hasil) > 1:
        print(f"Standar deviasi         : {statistics.stdev(hasil):.2f} ms")

    # Simpan detail ke CSV agar bisa dilampirkan sebagai bukti pengujian
    try:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["percobaan_ke", "waktu_respons_ms"])
            for idx, durasi in enumerate(hasil, start=1):
                writer.writerow([idx, f"{durasi:.2f}"])
        print(f"\nDetail hasil disimpan di: {OUTPUT_CSV}")
    except IOError as e:
        print(f"\nGagal menulis file CSV: {e}")

    print("\nContoh kalimat untuk jurnal:")
    print(
        f'"Berdasarkan {len(hasil)} kali percobaan, sistem tercatat memiliki '
        f'rata-rata waktu respons sebesar {statistics.mean(hasil):.2f} milidetik, '
        f'dengan waktu tercepat {min(hasil):.2f} ms dan waktu terlambat '
        f'{max(hasil):.2f} ms."'
    )


if __name__ == "__main__":
    main()
