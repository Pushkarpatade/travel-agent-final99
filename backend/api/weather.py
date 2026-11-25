from fastapi import APIRouter, Query
from backend.schemas.schemas import WeatherResponse, WeatherForecastDay
from backend.tools.weather_tool import weather_tool

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("", response_model=WeatherResponse)
def get_weather(destination: str = Query(..., description="Destination city name")):
    res = weather_tool.get_forecast(destination, days=5)
    forecast_days = [
        WeatherForecastDay(
            date=day["date"],
            condition=day["condition"],
            temp_high_c=day["temp_high_c"],
            temp_low_c=day["temp_low_c"],
            rain_probability_pct=day["rain_probability_pct"],
            wind_kmh=day["wind_kmh"],
            icon=day["icon"]
        ) for day in res.get("forecast", [])
    ]
    return WeatherResponse(destination=destination, forecast=forecast_days)
