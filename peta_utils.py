import folium
import rasterio
import rasterio.mask
import numpy as np
from matplotlib import cm
from shapely.geometry import mapping

def generate_flood_map(shp_gdf, raster_path):
    """
    Fungsi untuk memproses raster, melakukan masking/clipping, 
    dan mengembalikan objek Peta Folium.
    """
    # 1. Pastikan CRS Shapefile adalah Lat/Lon (EPSG:4326)
    batas_folium = shp_gdf.to_crs(epsg=4326)

    # 2. Buka Raster dan Lakukan Masking
    with rasterio.open(raster_path) as src:
        # Ambil geometri dari shapefile
        geoms = [mapping(g) for g in batas_folium.geometry]
        
        # MASKING: Potong raster sesuai bentuk shapefile
        # nodata=-9999 digunakan agar kita bisa membedakan area luar vs area aman
        out_image, out_transform = rasterio.mask.mask(src, geoms, crop=True, nodata=-9999)
        
        data = out_image[0]
        
        # Hitung batas koordinat baru untuk Folium
        min_lon, min_lat = out_transform * (0, out_image.shape[1])
        max_lon, max_lat = out_transform * (out_image.shape[2], 0)
        bounds = [[min_lat, min_lon], [max_lat, max_lon]]

    # 3. Pewarnaan dan Transparansi
    # Ubah -9999 menjadi NaN untuk visualisasi
    data_visual = data.astype('float')
    data_visual[data_visual == -9999] = np.nan

    # Normalisasi data 0-1
    # Menggunakan nanmin/nanmax agar NaN tidak merusak perhitungan
    min_val = np.nanmin(data_visual)
    max_val = np.nanmax(data_visual)
    data_norm = (data_visual - min_val) / (max_val - min_val)

    # Terapkan Colormap 'coolwarm' (Biru ke Merah)
    colormap = cm.get_cmap('coolwarm')
    colored_data = colormap(data_norm)
    
    # Konversi ke format gambar (0-255)
    image_data = np.uint8(colored_data[:, :, :3] * 255)

    # 4. Atur Alpha Channel (Transparansi)
    alpha = np.uint8(colored_data[:, :, 3] * 255)
    
    # Masking Visual:
    # Jika nilainya -9999 (luar batas) atau NaN -> Transparan Total (0)
    mask_luar = (data == -9999) | np.isnan(data_visual)
    alpha[mask_luar] = 0
    
    # Jika di dalam batas -> Agak transparan (180 dari 255)
    alpha[~mask_luar] = 180 

    final_image = np.dstack((image_data, alpha))

    # 5. Buat Peta Folium
    center = [batas_folium.geometry.centroid.y.mean(), batas_folium.geometry.centroid.x.mean()]
    m = folium.Map(location=center, zoom_start=10, tiles='CartoDB positron')

    # Tambahkan Raster Overlay
    folium.raster_layers.ImageOverlay(
        image=final_image,
        bounds=bounds,
        name='Prediksi Kerentanan Banjir',
        interactive=True,
        cross_origin=False,
        zindex=1
    ).add_to(m)

    # Tambahkan Garis Batas Administrasi
    folium.GeoJson(
        batas_folium,
        name='Batas Administrasi',
        style_function=lambda x: {'fillColor': 'none', 'color': 'black', 'weight': 2}
    ).add_to(m)

    folium.LayerControl().add_to(m)
    
    return m