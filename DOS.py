import click
import numpy as np
import rasterio


def find_dark_object_value(arr):
    """Find the value of the dark object
    ie the first dark value that is not an outlier
    """
    preval = None
    step = arr.max() / 255.0
    for val in np.unique(arr)[:100]:
        if val == 0:
            continue
        if preval is not None and (val - preval) < step:
            break
        else:
            preval = val
    return preval


def calc_haze_reduction(dark, band, model, mult=1.0):
    """Calculate the haze reduction for red, blue and green bands
    given the a visible band's TOA reflectance of a dark object
    and a scattering model (inverse proportion)
    Returns a three element tuple containing th TOA values to
    substract from the R, G and B bands to account for scatter
    """
    # wavelengths, micrometers
    wavelengths = {
        'blue': 0.48,
        'green': 0.56,
        'red': 0.655}

    k = wavelengths[band]

    haze_r = dark * ((wavelengths['red'] ** model) / (k ** model)) * mult
    haze_g = dark * ((wavelengths['green'] ** model) / (k ** model)) * mult
    haze_b = dark * ((wavelengths['blue'] ** model) / (k ** model)) * mult

    return (haze_r, haze_g, haze_b)


@click.command()
@click.argument('red_path')
@click.argument('green_path')
@click.argument('blue_path')
@click.option('--output', '-o', type=str, required=True)
@click.option('--model', type=float, default=-2,
              help="Ranges from -4 (Very Clear) to -0.5 (Very Hazy)")
def dos(red_path, green_path, blue_path, output, model):
    """ Correct for atmospheric scatter (haze) using Dark Object Subtraction
    Given a red, green and blue band and model of atmospheric
    scattering, correct the bands to remove this scatter component.
    The Rayleigh model states that relative scattering is
    inversely proportional to the fourth power of the wavelength (-4)
    The Mie model uses the first power for moderate atmospheric
    conditions (-1)
    Assumes input is TOA reflectance, float32, 0..1
    Outputs a uint16 RGB, 0..55000
    """
    with rasterio.open(red_path) as r, \
            rasterio.open(green_path) as g, \
            rasterio.open(blue_path) as b:
        red = r.read(1)
        green = g.read(1)
        blue = b.read(1)
        profile = r.profile

    profile['count'] = 3
    scale_to, scale_factor = 'uint16', 55000
    profile['dtype'] = scale_to

    # Using red as the reference
    dark = find_dark_object_value(red)
    haze_r, haze_g, haze_b = calc_haze_reduction(dark, 'red', model)

    corr_red = red - haze_r
    corr_green = green - haze_g
    corr_blue = blue - haze_b

    # Clip to zero, scale 0..1 to 0..55000
    corr_red[corr_red < 0] = 0
    corr_green[corr_green < 0] = 0
    corr_blue[corr_blue < 0] = 0
    corr_red = (corr_red * scale_factor).astype(scale_to)
    corr_green = (corr_green * scale_factor).astype(scale_to)
    corr_blue = (corr_blue * scale_factor).astype(scale_to)

    with rasterio.open(output, 'w', **profile) as dst:
        dst.write(corr_red, 1)
        dst.write(corr_green, 2)
        dst.write(corr_blue, 3)


if __name__ == "__main__":
    dos()