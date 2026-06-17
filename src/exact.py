"""
exact.py
Algoritma B (Eksak) — Backtracking DFS with Pruning (Branch & Bound).

Mencari rute dengan BIAYA BBM minimum, bukan jarak terpendek. Karena rasio
konsumsi berubah mengikuti beban, rute terpendek belum tentu termurah —
dan metrik yang dinilai (TCO) adalah biaya. Maka optimasi dilakukan
terhadap biaya BBM secara langsung, dengan beban dilacak sepanjang rekursi.

Optimasi terhadap LITER (tanpa harga): sah karena harga BBM hanya pengali
seragam di semua segmen, sehingga urutan rute termurah identik untuk
skenario subsidi maupun krisis. Biaya rupiah dihitung terpisah oleh cost.py.

Kompleksitas: Waktu O(n!) worst-case (dipangkas pruning), Ruang O(n).
Tanpa library eksternal untuk logika pencarian.
"""

import time
from graph import Graph
from cost import hitung_rasio_konsumsi


class BacktrackingSolver:
    """Solver TSP via Backtracking DFS + Branch & Bound, optimasi biaya BBM."""

    def __init__(self, graph: Graph, kapasitas_max: float,
                 rasio_penuh: float, rasio_kosong: float):
        self.g           = graph
        self.hub         = graph.hub_index
        self.n_pelanggan = graph.n - 1
        self.kap         = kapasitas_max
        self.rp          = rasio_penuh
        self.rk          = rasio_kosong
        self.total_berat = graph.total_berat_semua_paket()

        self.rute_terbaik  = []
        self.liter_terbaik = float('inf')
        self.dikunjungi    = [False] * graph.n
        self.rute_saat_ini = [self.hub]
        self.node_explored = 0

    def _rasio(self, beban: float) -> float:
        return hitung_rasio_konsumsi(beban, self.kap, self.rp, self.rk)

    def _dfs(self, posisi: int, liter_akum: float, beban: float, terkunjungi: int):
        # Pruning: liter monoton naik, jadi cabang yang sudah kalah mustahil membaik.
        if liter_akum >= self.liter_terbaik:
            return

        # Base case: semua pelanggan dikunjungi, tambah segmen pulang ke Hub.
        if terkunjungi == self.n_pelanggan:
            liter_total = liter_akum + self.g.jarak(posisi, self.hub) * self._rasio(beban)
            if liter_total < self.liter_terbaik:
                self.liter_terbaik = liter_total
                self.rute_terbaik  = self.rute_saat_ini[:] + [self.hub]
            return

        for j in range(self.g.n):
            if self.dikunjungi[j] or j == self.hub:
                continue
            self.node_explored += 1

            # Segmen posisi->j ditempuh dgn beban SAAT INI (paket j turun setelah tiba).
            liter_j = self.g.jarak(posisi, j) * self._rasio(beban)
            if liter_akum + liter_j >= self.liter_terbaik:
                continue

            self.dikunjungi[j] = True
            self.rute_saat_ini.append(j)
            self._dfs(j, liter_akum + liter_j,
                      max(0.0, beban - self.g.berat_paket(j)), terkunjungi + 1)
            self.dikunjungi[j] = False
            self.rute_saat_ini.pop()

    def solve(self) -> dict:
        self.rute_terbaik  = []
        self.liter_terbaik = float('inf')
        self.dikunjungi    = [False] * self.g.n
        self.rute_saat_ini = [self.hub]
        self.node_explored = 0
        self.dikunjungi[self.hub] = True

        # Upper bound awal dari Greedy agar pruning agresif sejak node pertama.
        self.liter_terbaik = _greedy_upper_bound(self.g, self.kap, self.rp, self.rk)

        mulai = time.perf_counter()
        self._dfs(self.hub, 0.0, self.total_berat, 0)
        waktu_ms = (time.perf_counter() - mulai) * 1000

        return {
            'algoritma'     : 'Backtracking DFS with Pruning',
            'rute'          : self.rute_terbaik,
            'urutan_nama'   : [self.g.labels[i] for i in self.rute_terbaik],
            'total_jarak'   : self.g.hitung_total_jarak(self.rute_terbaik),
            'total_liter'   : round(self.liter_terbaik, 6),
            'waktu_ms'      : waktu_ms,
            'node_explored' : self.node_explored,
        }


def _greedy_upper_bound(graph: Graph, kap: float, rp: float, rk: float) -> float:
    """Batas atas awal (liter) via Nearest Neighbor, untuk mempercepat pruning."""
    hub        = graph.hub_index
    dikunjungi = [False] * graph.n
    dikunjungi[hub] = True
    posisi, beban, liter = hub, graph.total_berat_semua_paket(), 0.0

    for _ in range(graph.n - 1):
        terdekat, dmin = -1, float('inf')
        for j in range(graph.n):
            if not dikunjungi[j] and graph.jarak(posisi, j) < dmin:
                dmin, terdekat = graph.jarak(posisi, j), j
        if terdekat == -1:
            break
        liter += dmin * hitung_rasio_konsumsi(beban, kap, rp, rk)
        beban = max(0.0, beban - graph.berat_paket(terdekat))
        dikunjungi[terdekat], posisi = True, terdekat

    liter += graph.jarak(posisi, hub) * hitung_rasio_konsumsi(beban, kap, rp, rk)
    return liter


def backtracking_exact(graph: Graph, kapasitas_max: float,
                       rasio_penuh: float, rasio_kosong: float) -> dict:
    """Wrapper publik Algoritma B. Parameter kendaraan dibaca dari scenario.json."""
    return BacktrackingSolver(graph, kapasitas_max, rasio_penuh, rasio_kosong).solve()