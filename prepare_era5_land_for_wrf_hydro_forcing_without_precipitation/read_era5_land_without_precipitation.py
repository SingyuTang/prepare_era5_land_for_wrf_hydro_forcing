import xarray as xr # process netcdf files
import pandas as pd 
import numpy as np
import math
import os 

era5_path = r'./nc_data'
era5_list = os.listdir(era5_path)

for i, item in enumerate(era5_list):
    item = os.path.join(era5_path, item) # concentrate ncfile path
    every_data = xr.open_dataset(item) # read monthly data 
    for j, jtem in enumerate(every_data.time): # disaggreated
        hr_dataset = every_data.isel(time=j) # select single time

        # solor radiation
        hr_dataset.variables['ssrd'][:] = hr_dataset.variables['ssrd'][:] / 3600 # J m**-2 unit to W m**-2 
        hr_dataset.variables['strd'][:] = hr_dataset.variables['strd'][:] / 3600 
        hr_dataset.variables['ssrd'].attrs['units'] = 'W m**-2' # update unit name
        hr_dataset.variables['strd'].attrs['units'] = 'W m**-2' 

        # Convert Tdew into Specific humidity, through water vapor pressure from through FAO-56 formula https://www.fao.org/3/X0490E/x0490e07.htm#TopOfPage  (formula: 14)
        Td = hr_dataset.variables['d2m'][:] - 273.15 # read Tdew
        SP = hr_dataset.variables['sp'][:] # unit is pa
        ea = 0.6108*(math.e**(17.27*Td/(Td+237.3)))*1000 # kPa unit to Pa 
        specific_humidity = 0.622*ea / (SP - 0.378*ea)
        hr_dataset.variables['d2m'][:] = specific_humidity # replace fields
        hr_dataset = hr_dataset.rename_vars({'d2m': 'shum'}) # replace fields name d2m to shum
        hr_dataset.variables['shum'].attrs['units'] = 'kg kg-1' # update unit
        hr_dataset.variables['shum'].attrs['long_name'] = 'Specific humidity' # update fields long_name

        # Convert U10/V10 into U2/V2, through FAO-56 formula https://www.fao.org/3/X0490E/x0490e07.htm#TopOfPage  (formula: 47)
        hr_dataset.variables['u10'][:] = hr_dataset.variables['u10'][:] * 4.87 / math.log(67.8 * 10 - 5.42)
        hr_dataset.variables['v10'][:] = hr_dataset.variables['v10'][:] * 4.87 / math.log(67.8 * 10 - 5.42)
        hr_dataset.variables['u10'].attrs['long_name'] = '2 metre U wind component' # update unit name
        hr_dataset.variables['v10'].attrs['long_name'] = '2 metre V wind component'
        hr_dataset = hr_dataset.rename_vars({'u10': 'u2'}) # replace fields name u10 to u2
        hr_dataset = hr_dataset.rename_vars({'v10': 'v2'})

        # notice netcdf encoding
        outputname = os.path.join('./input_files1', 'ERA5_025_1H.' + pd.to_datetime(hr_dataset.time.values).strftime('%Y%m%d.%H00') + '.nc4')
        hr_dataset.to_netcdf(outputname, encoding={'ssrd': {'dtype': 'float32', '_FillValue': -32767, 'missing_value': -32767,}, 
                                                   'strd': {'dtype': 'float32', '_FillValue': -32767, 'missing_value': -32767,},
                                                   'shum': {'dtype': 'float32', '_FillValue': -32767, 'missing_value': -32767,},
                                                   'sp': {'dtype': 'float32', '_FillValue': -32767, 'missing_value': -32767,},
                                                   't2m': {'dtype': 'float32', '_FillValue': -32767, 'missing_value': -32767,},
                                                   'u2': {'dtype': 'float32', '_FillValue': -32767, 'missing_value': -32767,},
                                                   'v2': {'dtype': 'float32', '_FillValue': -32767, 'missing_value': -32767,},
                                                    })
