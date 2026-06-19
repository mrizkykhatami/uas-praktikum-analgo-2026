"""
main.py
"""

import os
from graph import Graph
from heuristic import greedy_nearest_neighbor
from exact import backtracking_exact
from cost import load_scenario


def main():
    """testing"""

    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, '..', 'data')
    json_path = os.path.join(data_dir, 'locations.json')
    scenario_path = os.path.join(data_dir, 'scenario.json')

    graph = Graph()
    graph.load_from_json(json_path)

    scenario = load_scenario(scenario_path)
    kendaraan = scenario['parameter_kendaraan']
    kapasitas_max = kendaraan['kapasitas_maksimal_kg']
    rasio_penuh = kendaraan['rasio_konsumsi_penuh_liter_per_km']
    rasio_kosong = kendaraan['rasio_konsumsi_kosong_liter_per_km']

    print('== Uji Coba ==')
    print(f'Graph dimuat: {graph.n} simpul, Hub = {graph.labels[graph.hub_index]}')
    print(f'Kapasitas kendaraan: {kapasitas_max} kg')
    print(f'Rasio penuh: {rasio_penuh} L/km, Rasio kosong: {rasio_kosong} L/km')
    print()

    hasil_heuristic = greedy_nearest_neighbor(
        graph,
        kapasitas_max = kapasitas_max,
        rasio_penuh   = rasio_penuh,
        rasio_kosong  = rasio_kosong,
    )

    hasil_exact = backtracking_exact(
        graph,
        kapasitas_max = kapasitas_max,
        rasio_penuh   = rasio_penuh,
        rasio_kosong  = rasio_kosong,
    )

    print('--- Heuristic ---')
    print(f"Algoritma  : {hasil_heuristic['algoritma']}")
    print(f"Rute       : {hasil_heuristic['urutan_nama']}")
    print(f"Total jarak: {hasil_heuristic['total_jarak']:.4f} km")
    print(f"Total liter: {hasil_heuristic['total_liter']:.6f} L")
    print(f"Waktu      : {hasil_heuristic['waktu_ms']:.4f} ms")
    print()

    print('--- Exact ---')
    print(f"Algoritma  : {hasil_exact['algoritma']}")
    print(f"Rute       : {hasil_exact['urutan_nama']}")
    print(f"Total jarak: {hasil_exact['total_jarak']:.4f} km")
    print(f"Total liter: {hasil_exact['total_liter']:.6f} L")
    print(f"Waktu      : {hasil_exact['waktu_ms']:.4f} ms")


if __name__ == '__main__':
    main()
