"""
graph.py
Modul struktur data Graf berbobot menggunakan Adjacency Matrix.
"""

import json

class Graph:
    """
    Representasi graf berbobot dengan Adjacency Matrix.

    Atribut:
        n          : jumlah simpul (node)
        matrix     : matriks jarak n x n (list of list)
        labels     : nama tiap simpul
        lokasi     : data lengkap tiap simpul (dari JSON)
        paket      : data paket per tujuan
        hub_index  : index simpul Hub (default 0)
    """

    def __init__(self):
        self.n = 0
        self.matrix = []
        self.labels = []
        self.lokasi = []
        self.paket = []
        self.hub_index = 0

    # Load data
    def load_from_json(self, filepath: str):
        """Muat data graf dari file JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        adj = data['adjacency_matrix']
        self.matrix    = adj['matrix']
        self.labels    = adj['labels']
        self.lokasi    = data['lokasi']
        self.paket     = data['paket']
        self.hub_index = data['metadata']['hub_index']
        self.n         = len(self.matrix)

        self._validasi()

    def _validasi(self):
        """Pastikan matriks valid: ukuran konsisten, diagonal 0, simetris."""
        assert len(self.matrix) == self.n, "Ukuran matriks tidak konsisten"
        for i in range(self.n):
            assert len(self.matrix[i]) == self.n, f"Baris {i} tidak lengkap"
            assert self.matrix[i][i] == 0.0, f"Diagonal [{i}][{i}] bukan 0"
        for i in range(self.n):
            for j in range(self.n):
                assert self.matrix[i][j] == self.matrix[j][i], \
                    f"Matriks tidak simetris pada [{i}][{j}]"

    # Operasi dasar graf
    def jarak(self, asal: int, tujuan: int) -> float:
        """Kembalikan bobot edge antara dua simpul (jarak km)."""
        return self.matrix[asal][tujuan]

    def tetangga(self, simpul: int) -> list:
        """
        Kembalikan daftar (index_tetangga, jarak) dari suatu simpul,
        diurutkan dari yang terdekat ke terjauh.
        """
        hasil = []
        for j in range(self.n):
            if j != simpul and self.matrix[simpul][j] > 0:
                hasil.append((j, self.matrix[simpul][j]))
        hasil.sort(key=lambda x: x[1])
        return hasil

    def hitung_total_jarak(self, rute: list) -> float:
        """
        Hitung total jarak suatu rute (list index simpul).
        Rute harus dimulai dan diakhiri di Hub.
        Contoh rute: [0, 3, 1, 2, 0]
        """
        total = 0.0
        for i in range(len(rute) - 1):
            total += self.jarak(rute[i], rute[i + 1])
        return total

    def daftar_pelanggan(self) -> list:
        """Kembalikan list index semua simpul pelanggan (bukan Hub)."""
        return [i for i in range(self.n) if i != self.hub_index]

    # Utilitas paket
    def berat_paket(self, tujuan_id: int) -> float:
        """Kembalikan berat paket untuk tujuan tertentu."""
        for p in self.paket:
            if p['tujuan_id'] == tujuan_id:
                return p['berat_kg']
        return 0.0

    def total_berat_semua_paket(self) -> float:
        """Kembalikan total berat seluruh paket."""
        return sum(p['berat_kg'] for p in self.paket)

    # Tampilan / Debug
    def tampilkan_matriks(self):
        """Cetak adjacency matrix ke terminal."""
        lebar = 8
        header = ' ' * 16 + ''.join(f'{i:>{lebar}}' for i in range(self.n))
        print(header)
        print(' ' * 16 + '-' * (lebar * self.n))
        for i in range(self.n):
            label = self.labels[i][:13].ljust(14)
            baris = f'  {label} |'
            baris += ''.join(f'{self.matrix[i][j]:>{lebar}.1f}' for j in range(self.n))
            print(baris)

    def tampilkan_lokasi(self):
        """Cetak daftar simpul ke terminal."""
        print(f"  {'ID':>3}  {'Tipe':<12}  {'Nama'}")
        print("  " + "-" * 50)
        for loc in self.lokasi:
            tipe = loc['tipe'].upper()
            print(f"  [{loc['id']:>2}]  {tipe:<12}  {loc['nama']}")