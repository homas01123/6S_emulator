import click
import numpy as np
import rioxarray
import xarray as xr

def find_dark_object_value(arr):
    """Find the value of the dark object, ie the first dark value that is not an outlier."""
    preval = None
    step = np.nanmax(arr) / 255.0
    for val in np.unique(arr)[:100]:
        if val == 0:
            continue
        if preval is not None and (val - preval) < step:
            break
        else:
            preval = val
    return preval

def calc_haze_reduction(dark, band, model, mult=1.0):
    """Calculate the haze reduction for red, blue and green bands."""
    wavelengths = {
        'blue': 0.48,
        'green': 0.56,
        'red': 0.655,
        'nir': 0.815
    }

    k = wavelengths[band]

    haze_nir = dark * ((wavelengths['nir'] ** model) / (k ** model)) * mult
    haze_r = dark * ((wavelengths['red'] ** model) / (k ** model)) * mult
    haze_g = dark * ((wavelengths['green'] ** model) / (k ** model)) * mult
    haze_b = dark * ((wavelengths['blue'] ** model) / (k ** model)) * mult

    return (haze_nir,haze_r, haze_g, haze_b)

@click.command()
@click.argument('nir_path')
@click.argument('red_path')
@click.argument('green_path')
@click.argument('blue_path')
@click.option('--output_dir', '-o', type=str, required=True)
@click.option('--model', type=float, default=-2, help="Ranges from -4 (Very Clear) to -0.5 (Very Hazy)")
def dos(nir_path, red_path, green_path, blue_path, output_dir, model):
    """Correct for atmospheric scatter (haze) using Dark Object Subtraction."""
    nir = rioxarray.open_rasterio(nir_path).squeeze()
    red = rioxarray.open_rasterio(red_path).squeeze()
    green = rioxarray.open_rasterio(green_path).squeeze()
    blue = rioxarray.open_rasterio(blue_path).squeeze()

    # Using red as the reference
    dark = find_dark_object_value(red.values)
    haze_nir, haze_r, haze_g, haze_b = calc_haze_reduction(dark, 'red', model)

    corr_nir = nir - haze_nir
    corr_red = red - haze_r
    corr_green = green - haze_g
    corr_blue = blue - haze_b

    # Clip to zero
    corr_nir = corr_red.where(corr_nir >= 0, 0)
    corr_red = corr_red.where(corr_red >= 0, 0)
    corr_green = corr_green.where(corr_green >= 0, 0)
    corr_blue = corr_blue.where(corr_blue >= 0, 0)

    # Save each corrected band separately
    corr_nir.rio.to_raster(f"{output_dir}/B4_C3_BOA_DOS.tif")
    corr_red.rio.to_raster(f"{output_dir}/B3_C3_BOA_DOS.tif")
    corr_green.rio.to_raster(f"{output_dir}/B2_C3_BOA_DOS.tif")
    corr_blue.rio.to_raster(f"{output_dir}/B1_C3_BOA_DOS.tif")
    

if __name__ == "__main__":
    dos()
