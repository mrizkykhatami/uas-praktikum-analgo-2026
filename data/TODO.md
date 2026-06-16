# TODO: data/

## Gambaran Besar
Folder `data/` menyimpan input utama simulasi:
- `locations.json` untuk detail Hub + pelanggan, paket, dan matriks jarak.
- `scenario.json` untuk parameter ekonomi (harga BBM), kendaraan, dan biaya komputasi.

## Deskripsi
1. Buat `locations.json` dengan:
   - metadata proyek
   - daftar lokasi (`hub` + `pelanggan`)
   - paket pengiriman dengan `tujuan_id` dan `berat_kg`
   - matriks jarak `adjacency_matrix.matrix`
   - label lokasi yang konsisten
2. Buat `scenario.json` dengan:
   - skenario `subsidi` dan `krisis`
   - harga BBM per liter untuk tiap skenario
   - parameter kendaraan (kapasitas, rasio konsumsi penuh/kosong)
   - parameter biaya komputasi (`biaya_per_milidetik`)
3. Pastikan data siap dibaca dari `src/` dan dipakai oleh perhitungan TCO.
4. (Opsional) Bisa tambahkan skenario tambahan untuk analisis lebih lanjut.

## Catatan
- Pastikan struktur file JSON valid.
- Data harus konsisten.
- Jaga agar jarak dan berat realistis untuk studi kasus Bandung/last-mile delivery.