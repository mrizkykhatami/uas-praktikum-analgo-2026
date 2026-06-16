"""
main.py
"""

from graph import Graph
import os

def main():
    """Test Graph (ntar hapus aja)."""
    
    json_path = os.path.join(os.path.dirname(__file__), 
                            "..", "data", "locations.json")
    g = Graph()
    g.load_from_json(json_path)
    print(f"Graph dimuat: {g.n} simpul, Hub = '{g.labels[g.hub_index]}'")
    
    jarak = g.jarak(0, 1)
    print(f"Jarak Hub ke Alun-alun: {jarak:.2f} km")
    
    tetangga = g.tetangga(0)
    print(f"3 tetangga terdekat dari Hub:")
    for i, (idx, dist) in enumerate(tetangga[:3]):
        print(f"  {i+1}. {g.labels[idx]}: {dist:.2f} km")
    
    rute = [0, 1, 2, 0]
    total = g.hitung_total_jarak(rute)
    print(f"Rute {rute}: Total {total:.2f} km")
    
    pelanggan = g.daftar_pelanggan()
    print(f"Total pelanggan: {len(pelanggan)}")
    
    for i in pelanggan[:3]:
        berat = g.berat_paket(i)
        print(f"  {g.labels[i]}: {berat:.1f} kg")
    
if __name__ == "__main__":
    main()
