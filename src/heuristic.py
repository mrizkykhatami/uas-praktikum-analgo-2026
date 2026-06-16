"""
heuristic.py
Algoritma A: Greedy Nearest Neighbor (Heuristik)

Strategi: Dari Hub, selalu pilih pelanggan terdekat yang belum
dikunjungi. Ulangi hingga semua pelanggan dikunjungi, lalu kembali
ke Hub.

Kompleksitas Waktu : O(n^2)
  - Loop luar  : n iterasi (jumlah pelanggan)
  - Loop dalam : maks n-1 perbandingan (cari minimum)
  - Total perbandingan: n*(n-1)/2 -> O(n^2)

Kompleksitas Ruang : O(n)
  - visited[] dan rute[] masing-masing berukuran n
"""

import time
from graph import Graph


def greedy_nearest_neighbor(graph: Graph) -> dict:
    """
    Jalankan algoritma Greedy Nearest Neighbor pada graf

    Parameter:
        graph : objek Graph yang sudah di-load

    Return:
        dict berisi:
          - rute          : list index simpul (diawali & diakhiri Hub)
          - total_jarak   : float (km)
          - waktu_ms      : float (milidetik)
          - urutan_nama   : list nama simpul sesuai rute
    """

    # Catat waktu mulai 
    waktu_mulai = time.perf_counter()

    n_pelanggan = graph.n - 1          # jumlah pelanggan (tanpa Hub)
    hub         = graph.hub_index      # index Hub (0)
    dikunjungi  = [False] * graph.n    # status kunjungan tiap simpul

    rute        = [hub]                # rute dimulai dari Hub
    posisi_saat_ini = hub
    dikunjungi[hub] = True

    # Kunjungi semua pelanggan
    for _ in range(n_pelanggan):
        jarak_terdekat = float('inf')
        simpul_terdekat = -1

        # Cari pelanggan terdekat yang belum dikunjungi
        for j in range(graph.n):
            if not dikunjungi[j]:
                jarak_ke_j = graph.jarak(posisi_saat_ini, j)
                if jarak_ke_j < jarak_terdekat:
                    jarak_terdekat  = jarak_ke_j
                    simpul_terdekat = j

        # Kunjungi simpul terdekat
        dikunjungi[simpul_terdekat] = True
        rute.append(simpul_terdekat)
        posisi_saat_ini = simpul_terdekat

    # Kembali ke Hub
    rute.append(hub)

    # Catat waktu selesai
    waktu_selesai = time.perf_counter()
    waktu_ms = (waktu_selesai - waktu_mulai) * 1000

    total_jarak  = graph.hitung_total_jarak(rute)
    urutan_nama  = [graph.labels[i] for i in rute]

    return {
        'algoritma'   : 'Greedy Nearest Neighbor',
        'rute'        : rute,
        'urutan_nama' : urutan_nama,
        'total_jarak' : total_jarak,
        'waktu_ms'    : waktu_ms,
    }
