# TODO: src/

## Gambaran Besar
Folder `src/` menyimpan semua logika dan implementasi algoritma simulasi rute, mulai dari pembacaan data hingga perhitungan TCO dan output terminal.

## Deskripsi
1. Buat `src/main.py`:
   - entry point CLI
   - load data dari `data/locations.json` dan `data/scenario.json`
   - jalankan kedua algoritma untuk tiap skenario
   - tampilkan ringkasan hasil, detail segmen, dan perbandingan TCO
2. Buat `src/graph.py`:
   - kelas `Graph` untuk lokasi, paket, dan matriks jarak
   - fungsi bantu untuk total berat paket, jarak antar node, dan nama lokasi
3. Buat `src/heuristic.py`:
   - implementasi Greedy Nearest Neighbor
   - pilih lokasi terdekat yang belum dikunjungi sampai semua selesai
4. Buat `src/exact.py`:
   - implementasi Backtracking DFS dengan pruning
   - rekam rute optimal, total jarak, waktu, dan node yang dikunjungi
5. Buat `src/cost.py`:
   - fungsi baca skenario
   - hitung biaya BBM dan biaya komputasi
   - hasilkan TCO dan detail biaya per segmen
6. Tambahkan dukungan fitur:
   - opsi `--scenario subsidi|krisis|all`
   - perbandingan algoritma Greedy vs Exact
   - output yang mudah dibaca di terminal

## Catatan
- Gunakan Greedy Nearest Neighbor untuk heuristic dan Backtracking DFS dengan pruning untuk exact
- Pastikan output menampilkan semua data penting seperti waktu eksekusi presisi untuk kedua algoritma, urutan rute, dan komparasi nilai TCO dari kedua skenario
- Jaga agar struktur kode tetap modular.