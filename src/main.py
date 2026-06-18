"""
main.py
Pipeline simulasi CLI: membandingkan Algoritma Heuristik (Greedy) vs
Eksak (Backtracking) dari sisi Total Cost of Ownership (TCO) pada dua
skenario ekonomi.

Menjalankan:
    python src/main.py                      # kedua skenario (default)
    python src/main.py --scenario subsidi   # satu skenario
    python src/main.py --scenario krisis
    python src/main.py --repeat 5           # median dari N run (waktu stabil)

Semua parameter dibaca dari data/locations.json & data/scenario.json.
Tidak ada nilai yang di-hardcode di logika.
"""

import os
import sys
import argparse
from statistics import median

from graph import Graph
from heuristic import greedy_nearest_neighbor
from exact import backtracking_exact
from cost import (load_scenario, jalankan_skenario,
                  hitung_biaya_bbm, hitung_biaya_komputasi)


def _path_data(nama_file):
    return os.path.join(os.path.dirname(__file__), "..", "data", nama_file)


# Warna ANSI untuk output terminal. Nonaktif otomatis bila output
# dialihkan ke file/pipe (mis. saat di-redirect), agar teks tetap bersih.
class C:
    _aktif = sys.stdout.isatty()
    HEADER = "\033[1;36m" if _aktif else ""   # cyan tebal
    JUDUL  = "\033[1;37m" if _aktif else ""    # putih tebal
    HIJAU  = "\033[32m"   if _aktif else ""
    KUNING = "\033[33m"   if _aktif else ""
    ABU    = "\033[90m"   if _aktif else ""
    RESET  = "\033[0m"    if _aktif else ""


def _jalankan_dengan_median(fungsi, repeat):
    """
    Jalankan solver 'repeat' kali, kembalikan hasil dengan waktu_ms = median.
    Median meredam noise OS agar biaya komputasi (dan TCO) lebih stabil.
    """
    hasil = None
    waktu_list = []
    for _ in range(repeat):
        hasil = fungsi()
        waktu_list.append(hasil['waktu_ms'])
    hasil['waktu_ms'] = median(waktu_list)
    return hasil


def _format_rute(urutan_nama):
    return " -> ".join(urutan_nama)


def _cetak_hasil_algoritma(h):
    print(f"\n  {C.JUDUL}{h['algoritma']}{C.RESET}")
    print(f"    Rute           : {C.ABU}{_format_rute(h['urutan_nama'])}{C.RESET}")
    print(f"    Total jarak    : {h['total_jarak']:.2f} km")
    print(f"    Total BBM      : {h['total_liter']:.4f} liter")
    print(f"    Waktu eksekusi : {h['waktu_ms']:.4f} ms")
    print(f"    Biaya BBM      : Rp {h['biaya_bbm']:>14,.2f}")
    print(f"    Biaya komputasi: Rp {h['biaya_komputasi']:>14,.2f}")
    print(f"    {C.JUDUL}>> TCO         : Rp {h['tco']:>14,.2f}{C.RESET}")


def _cetak_komparasi(hasil_heuristik, hasil_eksak):
    print("\n  " + C.ABU + "-" * 64 + C.RESET)
    selisih = hasil_heuristik['tco'] - hasil_eksak['tco']
    if selisih > 0:
        print(f"  {C.HIJAU}REKOMENDASI: Algoritma Eksak lebih murah "
              f"Rp {selisih:,.2f}{C.RESET}")
        print(f"  {C.ABU}Penghematan BBM menutupi biaya komputasinya pada skenario ini.{C.RESET}")
    elif selisih < 0:
        print(f"  {C.KUNING}REKOMENDASI: Algoritma Heuristik lebih murah "
              f"Rp {abs(selisih):,.2f}{C.RESET}")
        print(f"  {C.ABU}Biaya komputasi eksak tak sebanding penghematan BBM-nya.{C.RESET}")
    else:
        print(f"  TCO kedua algoritma setara (titik impas).")


def jalankan_skenario_penuh(graph, kunci_skenario, skenario_data,
                            kendaraan, tarif_komputasi, hasil_h, hasil_e):
    """Jalankan & tampilkan satu skenario ekonomi untuk kedua algoritma."""
    info     = skenario_data[kunci_skenario]
    harga    = info['harga_bbm_per_liter']
    nama     = info['nama']

    print("\n" + C.HEADER + "=" * 68 + C.RESET)
    print(f"  {C.HEADER}{nama.upper()}  |  Harga BBM: Rp {harga:,.0f}/liter{C.RESET}")
    print(C.HEADER + "=" * 68 + C.RESET)

    sim_h = jalankan_skenario(
        graph, hasil_h, nama, harga,
        kendaraan['kapasitas_maksimal_kg'],
        kendaraan['rasio_konsumsi_penuh_liter_per_km'],
        kendaraan['rasio_konsumsi_kosong_liter_per_km'],
        tarif_komputasi)
    sim_e = jalankan_skenario(
        graph, hasil_e, nama, harga,
        kendaraan['kapasitas_maksimal_kg'],
        kendaraan['rasio_konsumsi_penuh_liter_per_km'],
        kendaraan['rasio_konsumsi_kosong_liter_per_km'],
        tarif_komputasi)

    _cetak_hasil_algoritma(sim_h)
    _cetak_hasil_algoritma(sim_e)
    _cetak_komparasi(sim_h, sim_e)
    return sim_h, sim_e


def cetak_analisis_break_even(graph, hasil_h, hasil_e, kendaraan, tarif_komputasi):
    """
    Hitung pada harga BBM berapa Algoritma Eksak mulai lebih murah dari
    Heuristik (titik break-even).

    TCO tiap algoritma linear terhadap harga BBM h:
        TCO(h) = total_liter * h + biaya_komputasi
    Titik impas didapat dari menyamakan kedua garis:
        h = (komputasi_eksak - komputasi_heuristik) / (liter_h - liter_e)
    Di atas harga ini, penghematan BBM eksak menutupi biaya komputasinya.
    """
    kap = kendaraan['kapasitas_maksimal_kg']
    rp  = kendaraan['rasio_konsumsi_penuh_liter_per_km']
    rk  = kendaraan['rasio_konsumsi_kosong_liter_per_km']

    bbm_h = hitung_biaya_bbm(graph, hasil_h['rute'], 1.0, kap, rp, rk)
    bbm_e = hitung_biaya_bbm(graph, hasil_e['rute'], 1.0, kap, rp, rk)
    liter_h = bbm_h['total_liter']
    liter_e = bbm_e['total_liter']

    komp_h = hitung_biaya_komputasi(hasil_h['waktu_ms'], tarif_komputasi)
    komp_e = hitung_biaya_komputasi(hasil_e['waktu_ms'], tarif_komputasi)

    print("\n" + C.HEADER + "=" * 68 + C.RESET)
    print(f"  {C.HEADER}ANALISIS BREAK-EVEN: KAPAN ALGORITMA EKSAK LEBIH UNGGUL?{C.RESET}")
    print(C.HEADER + "=" * 68 + C.RESET)
    print(f"\n  Penghematan BBM eksak  : {liter_h - liter_e:.4f} liter/rute")
    print(f"  Selisih biaya komputasi: Rp {komp_e - komp_h:,.2f}")

    selisih_liter = liter_h - liter_e
    if selisih_liter <= 0:
        print("\n  Eksak tidak menghemat BBM pada rute ini; break-even tidak ada.")
        return

    harga_impas = (komp_e - komp_h) / selisih_liter
    print(f"\n  {C.JUDUL}>> TITIK BREAK-EVEN: Rp {harga_impas:,.2f} / liter{C.RESET}")
    print(f"     {C.KUNING}Di bawah harga ini : Heuristik lebih ekonomis.{C.RESET}")
    print(f"     {C.HIJAU}Di atas harga ini  : Eksak mulai menguntungkan.{C.RESET}")

    print("\n  Sensitivitas TCO terhadap harga BBM:")
    print(f"  {C.ABU}{'Harga/L':>12} | {'TCO Heuristik':>16} | "
          f"{'TCO Eksak':>16} | Unggul{C.RESET}")
    print("  " + C.ABU + "-" * 60 + C.RESET)
    daftar_harga = sorted(set([5000, 20000, 50000, 100000,
                               int(harga_impas), int(harga_impas) + 10000]))
    for harga in daftar_harga:
        tco_h = liter_h * harga + komp_h
        tco_e = liter_e * harga + komp_e
        if tco_e < tco_h:
            unggul = f"{C.HIJAU}Eksak{C.RESET}"
        else:
            unggul = f"{C.KUNING}Heuristik{C.RESET}"
        print(f"  {harga:>12,} | {tco_h:>16,.0f} | {tco_e:>16,.0f} | {unggul}")


def main():
    parser = argparse.ArgumentParser(
        description="Simulasi TCO rute Last-Mile Delivery: Heuristik vs Eksak.")
    parser.add_argument("--scenario", default="both",
                        choices=["subsidi", "krisis", "both"],
                        help="Skenario ekonomi (default: both).")
    parser.add_argument("--repeat", type=int, default=5,
                        help="Jumlah run untuk median waktu (default: 5).")
    args = parser.parse_args()

    # Muat data
    graph = Graph()
    graph.load_from_json(_path_data("locations.json"))
    scenario = load_scenario(_path_data("scenario.json"))

    kendaraan       = scenario['parameter_kendaraan']
    tarif_komputasi = scenario['parameter_komputasi']['biaya_per_milidetik']
    skenario_data   = scenario['skenario']

    kap = kendaraan['kapasitas_maksimal_kg']
    rp  = kendaraan['rasio_konsumsi_penuh_liter_per_km']
    rk  = kendaraan['rasio_konsumsi_kosong_liter_per_km']

    print(f"\n{C.HEADER}SIMULASI TCO: LAST-MILE DELIVERY ROUTE OPTIMIZATION{C.RESET}")
    print(f"{C.ABU}Dataset: {graph.n} simpul (1 Hub + {graph.n - 1} pelanggan), "
          f"total beban {graph.total_berat_semua_paket():.1f} kg{C.RESET}")
    print(f"{C.ABU}Pengukuran waktu: median dari {args.repeat} run{C.RESET}")

    # Jalankan kedua algoritma (rute tak bergantung harga BBM)
    hasil_h = _jalankan_dengan_median(
        lambda: greedy_nearest_neighbor(graph), args.repeat)
    hasil_e = _jalankan_dengan_median(
        lambda: backtracking_exact(graph, kap, rp, rk), args.repeat)

    # Eksekusi skenario yang diminta
    daftar = ["subsidi", "krisis"] if args.scenario == "both" else [args.scenario]
    for kunci in daftar:
        jalankan_skenario_penuh(graph, kunci, skenario_data,
                                kendaraan, tarif_komputasi, hasil_h, hasil_e)

    # Analisis break-even: kapan eksak mulai unggul (lintas semua harga BBM)
    cetak_analisis_break_even(graph, hasil_h, hasil_e, kendaraan, tarif_komputasi)

    print()


if __name__ == "__main__":
    main()