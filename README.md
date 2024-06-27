## Introduction

For Remotely Sensed Optical (Multispectral/Hyperspectral) Images, The sensor acquired radiance (L) needs to be corrected for the 1. Atmoshperic gaseous transmittance (τ<sub>g</sub>), 2. Rayleigh-aerosol combined scattering in the atmoshperic column (Path radiance; L<sub>p</sub>) to calculate the surface reflectance (ρ). The theory of Radiave Transfer can be used in following way to algebrically express these quantities:

ρ = π(L -L<sub>p</sub>) / τ<sub>g</sub>(E<sub>dir</sub> + E<sub>dif</sub>)

where,

* ρ = surface reflectance
* L = at-sensor radiance
* L<sub>p</sub> = path radiance (Rayleigh + Aerosol)
* τ<sub>g</sub> = gaseous transmissivity (from surface to satellite)
* E<sub>dir</sub> = direct solar irradiance 
* E<sub>dif</sub> = diffuse solar irradiance
* π = 3.1415 (pi)

Algebraically rearranging, ρ can be obtained as ρ = (L - a) / b, where a = L<sub>p</sub> and b = (τ<sub>g</sub>(E<sub>dir</sub> + E<sub>dif</sub>))/π. 

The L<sub>p</sub> can be obtained as a function of atmospheric column height of water vapour and Ozone (Rayleigh scattering) and Aerosol Optical Thickness (AOT) (Aerosol scattering). The τ<sub>g</sub>, E<sub>dir</sub> and E<sub>dif</sub> can climatically be approximated for the sun-sensor geometry and given time. The Python wrapper ([Py6S](https://py6s.readthedocs.io/en/latest/introduction.html) by Wilson, 2013) of Second Simulation of a Satellite Signal in the Solar Spectrum vector code ([6S](https://salsa.umd.edu/6spage.html)) (Vermote et al., 1997) has been used to approximate a and b mentioned above as a function of solar zenith angle, atmospheric column height of water vapour and ozone, AOT at 550 nanometers (nm) and the surface elevation. However, run-time simulation with Py6S is computationally extensive, especially when ran for millions of pixels in a satellite acquired image. Hence, wavelength dependent Look-Up Tables (LUTs) are obtained for a and b for a vast number of combinations of the input parameters (solar zenith angle, atmospheric column height of water vapour and ozone, AOT550 and the surface elevation). In the AC process, the input parameters are fetched as mean over the image extent from different data sources (solar zenith from metadata, water vapour from NCEP/NCAR, ozone from TOMS/OMI, AOT550 from MODIS and surface elevation from SRTM). Finally, the a and b values are interpolated from the LUT for the mean values of input parameters and the image is algebraically corrected. The interpolatable LUTs (iLUTs) are obtained from [6S emulator](https://github.com/samsammurphy/6S_emulator), which is an open-source tool to create LUTs of a and b with **100x speed** than 6S, but with minimal additional error (i.e. < 0.5 %).

### Installation

##### Quick note

The installation instructions (below) are for building look-up tables mainly. In case of use cases with pre-existing iLUTs, all that is required are python3.x, numpy and scipy.

#### Recommended installation

The [recommended installation](http://py6s.readthedocs.io/en/latest/installation.html) method is to use the [conda](https://conda.io/docs/install/quick.html) package and environment manager.

`$ conda create -n py6s-env -c conda-forge py6s`

This will create a new environment that needs to be activated.

### Usage

#### Quick Start

See the [jupyter notebook](https://github.com/datakaveri/ugix-ard-pipelines/blob/main/jupyter_notebooks/ACX_constrained.ipynb) for an illustrated example of atmospheric correction with pre-existing iLUTs. The creation of LUTs and iLUTS are explained below.

#### Building your own interpolated look-up tables

It is much more bandwidth efficient to create user-defined look-up tables, and then interpolate them locally, which is why building and interpolating are handled by separate modules. To see a more complete list of examples of how to build a look-up table (for any satellite mission or user-defined spectral response) see this [wiki](https://github.com/samsammurphy/6S_emulator/wiki/Build-examples). Here is a short example.

`$ python3 LUT_build.py --wavelength 0.42`

which will build a look-up table for a wavelength of 0.42 microns, it can be interpolated as follows

`$ python3 LUT_interpolate.py  path/to/LUT_directory`

where the 'path/to/LUT_directory' is the full path to the look-up table files ('.lut').
