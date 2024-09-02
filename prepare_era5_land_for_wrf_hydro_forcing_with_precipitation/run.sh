mkdir input_files1

python read_era5_land_with_precipitaion.py

ncl 'interp_opt="bilinear"' 'srcGridName="input_files1/ERA5_025_1H.20060601.0100.nc4"' 'dstGridName="geo_em.d03.nc"' ERA52WRFHydro_generate_weights.ncl

ncl 'srcFileName="*.nc4"' 'dstGridName="geo_em.d03.nc"' ERA52WRFHydro_regrid.ncl
