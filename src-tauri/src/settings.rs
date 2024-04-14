use config::{Config, ConfigError, Environment, File};
use serde::Deserialize;

#[derive(Debug, Deserialize)]
#[allow(unused)]
pub struct ToDoWidget {
    pub update_interval: u32,
    pub show_completed_tasks: bool,
    pub lists_to_use: Vec<String>,
    pub task_sort_order: Vec<String>,
    pub app_id: String,
}

#[derive(Debug, Deserialize)]
#[allow(unused)]
pub struct WeatherWidget {
    pub city_name: String,
    pub units: String,
    pub update_interval: u32,
    pub api_key: String,
}

#[derive(Debug, Deserialize)]
#[allow(unused)]
pub struct SpotifyWidget {
    pub update_interval: u32,
    pub client_id: String,
    pub client_secret: String,
}

#[derive(Debug, Deserialize)]
#[allow(unused)]
pub struct Settings {
    pub to_do_widget: ToDoWidget,
    pub weather_widget: WeatherWidget,
    pub spotify_widget: SpotifyWidget,
}

impl Settings {
    pub fn new() -> Result<Self, ConfigError> {
        let s = Config::builder()
            // Start off by merging in the "default" configuration file
            .add_source(File::with_name("../settings"))
            // Merge in the secrets
            .add_source(File::with_name("../.secrets").required(false))
            // Add in settings from the environment (with a prefix of DESKITY)
            .add_source(Environment::with_prefix("deskity"))
            .build()?;

        // Now that we're done, let's access our configuration
        println!("ToDo Update Interval: {:?}", s.get::<u32>("to_do_widget.update_interval"));
        println!("ToDo Lists: {:?}", s.get::<Vec<String>>("to_do_widget.lists_to_use").unwrap());
        println!("Weather City Name: {:?}", s.get::<String>("weather_widget.city_name").unwrap());

        // You can deserialize (and thus freeze) the entire configuration as
        return s.try_deserialize()
    }
}