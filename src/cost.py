"""
cost.py
Modul Untuk Menghitung Fungsi Biaya (Cost Function)

Menghitung:
  1. Biaya BBM per segmen rute (beban dinamis berkurang tiap stop)
  2. Biaya Komputasi Server (waktu eksekusi x Rp50/ms)
  3. TCO = Biaya BBM + Biaya Komputasi

Formula rasio konsumsi BBM (interpolasi linear):
    rasio = (beban_saat_ini / kapasitas_max) * (r_penuh - r_kosong) + r_kosong

Semakin berat beban → semakin boros BBM.
Beban berkurang setiap kali kurir mengantar paket ke pelanggan.
"""

import json
from graph import Graph

# Default Scenario
RASIO_PENUH_DEFAULT  = 0.05
RASIO_KOSONG_DEFAULT = 0.02
KAPASITAS_MAX_DEFAULT = 30.0
BIAYA_KOMPUTASI_DEFAULT = 50

def load_scenario(filepath: str) -> dict:
    """Muat parameter skenario dari file JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback ke konstanta default jika file tidak ditemukan atau error
        return {
            'skenario': {
                'subsidi': {'harga_bbm_per_liter': 5000},
                'krisis':  {'harga_bbm_per_liter': 20000}
            },
            'parameter_kendaraan': {
                'kapasitas_maksimal_kg': KAPASITAS_MAX_DEFAULT,
                'rasio_konsumsi_penuh_liter_per_km':  RASIO_PENUH_DEFAULT,
                'rasio_konsumsi_kosong_liter_per_km': RASIO_KOSONG_DEFAULT,
            },
            'parameter_komputasi': {
                'biaya_per_milidetik': BIAYA_KOMPUTASI_DEFAULT
            }
        }


def hitung_rasio_konsumsi(
    beban_kg: float,
    kapasitas_max: float,
    rasio_penuh: float,
    rasio_kosong: float
) -> float:
    """
    Hitung rasio konsumsi BBM (liter/km) berdasarkan beban saat ini.

    Interpolasi linear:
        beban penuh  → rasio_penuh  (0.05 L/km)
        beban kosong → rasio_kosong (0.02 L/km)

    Parameter:
        beban_kg      : berat muatan saat ini (kg)
        kapasitas_max : kapasitas maksimal kendaraan (kg)
        rasio_penuh   : konsumsi BBM saat penuh (L/km)
        rasio_kosong  : konsumsi BBM saat kosong (L/km)

    Return:
        rasio konsumsi dalam liter/km
    """
    if kapasitas_max <= 0:
        return rasio_kosong

    proporsi = beban_kg / kapasitas_max
    # Clamp proporsi ke [0, 1]
    if proporsi > 1.0:
        proporsi = 1.0
    if proporsi < 0.0:
        proporsi = 0.0

    return proporsi * (rasio_penuh - rasio_kosong) + rasio_kosong


def hitung_biaya_bbm(
    graph: Graph,
    rute: list,
    harga_bbm: float,
    kapasitas_max: float,
    rasio_penuh: float,
    rasio_kosong: float
) -> dict:
    """
    Hitung biaya BBM total sepanjang rute dengan beban dinamis.

    Logika beban:
      - Kurir berangkat dari Hub membawa SEMUA paket
      - Setiap kali tiba di lokasi pelanggan, paket diturunkan
        → beban berkurang → rasio konsumsi turun
      - Segmen Hub→Pelanggan pertama: beban penuh
      - Segmen terakhir → Hub: beban kosong (semua sudah diantar)

    Parameter:
        graph        : objek Graph
        rute         : list index simpul (diawali & diakhiri Hub)
        harga_bbm    : harga per liter (Rupiah)
        kapasitas_max: kapasitas kendaraan (kg)
        rasio_penuh  : L/km saat penuh
        rasio_kosong : L/km saat kosong

    Return:
        dict berisi detail tiap segmen dan total biaya BBM
    """
    # Hitung total beban awal (semua paket dibawa)
    beban_saat_ini = graph.total_berat_semua_paket()

    detail_segmen  = []
    total_bbm_liter = 0.0
    total_biaya_bbm = 0.0

    for i in range(len(rute) - 1):
        asal   = rute[i]
        tujuan = rute[i + 1]
        jarak  = graph.jarak(asal, tujuan)

        # Hitung rasio konsumsi berdasarkan beban SEBELUM mengantar
        rasio   = hitung_rasio_konsumsi(
            beban_kg      = beban_saat_ini,
            kapasitas_max = kapasitas_max,
            rasio_penuh   = rasio_penuh,
            rasio_kosong  = rasio_kosong
        )

        liter_segmen = jarak * rasio
        biaya_segmen = liter_segmen * harga_bbm

        total_bbm_liter += liter_segmen
        total_biaya_bbm += biaya_segmen

        detail_segmen.append({
            'dari'          : graph.labels[asal],
            'ke'            : graph.labels[tujuan],
            'jarak_km'      : jarak,
            'beban_kg'      : round(beban_saat_ini, 2),
            'rasio_l_per_km': round(rasio, 4),
            'liter'         : round(liter_segmen, 4),
            'biaya_rp'      : round(biaya_segmen, 2),
        })

        # Setelah tiba di pelanggan, turunkan paket → kurangi beban
        if tujuan != graph.hub_index:
            berat_paket = graph.berat_paket(tujuan)
            beban_saat_ini -= berat_paket
            if beban_saat_ini < 0:
                beban_saat_ini = 0.0

    return {
        'detail_segmen'  : detail_segmen,
        'total_liter'    : round(total_bbm_liter, 4),
        'total_biaya_bbm': round(total_biaya_bbm, 2),
    }


def hitung_biaya_komputasi(waktu_ms: float, tarif_per_ms: int) -> float:
    """
    Hitung biaya komputasi cloud server.

    Formula: waktu_eksekusi (ms) x tarif (Rp/ms)

    Parameter:
        waktu_ms     : waktu eksekusi algoritma dalam milidetik
        tarif_per_ms : tarif cloud server per milidetik (Rp)

    Return:
        biaya komputasi dalam Rupiah
    """
    return round(waktu_ms * tarif_per_ms, 2)


def hitung_tco(biaya_bbm: float, biaya_komputasi: float) -> float:
    """
    Hitung Total Cost of Ownership (TCO).

    TCO = Biaya BBM + Biaya Komputasi

    Parameter:
        biaya_bbm        : total biaya BBM (Rp)
        biaya_komputasi  : total biaya server (Rp)

    Return:
        TCO dalam Rupiah
    """
    return round(biaya_bbm + biaya_komputasi, 2)


def jalankan_skenario(
    graph: Graph,
    hasil_algoritma: dict,
    nama_skenario: str,
    harga_bbm: float,
    kapasitas_max: float,
    rasio_penuh: float,
    rasio_kosong: float,
    tarif_komputasi: int
) -> dict:
    """
    Jalankan simulasi lengkap satu kombinasi (algoritma x skenario).

    Return:
        dict hasil lengkap siap ditampilkan dan dibandingkan
    """
    bbm = hitung_biaya_bbm(
        graph         = graph,
        rute          = hasil_algoritma['rute'],
        harga_bbm     = harga_bbm,
        kapasitas_max = kapasitas_max,
        rasio_penuh   = rasio_penuh,
        rasio_kosong  = rasio_kosong
    )

    biaya_komputasi = hitung_biaya_komputasi(
        waktu_ms     = hasil_algoritma['waktu_ms'],
        tarif_per_ms = tarif_komputasi
    )

    tco = hitung_tco(bbm['total_biaya_bbm'], biaya_komputasi)

    return {
        'algoritma'       : hasil_algoritma['algoritma'],
        'skenario'        : nama_skenario,
        'harga_bbm'       : harga_bbm,
        'rute'            : hasil_algoritma['rute'],
        'urutan_nama'     : hasil_algoritma['urutan_nama'],
        'total_jarak'     : hasil_algoritma['total_jarak'],
        'waktu_ms'        : hasil_algoritma['waktu_ms'],
        'total_liter'     : bbm['total_liter'],
        'biaya_bbm'       : bbm['total_biaya_bbm'],
        'biaya_komputasi' : biaya_komputasi,
        'tco'             : tco,
        'detail_segmen'   : bbm['detail_segmen'],
    }