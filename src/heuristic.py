"""
heuristic.py
Algoritma A: Greedy Heuristik berdasarkan biaya BBM.

Strategi: Dari Hub, pilih pelanggan berikutnya berdasarkan estimasi
biaya BBM segmen saat ini dan dampak pengurangan beban. Ulangi hingga
semua pelanggan dikunjungi, lalu kembali ke Hub.

Kompleksitas Waktu : O(n^2)
  - Loop luar  : n iterasi (jumlah pelanggan)
  - Loop dalam : maks n-1 perbandingan (cari minimum)
  - Total perbandingan: n*(n-1)/2 -> O(n^2)

Kompleksitas Ruang : O(n)
  - visited[] dan rute[] masing-masing berukuran n
"""

import time
from graph import Graph
from cost import (
    KAPASITAS_MAX_DEFAULT,
    RASIO_PENUH_DEFAULT,
    RASIO_KOSONG_DEFAULT,
    hitung_rasio_konsumsi,
)


def _hitung_total_liter(graph: Graph, rute: list,
                        kapasitas_max: float,
                        rasio_penuh: float,
                        rasio_kosong: float) -> float:
    """Hitung total liter BBM untuk rute yang dibentuk greedy."""
    beban_saat_ini = graph.total_berat_semua_paket()
    total_liter = 0.0

    for i in range(len(rute) - 1):
        asal   = rute[i]
        tujuan = rute[i + 1]
        jarak  = graph.jarak(asal, tujuan)

        rasio = hitung_rasio_konsumsi(
            beban_kg      = beban_saat_ini,
            kapasitas_max = kapasitas_max,
            rasio_penuh   = rasio_penuh,
            rasio_kosong  = rasio_kosong,
        )

        total_liter += jarak * rasio

        if tujuan != graph.hub_index:
            beban_saat_ini = max(0.0, beban_saat_ini - graph.berat_paket(tujuan))

    return round(total_liter, 6)


def greedy_nearest_neighbor(
    graph: Graph,
    kapasitas_max: float = KAPASITAS_MAX_DEFAULT,
    rasio_penuh: float = RASIO_PENUH_DEFAULT,
    rasio_kosong: float = RASIO_KOSONG_DEFAULT,
) -> dict:
    """
    Jalankan heuristik Greedy berbasis estimasi biaya BBM pada graf.

    Parameter:
        graph          : objek Graph yang sudah di-load
        kapasitas_max  : kapasitas kendaraan (kg)
        rasio_penuh    : rasio konsumsi saat penuh (L/km)
        rasio_kosong   : rasio konsumsi saat kosong (L/km)

    Return:
        dict berisi:
          - rute          : list index simpul (diawali & diakhiri Hub)
          - total_jarak   : float (km)
          - total_liter   : float (liter)
          - waktu_ms      : float (milidetik)
          - urutan_nama   : list nama simpul sesuai rute
    """

    # Catat waktu mulai 
    waktu_mulai = time.perf_counter()

    n_pelanggan = graph.n - 1          # jumlah pelanggan (tanpa Hub)
    hub         = graph.hub_index      # index Hub
    dikunjungi  = [False] * graph.n    # status kunjungan tiap simpul

    rute        = [hub]                # rute dimulai dari Hub
    posisi_saat_ini = hub
    dikunjungi[hub] = True

    # Kunjungi semua pelanggan
    for _ in range(n_pelanggan):
        biaya_terendah = float('inf')
        simpul_terbaik = -1

        beban_saat_ini = graph.total_berat_semua_paket()
        for visited_idx in range(graph.n):
            if dikunjungi[visited_idx] and visited_idx != hub:
                beban_saat_ini -= graph.berat_paket(visited_idx)

        for j in range(graph.n):
            if not dikunjungi[j]:
                jarak_ke_j = graph.jarak(posisi_saat_ini, j)
                rasio = hitung_rasio_konsumsi(
                    beban_kg      = beban_saat_ini,
                    kapasitas_max = kapasitas_max,
                    rasio_penuh   = rasio_penuh,
                    rasio_kosong  = rasio_kosong,
                )
                biaya_sementara = jarak_ke_j * rasio

                if biaya_sementara < biaya_terendah:
                    biaya_terendah = biaya_sementara
                    simpul_terbaik = j

        dikunjungi[simpul_terbaik] = True
        rute.append(simpul_terbaik)
        posisi_saat_ini = simpul_terbaik

    # Kembali ke Hub
    rute.append(hub)

    # Catat waktu selesai
    waktu_selesai = time.perf_counter()
    waktu_ms = (waktu_selesai - waktu_mulai) * 1000

    total_jarak  = graph.hitung_total_jarak(rute)
    total_liter  = _hitung_total_liter(
        graph, rute,
        kapasitas_max,
        rasio_penuh,
        rasio_kosong,
    )
    urutan_nama  = [graph.labels[i] for i in rute]

    return {
        'algoritma'   : 'Greedy BBM Cost Heuristic',
        'rute'        : rute,
        'urutan_nama' : urutan_nama,
        'total_jarak' : total_jarak,
        'total_liter' : total_liter,
        'waktu_ms'    : waktu_ms,
    }
