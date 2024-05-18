use crate::settings;

static BASE_URL: &str = "https://api.openweathermap.org/data/2.5/weather";

#[tauri::command(async)]
pub async fn get_weather() -> Result<String, String> {
    log::debug!("Getting weather");

    let complete_url = format!(
        "{}?appid={}&q={}&units={}",
        BASE_URL,
        settings::SETTINGS.weather_widget.get_api_key(), 
        settings::SETTINGS.weather_widget.get_city_name(), 
        settings::SETTINGS.weather_widget.get_units()
    );

    let response = reqwest::get(&complete_url)
        .await
        .map_err(|e| e.to_string())?
        .error_for_status()
        .map_err(|e| e.to_string())?;
    Ok(response.text().await.unwrap())
}