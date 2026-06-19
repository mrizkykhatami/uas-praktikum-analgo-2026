"""
heuristic.py
Algoritma A (Heuristik): Greedy Nearest Neighbor.

Dari Hub, selalu pilih pelanggan terdekat (jarak) yang belum dikunjungi,
lalu kembali ke Hub. Greedy berbasis jarak: saat memilih dari satu titik,
beban (dan rasio konsumsi) sama untuk semua kandidat, sehingga kriteria
biaya setara dengan jarak. Biaya BBM rute tetap dihitung dinamis agar
adil dibanding algoritma eksak.

Kompleksitas: Waktu O(n^2), Ruang O(n).
"""

import time
from graph import Graph
from cost import (
    KAPASITAS_MAX_DEFAULT,
    RASIO_PENUH_DEFAULT,
    RASIO_KOSONG_DEFAULT,
    hitung_rasio_konsumsi,
)


def _hitung_total_liter(graph: Graph, rute: list, kapasitas_max: float,
                        rasio_penuh: float, rasio_kosong: float) -> float:
    """Total liter BBM rute, rasio konsumsi dinamis per segmen."""
    beban = graph.total_berat_semua_paket()
    total_liter = 0.0

    for i in range(len(rute) - 1):
        asal, tujuan = rute[i], rute[i + 1]
        rasio = hitung_rasio_konsumsi(beban, kapasitas_max, rasio_penuh, rasio_kosong)
        total_liter += graph.jarak(asal, tujuan) * rasio
        if tujuan != graph.hub_index:  # paket turun setelah tiba
            beban = max(0.0, beban - graph.berat_paket(tujuan))

    return round(total_liter, 6)


def greedy_nearest_neighbor(
    graph: Graph,
    kapasitas_max: float = KAPASITAS_MAX_DEFAULT,
    rasio_penuh: float = RASIO_PENUH_DEFAULT,
    rasio_kosong: float = RASIO_KOSONG_DEFAULT,
) -> dict:
    """Bangun rute via Nearest Neighbor (greedy jarak) mulai dari Hub."""
    waktu_mulai = time.perf_counter()

    hub        = graph.hub_index
    dikunjungi = [False] * graph.n
    rute       = [hub]
    posisi     = hub
    dikunjungi[hub] = True

    for _ in range(graph.n - 1):
        terdekat, jarak_min = -1, float('inf')
        for j in range(graph.n):
            if not dikunjungi[j] and graph.jarak(posisi, j) < jarak_min:
                jarak_min, terdekat = graph.jarak(posisi, j), j
        dikunjungi[terdekat] = True
        rute.append(terdekat)
        posisi = terdekat

    rute.append(hub)  # kembali ke Hub
    waktu_ms = (time.perf_counter() - waktu_mulai) * 1000

    return {
        'algoritma'   : 'Greedy Nearest Neighbor',
        'rute'        : rute,
        'urutan_nama' : [graph.labels[i] for i in rute],
        'total_jarak' : graph.hitung_total_jarak(rute),
        'total_liter' : _hitung_total_liter(graph, rute, kapasitas_max,
                                            rasio_penuh, rasio_kosong),
        'waktu_ms'    : waktu_ms,
    }