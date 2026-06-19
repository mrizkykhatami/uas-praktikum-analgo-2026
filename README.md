# UAS PRAKTIKUM ANALISIS ALGORITMA 2026

## Route Optimization: Last-Mile Delivery Simulation

Pipeline simulasi komputasi yang membandingkan algoritma **Heuristik (Greedy Nearest Neighbor)** vs **Eksak (Backtracking DFS with Pruning)** untuk penentuan rute kurir pengantaran (Last-Mile Delivery), ditinjau dari perspektif **Total Cost of Ownership (TCO)**.

Studi kasus: sebuah perusahaan ekspedisi lokal harus memutuskan apakah investasi pada algoritma eksak yang mahal secara komputasi (Cloud Server *Pay-as-you-go*) sepadan dengan penghematan bahan bakar (BBM) yang dihasilkannya, pada dua kondisi ekonomi yang berbeda.

**Region dataset**: Bandung Raya, Jawa Barat

---

## Anggota Tim

| NPM | Nama |
| --- | --- |
| 140810240029 | Hamzah Abdillah Gabriela |
| 140810240061 | Renadi Wilantara |
| 140810240069 | Zedka Yaswa Ahmadetya |
| 140810240073 | Muhammad Rizky Khatami |

**Mata Kuliah**: Analisis Algoritma - Praktikum

---

## 1. Cara Menjalankan Program

### Prasyarat
- **Python 3.8** atau lebih baru.
- `matplotlib` **opsional**, hanya dibutuhkan untuk membuat grafik perbandingan (`src/plot.py`).
```bash
# (opsional) hanya jika ingin membuat grafik perbandingan
pip install matplotlib
```

### Menjalankan Simulasi (CLI)

```bash
# Jalankan KEDUA skenario ekonomi sekaligus + analisis break-even (default)
python src/main.py

# Hanya skenario Subsidi (BBM Rp 5.000/liter)
python src/main.py --scenario subsidi

# Hanya skenario Krisis (BBM Rp 20.000/liter)
python src/main.py --scenario krisis

# Atur jumlah run untuk pengukuran waktu (median dari N run, default 5)
python src/main.py --repeat 9
```

> **Catatan pengukuran waktu.** Karena waktu eksekusi memengaruhi biaya komputasi, program mengukur waktu sebagai **median dari beberapa run** (`--repeat`, default 5) agar tahan terhadap *noise* penjadwalan OS.

### Menyimpan Output Terminal ke File

```bash
python src/main.py > docs/output_simulation.txt
```

### (Opsional) Membuat Grafik Perbandingan

```bash
python src/plot.py                 # tampilkan + simpan PNG
python src/plot.py --no-show       # hanya simpan PNG (untuk headless/CI)
python src/plot.py --out docs/perbandingan_algoritma.png
```

---

## 2. Struktur Repositori

```
uas-praktikum-analgo-2026/
├── src/                              # Source code utama (algoritma from scratch)
│   ├── main.py                       # Entry point CLI: pipeline simulasi & analisis break-even
│   ├── graph.py                      # Struktur data Graf berbobot (Adjacency Matrix)
│   ├── heuristic.py                  # Algoritma A: Greedy Nearest Neighbor
│   ├── exact.py                      # Algoritma B: Backtracking DFS with Pruning (Branch & Bound)
│   ├── cost.py                       # Cost function: rasio BBM dinamis, biaya komputasi, TCO
│   └── plot.py                       # Visualisasi grafik perbandingan (matplotlib)
├── data/                             # Input eksternal (.json)
│   ├── locations.json                # Lokasi Hub & pelanggan, paket, adjacency matrix 11x11
│   └── scenario.json                 # Parameter skenario ekonomi & kendaraan
├── docs/                             # Bukti eksekusi
│   ├── output_simulation.txt         # Hasil output terminal
│   ├── perbandingan_algoritma.png    # Grafik perbandingan 4 panel
│   ├── screenshot_subsidi.png        # SS output terminal skenario subsidi
│   └── screenshot_krisis.png         # SS output terminal skenario krisis
├── README.md                         # Dokumentasi ini
└── .gitignore                        # Mengabaikan __pycache__, dsb.
```

### Pemodelan Data (Graf Berbobot)

Dataset memetakan **1 Hub (Gudang Pusat Gedebage)** + **10 lokasi pelanggan nyata** di Bandung Raya ke dalam **Adjacency Matrix simetris 11×11**, di mana bobot tiap edge merepresentasikan jarak fisik (km). Total beban paket awal = **30,5 kg**.

| ID | Lokasi | Tipe | Berat Paket |
| --- | --- | --- | --- |
| 0 | Hub - Gudang Pusat Gedebage | hub | - |
| 1 | Alun-alun Bandung | pelanggan | 3,5 kg |
| 2 | Cihampelas Walk | pelanggan | 2,0 kg |
| 3 | Pasar Baru Bandung | pelanggan | 4,0 kg |
| 4 | Buah Batu | pelanggan | 1,5 kg |
| 5 | Cimahi | pelanggan | 5,0 kg |
| 6 | Ujungberung | pelanggan | 2,5 kg |
| 7 | Margahayu | pelanggan | 3,0 kg |
| 8 | Dago | pelanggan | 1,0 kg |
| 9 | Antapani | pelanggan | 2,0 kg |
| 10 | Sumedang | pelanggan | 6,0 kg |

Semua parameter lokasi, berat paket, matriks jarak, harga BBM, dan parameter kendaraan **dibaca dari file `.json` eksternal** ([data/locations.json](data/locations.json), [data/scenario.json](data/scenario.json)).

---

## 3. Pemilihan Algoritma (Trade-off)

### Algoritma A - Greedy Nearest Neighbor (Heuristik) → [src/heuristic.py](src/heuristic.py)

- **Cara kerja**: Mulai dari Hub, pada setiap langkah selalu pilih lokasi pelanggan **terdekat** (jarak minimum) yang belum dikunjungi. Ulangi sampai semua pelanggan terkunjungi, lalu kembali ke Hub.
- **Kelebihan**: Sangat cepat (orde mikro-milidetik) sehingga biaya komputasi cloud nyaris nol. Cocok untuk *real-time dispatching*.
- **Kekurangan**: **Tidak menjamin rute optimal**, keputusan lokal yang serakah dapat menjebak kurir ke jarak total yang lebih panjang (sub-optimal).
- **Alasan dipilih**: Karena kompleksitasnya relatif rendah sekitar O(n²) dan relevan dengan kebutuhan finansial bagi perusahaan. 

### Algoritma B - Backtracking DFS with Pruning / Branch & Bound (Eksak) → [src/exact.py](src/exact.py)

- **Cara kerja**: Eksplorasi rekursif (DFS) atas seluruh ruang permutasi rute. Dua mekanisme pruning memangkas cabang yang tidak mungkin lebih baik:
  1. **Bound monoton**: konsumsi BBM akumulatif hanya bisa naik, sehingga begitu sebuah cabang sudah melampaui solusi terbaik saat ini, cabang itu langsung dibuang.
  2. **Upper bound awal dari Greedy**: solusi Greedy dipakai sebagai batas atas awal sehingga *pruning sudah agresif sejak node pertama* (Branch & Bound).
- **Catatan penting (optimasi BIAYA, bukan jarak)**: Karena rasio konsumsi BBM berubah mengikuti beban, **rute terpendek belum tentu yang termurah**. Maka Algoritma B mengoptimalkan **total liter BBM** secara langsung, dengan beban dilacak sepanjang rekursi. Inilah sebabnya rute eksak (104,10 km) berbeda dari sekadar rute jarak-terpendek.
- **Kelebihan**: Menjamin rute dengan **biaya BBM minimum** (optimal absolut terhadap metrik biaya).
- **Kekurangan**: Worst-case eksponensial **O(n!)** - waktu komputasi melonjak, menyebabkan biaya cloud *Pay-as-you-go* mahal.
- **Alasan dipilih**: Karena agar bisa menentukan rute yang memiliki biaya paling opimal

---

## 4. Simulasi Fungsi Biaya (Cost Function)

Implementasi pada [src/cost.py](src/cost.py).

### a. Rasio Konsumsi BBM Dinamis

Beban paket memengaruhi efisiensi bensin: motor yang penuh lebih boros. Beban berkurang setiap kali kurir mengantar paket ke pelanggan. Rasio dihitung dengan **interpolasi linear**:

```
rasio(L/km) = (beban_saat_ini / kapasitas_max) × (rasio_penuh − rasio_kosong) + rasio_kosong
```

dengan parameter dari [data/scenario.json](data/scenario.json):
- `rasio_penuh`  = **0,05 L/km** (saat beban penuh)
- `rasio_kosong` = **0,02 L/km** (saat beban kosong)
- `kapasitas_max` = **30,0 kg**

> **Catatan:** `kapasitas_max` di sini adalah **nilai nominal acuan** untuk menghitung rasio konsumsi BBM (titik "100% penuh"), bukan batas muatan fisik motor. Karena itu total beban awal (30,5 kg) boleh sedikit melebihi nilai ini pada segmen pertama proporsi beban di-*clamp* ke maksimal 1,0 (lihat [src/cost.py](src/cost.py)), sehingga motor dihitung tepat seperti kondisi penuh.

### b. Biaya BBM Rute

```
Biaya BBM = Σ ( Jarak_AB × RasioKonsumsi(beban) × HargaBensin )
```

Beban dievaluasi **sebelum** tiba di tiap stop; setelah paket diturunkan, beban berkurang untuk segmen berikutnya.

### c. Biaya Komputasi Server

```
Biaya Komputasi = WaktuEksekusi(ms) × Rp 50/ms
```

### d. Total Cost of Ownership (TCO)

```
TCO = Biaya BBM + Biaya Komputasi
```

---

## 5. Analisis Kompleksitas (Big-O)

| Aspek | Algoritma A (Greedy) | Algoritma B (Backtracking + Pruning) |
| --- | --- | --- |
| **Waktu** | **O(n²)** | **O(n!)** worst-case (dipangkas pruning) |
| **Ruang** | **O(n)** | **O(n)** (kedalaman stack rekursi) |
| **Optimality** | Tidak dijamin | Dijamin optimal (terhadap biaya BBM) |

### Derivasi Waktu - Greedy `O(n²)`
Terdapat loop luar sebanyak `n − 1` iterasi (memilih satu pelanggan tiap iterasi). Di dalamnya, loop dalam memindai hingga `n` kandidat untuk mencari yang terdekat. Total operasi ≈ `(n−1) × n` → **O(n²)**. Lihat *nested loop* pada [src/heuristic.py](src/heuristic.py) (`for _ in range(graph.n - 1)` → `for j in range(graph.n)`).

### Derivasi Waktu - Backtracking `O(n!)`
DFS membangun rute dengan memilih simpul berikutnya dari simpul yang tersisa: pada level pertama ada `n−1` pilihan, level berikutnya `n−2`, dan seterusnya → `(n−1)!` permutasi pada worst-case → **O(n!)**. Pruning (bound monoton + upper bound Greedy) memangkas sebagian besar cabang dalam praktik, **tetapi batas atas teoritis tetap O(n!)**. Lihat rekursi `_dfs` pada [src/exact.py](src/exact.py).

### Derivasi Ruang
- **Greedy**: array `dikunjungi` dan `rute` masing-masing berukuran `n` → **O(n)**.
- **Backtracking**: kedalaman rekursi maksimum = panjang rute = `n`, ditambah array status berukuran `n` → **O(n)**.

---

## 6. Eksekusi Skenario Ekonomi & Hasil Simulasi

Kedua algoritma dijalankan pada dua skenario, sesuai output di [docs/output_simulation.txt](docs/output_simulation.txt) dan grafik [docs/perbandingan_algoritma.png](docs/perbandingan_algoritma.png).

### Rute yang Dihasilkan

| Algoritma | Rute | Jarak | BBM |
| --- | --- | --- | --- |
| **Greedy** | Hub → Buah Batu → Antapani → Ujungberung → Alun-alun → Pasar Baru → Cihampelas → Dago → Cimahi → Margahayu → Sumedang → Hub | **123,80 km** | 3,8647 L |
| **Backtracking** | Hub → Buah Batu → Alun-alun → Pasar Baru → Cihampelas → Dago → Cimahi → Margahayu → Antapani → Ujungberung → Sumedang → Hub | **104,10 km** | 3,1726 L |

Algoritma eksak menemukan rute **19,70 km lebih pendek** dan menghemat **≈ 0,69 liter** BBM per trip.

### Tabel TCO per Skenario

| Skenario | Algoritma | Jarak | Biaya BBM | Biaya Komputasi | **TCO** | Rekomendasi |
| --- | --- | --- | --- | --- | --- | :---: |
| **Subsidi**<br>(Rp 5.000/L) | Greedy | 123,80 km | Rp 19.323,75 | Rp 0,50 | **Rp 19.324,25** | ✅ |
| | Backtracking | 104,10 km | Rp 15.862,75 | Rp 50.566,25 | Rp 66.429,00 | |
| **Krisis**<br>(Rp 20.000/L) | Greedy | 123,80 km | Rp 77.295,00 | Rp 0,50 | **Rp 77.295,50** | ✅ |
| | Backtracking | 104,10 km | Rp 63.451,00 | Rp 50.566,25 | Rp 114.017,25 | |

> Pada **kedua** skenario realistis, **Greedy unggul** secara TCO. Biaya komputasi eksak (≈ Rp 50.566) jauh melebihi penghematan BBM yang diperolehnya (Rp 3.461 di subsidi; Rp 13.844 di krisis).

*Catatan: angka waktu eksekusi (dan karenanya biaya komputasi) bersifat dependent pada mesin; nilai di atas berasal dari satu sesi run dan dapat sedikit berbeda di mesin Anda. Tren dan kesimpulan tetap konsisten.*

---

## 7. Summary - Keputusan Bisnis & Titik Break-Even

### Titik Break-Even: **≈ Rp 73.061 / liter**

Karena `TCO = total_liter × harga_BBM + biaya_komputasi` bersifat **linear terhadap harga BBM**, titik impas dihitung secara tertutup:

```
Harga_impas = (Biaya_komputasi_eksak − Biaya_komputasi_greedy) / (Liter_greedy − Liter_eksak)
            = Rp 50.565,75 / 0,6921 liter
            ≈ Rp 73.061 / liter
```

### Tabel Sensitivitas TCO terhadap Harga BBM

| Harga/Liter | TCO Heuristik | TCO Eksak | Unggul |
| ---: | ---: | ---: | :--- |
| Rp 5.000 | Rp 19.324 | Rp 66.429 | Heuristik |
| Rp 20.000 | Rp 77.294 | Rp 114.018 | Heuristik |
| Rp 50.000 | Rp 193.236 | Rp 209.196 | Heuristik |
| **Rp 73.061** | **Rp 282.359** | **Rp 282.360** | **≈ Impas** |
| Rp 83.061 | Rp 321.006 | Rp 314.086 | **Eksak** |
| Rp 100.000 | Rp 386.470 | Rp 367.826 | **Eksak** |

### Kesimpulan Bisnis Final

Dalam konteks bisnis pengiriman **last-mile real-time**, **algoritma Greedy (Heuristik) direkomendasikan pada kedua kondisi ekonomi yang realistis** - baik saat BBM disubsidi (Rp 5.000/L) maupun saat krisis (Rp 20.000/L). Penghematan jarak/BBM dari algoritma eksak **tidak cukup** menutup biaya komputasi cloud yang berat secara eksponensial.

Algoritma **Eksak baru menguntungkan jika harga BBM menembus ≈ Rp 73.061/liter** - sebuah angka yang **jauh di atas skenario krisis sekalipun** (3,6× lipat). Dengan kata lain, pada parameter biaya komputasi saat ini (Rp 50/ms), investasi pada algoritma eksak **belum masuk akal secara finansial** untuk operasi rutin.

**Rekomendasi praktis**: gunakan **Greedy sebagai baseline produksi** (respons instan, biaya cloud ≈ nol). Algoritma eksak hanya layak dipertimbangkan jika salah satu kondisi terpenuhi:
- Harga komputasi cloud turun drastis (jauh < Rp 50/ms), **atau**
- Harga BBM riil melampaui titik break-even (Rp 73.061/L), **atau**
- Jumlah titik pengiriman sangat kecil (n ≤ 8) sehingga waktu eksekusi eksponensial tetap terkendali - cocok untuk *perencanaan rute offline* dengan *time budget* longgar.

---
