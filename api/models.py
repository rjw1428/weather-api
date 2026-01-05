from pydantic import BaseModel, Field
from typing import List, Optional

class WeatherDesc(BaseModel):
    value: str

class WeatherIconUrl(BaseModel):
    value: str

class CurrentCondition(BaseModel):
    feels_like_c: str = Field(..., alias='FeelsLikeC')
    feels_like_f: str = Field(..., alias='FeelsLikeF')
    cloudcover: str
    humidity: str
    local_obs_date_time: str = Field(..., alias='localObsDateTime')
    observation_time: str
    precip_inches: str = Field(..., alias='precipInches')
    precip_mm: str = Field(..., alias='precipMM')
    pressure: str
    pressure_inches: str = Field(..., alias='pressureInches')
    temp_c: str = Field(..., alias='temp_C')
    temp_f: str = Field(..., alias='temp_F')
    uv_index: str = Field(..., alias='uvIndex')
    visibility: str
    visibility_miles: str = Field(..., alias='visibilityMiles')
    weather_code: str = Field(..., alias='weatherCode')
    weather_desc: List[WeatherDesc] = Field(..., alias='weatherDesc')
    weather_icon_url: List[WeatherIconUrl] = Field(..., alias='weatherIconUrl')
    winddir16_point: str = Field(..., alias='winddir16Point')
    winddir_degree: str = Field(..., alias='winddirDegree')
    windspeed_kmph: str = Field(..., alias='windspeedKmph')
    windspeed_miles: str = Field(..., alias='windspeedMiles')

class AreaName(BaseModel):
    value: str

class Country(BaseModel):
    value: str

class Region(BaseModel):
    value: str

class WeatherUrl(BaseModel):
    value: str

class NearestArea(BaseModel):
    area_name: List[AreaName] = Field(..., alias='areaName')
    country: List[Country]
    latitude: str
    longitude: str
    population: str
    region: List[Region]
    weather_url: List[WeatherUrl] = Field(..., alias='weatherUrl')

class Request(BaseModel):
    query: str
    type: str

class Astronomy(BaseModel):
    moon_illumination: str
    moon_phase: str
    moonrise: str
    moonset: str
    sunrise: str
    sunset: str

class Hourly(BaseModel):
    dew_point_c: str = Field(..., alias='DewPointC')
    dew_point_f: str = Field(..., alias='DewPointF')
    feels_like_c: str = Field(..., alias='FeelsLikeC')
    feels_like_f: str = Field(..., alias='FeelsLikeF')
    heat_index_c: str = Field(..., alias='HeatIndexC')
    heat_index_f: str = Field(..., alias='HeatIndexF')
    wind_chill_c: str = Field(..., alias='WindChillC')
    wind_chill_f: str = Field(..., alias='WindChillF')
    wind_gust_kmph: str = Field(..., alias='WindGustKmph')
    wind_gust_miles: str = Field(..., alias='WindGustMiles')
    chanceoffog: str
    chanceoffrost: str
    chanceofhightemp: str
    chanceofovercast: str
    chanceofrain: str
    chanceofremdry: str
    chanceofsnow: str
    chanceofsunshine: str
    chanceofthunder: str
    chanceofwindy: str
    cloudcover: str
    diff_rad: str = Field(..., alias='diffRad')
    humidity: str
    precip_inches: str = Field(..., alias='precipInches')
    precip_mm: str = Field(..., alias='precipMM')
    pressure: str
    pressure_inches: str = Field(..., alias='pressureInches')
    short_rad: str = Field(..., alias='shortRad')
    temp_c: str = Field(..., alias='tempC')
    temp_f: str = Field(..., alias='tempF')
    time: str
    uv_index: str = Field(..., alias='uvIndex')
    visibility: str
    visibility_miles: str = Field(..., alias='visibilityMiles')
    weather_code: str = Field(..., alias='weatherCode')
    weather_desc: List[WeatherDesc] = Field(..., alias='weatherDesc')
    weather_icon_url: List[WeatherIconUrl] = Field(..., alias='weatherIconUrl')
    winddir16_point: str = Field(..., alias='winddir16Point')
    winddir_degree: str = Field(..., alias='winddirDegree')
    windspeed_kmph: str = Field(..., alias='windspeedKmph')
    windspeed_miles: str = Field(..., alias='windspeedMiles')

class Weather(BaseModel):
    astronomy: List[Astronomy]
    avgtemp_c: str = Field(..., alias='avgtempC')
    avgtemp_f: str = Field(..., alias='avgtempF')
    date: str
    hourly: List[Hourly]
    maxtemp_c: str = Field(..., alias='maxtempC')
    maxtemp_f: str = Field(..., alias='maxtempF')
    mintemp_c: str = Field(..., alias='mintempC')
    mintemp_f: str = Field(..., alias='mintempF')
    sun_hour: str = Field(..., alias='sunHour')
    total_snow_cm: str = Field(..., alias='totalSnow_cm')
    uv_index: str = Field(..., alias='uvIndex')

class WeatherData(BaseModel):
    current_condition: List[CurrentCondition]
    nearest_area: List[NearestArea]
    request: List[Request]
    weather: List[Weather]
