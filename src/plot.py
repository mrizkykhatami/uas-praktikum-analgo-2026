"""
plot.py
Visualisasi grafik perbandingan Algoritma Heuristik (Greedy) vs
Eksak (Backtracking) dari sisi Total Cost of Ownership (TCO).

Menjalankan kedua algoritma sekali, lalu menggambar 4 panel grafik:
  1. TCO per skenario ekonomi (grouped bar)        -> metrik utama
  2. Rincian biaya: BBM vs Komputasi (stacked bar) -> sumber biaya
  3. Metrik rute: total jarak & konsumsi BBM (liter)
  4. Waktu eksekusi algoritma (skala log)          -> ongkos komputasi

Semua parameter dibaca dari data/locations.json & data/scenario.json
(tidak ada nilai yang di-hardcode), persis seperti main.py.

Menjalankan:
    python src/plot.py                 # tampilkan + simpan PNG
    python src/plot.py --no-show       # hanya simpan PNG (untuk CI/headless)
    python src/plot.py --repeat 9      # median dari N run (waktu lebih stabil)
    python src/plot.py --out docs/grafik.png

Hasil PNG default: docs/perbandingan_algoritma.png
"""

import os
import sys
import argparse
from statistics import median

import matplotlib
matplotlib.use("Agg") if "--no-show" in sys.argv else None
import matplotlib.pyplot as plt

from graph import Graph
from heuristic import greedy_nearest_neighbor
from exact import backtracking_exact
from cost import load_scenario, jalankan_skenario


def _path_data(nama_file):
    return os.path.join(os.path.dirname(__file__), "..", "data", nama_file)


def _path_docs(nama_file):
    return os.path.join(os.path.dirname(__file__), "..", "docs", nama_file)


# Warna konsisten untuk tiap algoritma di seluruh panel.
WARNA_HEURISTIK = "#e07a3f"   # oranye  (Greedy)
WARNA_EKSAK     = "#2f6fb0"   # biru    (Backtracking)
WARNA_BBM       = "#5aa469"   # hijau   (komponen BBM)
WARNA_KOMPUTASI = "#b0563a"   # merah   (komponen komputasi)


def _jalankan_dengan_median(fungsi, repeat):
    """Jalankan solver 'repeat' kali, ambil waktu_ms median (redam noise OS)."""
    hasil = None
    waktu_list = []
    for _ in range(repeat):
        hasil = fungsi()
        waktu_list.append(hasil['waktu_ms'])
    hasil['waktu_ms'] = median(waktu_list)
    return hasil


def _format_rp(nilai):
    """Format angka Rupiah ringkas untuk anotasi (mis. 12.345 -> 12,3 rb)."""
    if nilai >= 1_000_000:
        return f"Rp {nilai/1_000_000:.2f} jt"
    if nilai >= 1_000:
        return f"Rp {nilai/1_000:.1f} rb"
    return f"Rp {nilai:.0f}"


def _anotasi_bar(ax, bars, format_fn=lambda v: f"{v:.2f}"):
    """Tulis nilai di atas tiap batang."""
    for bar in bars:
        tinggi = bar.get_height()
        ax.annotate(format_fn(tinggi),
                    xy=(bar.get_x() + bar.get_width() / 2, tinggi),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)


def kumpulkan_data(graph, scenario, repeat):
    """
    Jalankan kedua algoritma & evaluasi pada tiap skenario ekonomi.

    Return dict:
        nama_skenario : list label skenario (sumbu X panel 1 & 2)
        heuristik/eksak : dict berisi list tco, bbm, komputasi per skenario,
                          plus metrik rute (jarak, liter, waktu) yang konstan.
    """
    kendaraan       = scenario['parameter_kendaraan']
    tarif_komputasi = scenario['parameter_komputasi']['biaya_per_milidetik']
    skenario_data   = scenario['skenario']

    kap = kendaraan['kapasitas_maksimal_kg']
    rp  = kendaraan['rasio_konsumsi_penuh_liter_per_km']
    rk  = kendaraan['rasio_konsumsi_kosong_liter_per_km']

    # Rute & waktu tidak bergantung harga BBM -> hitung sekali saja.
    hasil_h = _jalankan_dengan_median(
        lambda: greedy_nearest_neighbor(graph), repeat)
    hasil_e = _jalankan_dengan_median(
        lambda: backtracking_exact(graph, kap, rp, rk), repeat)

    data = {
        "nama_skenario": [],
        "heuristik": {"label": hasil_h['algoritma'], "tco": [], "bbm": [],
                      "komputasi": [], "jarak": hasil_h['total_jarak'],
                      "liter": [], "waktu": hasil_h['waktu_ms']},
        "eksak":     {"label": hasil_e['algoritma'], "tco": [], "bbm": [],
                      "komputasi": [], "jarak": hasil_e['total_jarak'],
                      "liter": [], "waktu": hasil_e['waktu_ms']},
    }

    for kunci in ["subsidi", "krisis"]:
        info  = skenario_data[kunci]
        harga = info['harga_bbm_per_liter']
        data["nama_skenario"].append(f"{info['nama']}\n(Rp {harga:,.0f}/L)")

        sim_h = jalankan_skenario(graph, hasil_h, info['nama'], harga,
                                  kap, rp, rk, tarif_komputasi)
        sim_e = jalankan_skenario(graph, hasil_e, info['nama'], harga,
                                  kap, rp, rk, tarif_komputasi)

        data["heuristik"]["tco"].append(sim_h['tco'])
        data["heuristik"]["bbm"].append(sim_h['biaya_bbm'])
        data["heuristik"]["komputasi"].append(sim_h['biaya_komputasi'])
        data["heuristik"]["liter"].append(sim_h['total_liter'])

        data["eksak"]["tco"].append(sim_e['tco'])
        data["eksak"]["bbm"].append(sim_e['biaya_bbm'])
        data["eksak"]["komputasi"].append(sim_e['biaya_komputasi'])
        data["eksak"]["liter"].append(sim_e['total_liter'])

    return data


def _panel_tco(ax, data):
    """Panel 1: TCO per skenario (grouped bar) — metrik keputusan utama."""
    x = range(len(data["nama_skenario"]))
    lebar = 0.38
    pos_h = [i - lebar / 2 for i in x]
    pos_e = [i + lebar / 2 for i in x]

    b1 = ax.bar(pos_h, data["heuristik"]["tco"], lebar,
                label=data["heuristik"]["label"], color=WARNA_HEURISTIK)
    b2 = ax.bar(pos_e, data["eksak"]["tco"], lebar,
                label=data["eksak"]["label"], color=WARNA_EKSAK)

    _anotasi_bar(ax, b1, _format_rp)
    _anotasi_bar(ax, b2, _format_rp)

    ax.set_title("TCO per Skenario Ekonomi", fontweight="bold")
    ax.set_ylabel("Total Cost of Ownership (Rp)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(data["nama_skenario"])
    ax.legend(fontsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.5)


def _panel_rincian_biaya(ax, data):
    """Panel 2: Komposisi biaya BBM vs Komputasi (stacked bar) per algoritma."""
    labels, bbm, komp, warna_tepi = [], [], [], []
    for idx, nama in enumerate(data["nama_skenario"]):
        nama_pendek = nama.split("\n")[0].replace("Skenario ", "")
        labels.append(f"{nama_pendek}\nHeuristik")
        bbm.append(data["heuristik"]["bbm"][idx])
        komp.append(data["heuristik"]["komputasi"][idx])
        warna_tepi.append(WARNA_HEURISTIK)
        labels.append(f"{nama_pendek}\nEksak")
        bbm.append(data["eksak"]["bbm"][idx])
        komp.append(data["eksak"]["komputasi"][idx])
        warna_tepi.append(WARNA_EKSAK)

    x = range(len(labels))
    b_bbm = ax.bar(x, bbm, color=WARNA_BBM, label="Biaya BBM",
                   edgecolor=warna_tepi, linewidth=1.5)
    ax.bar(x, komp, bottom=bbm, color=WARNA_KOMPUTASI,
           label="Biaya Komputasi", edgecolor=warna_tepi, linewidth=1.5)

    ax.set_title("Rincian Biaya: BBM vs Komputasi", fontweight="bold")
    ax.set_ylabel("Biaya (Rp)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.legend(fontsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.5)


def _panel_metrik_rute(ax, data):
    """Panel 3: Total jarak (km) & konsumsi BBM (liter) per algoritma."""
    # Liter konstan terhadap harga -> ambil nilai skenario pertama.
    liter_h = data["heuristik"]["liter"][0]
    liter_e = data["eksak"]["liter"][0]

    kategori = ["Total Jarak\n(km)", "Konsumsi BBM\n(liter)"]
    nilai_h  = [data["heuristik"]["jarak"], liter_h]
    nilai_e  = [data["eksak"]["jarak"], liter_e]

    x = range(len(kategori))
    lebar = 0.38
    b1 = ax.bar([i - lebar / 2 for i in x], nilai_h, lebar,
                label=data["heuristik"]["label"], color=WARNA_HEURISTIK)
    b2 = ax.bar([i + lebar / 2 for i in x], nilai_e, lebar,
                label=data["eksak"]["label"], color=WARNA_EKSAK)

    _anotasi_bar(ax, b1)
    _anotasi_bar(ax, b2)

    ax.set_title("Metrik Rute: Jarak & Konsumsi BBM", fontweight="bold")
    ax.set_ylabel("Nilai")
    ax.set_xticks(list(x))
    ax.set_xticklabels(kategori)
    ax.legend(fontsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.5)


def _panel_waktu(ax, data):
    """Panel 4: Waktu eksekusi algoritma (skala log) — ongkos komputasi."""
    labels = [data["heuristik"]["label"], data["eksak"]["label"]]
    waktu  = [data["heuristik"]["waktu"], data["eksak"]["waktu"]]
    warna  = [WARNA_HEURISTIK, WARNA_EKSAK]

    bars = ax.bar(labels, waktu, color=warna)
    _anotasi_bar(ax, bars, lambda v: f"{v:.4f} ms")

    ax.set_title("Waktu Eksekusi Algoritma", fontweight="bold")
    ax.set_ylabel("Waktu (ms, skala log)")
    ax.set_yscale("log")
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.5, which="both")


def buat_grafik(data, total_titik, beban_total):
    """Susun 4 panel grafik perbandingan dalam satu figure."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Perbandingan Algoritma: Heuristik (Greedy) vs Eksak (Backtracking)\n"
        f"Last-Mile Delivery — {total_titik} titik, beban total {beban_total:.1f} kg",
        fontsize=14, fontweight="bold")

    _panel_tco(axes[0][0], data)
    _panel_rincian_biaya(axes[0][1], data)
    _panel_metrik_rute(axes[1][0], data)
    _panel_waktu(axes[1][1], data)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def main():
    parser = argparse.ArgumentParser(
        description="Grafik perbandingan TCO: Heuristik vs Eksak.")
    parser.add_argument("--repeat", type=int, default=5,
                        help="Jumlah run untuk median waktu (default: 5).")
    parser.add_argument("--out", default=_path_docs("perbandingan_algoritma.png"),
                        help="Path file PNG keluaran.")
    parser.add_argument("--no-show", action="store_true",
                        help="Hanya simpan PNG tanpa menampilkan jendela.")
    args = parser.parse_args()

    graph = Graph()
    graph.load_from_json(_path_data("locations.json"))
    scenario = load_scenario(_path_data("scenario.json"))

    print("Menjalankan kedua algoritma & mengumpulkan data...")
    data = kumpulkan_data(graph, scenario, args.repeat)

    fig = buat_grafik(data, graph.n, graph.total_berat_semua_paket())

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=150, bbox_inches="tight")
    print(f"Grafik tersimpan: {os.path.abspath(args.out)}")

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
