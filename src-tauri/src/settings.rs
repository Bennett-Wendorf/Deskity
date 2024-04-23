use config::{Config, ConfigError, Environment, File};
use serde::Deserialize;
use validator::{Validate, ValidationError};
use lazy_static::lazy_static;

static MICROSOFT_APP_ID: &'static str = "565467a5-8f81-4e12-8c8d-e6ec0a0c4290";

lazy_static! {
    pub static ref SETTINGS: Settings = Settings::new().unwrap_or_else(|e| panic!("Failed to load settings. \n {:?}", e.to_string()));
}

#[derive(Debug, Validate, Deserialize)]
#[allow(unused)]
pub struct ToDoWidget {
    update_interval: Option<u32>,
    show_completed_tasks: Option<bool>,
    lists_to_use: Option<Vec<String>>,
    #[validate(custom(function = "validate_check_sort_order"))]
    task_sort_order: Option<Vec<String>>,
    #[validate(length(equal = 36))]
    app_id: Option<String>,
}

impl ToDoWidget {
    pub fn get_update_interval(&self) -> u32 {
        self.update_interval.unwrap_or(30)
    }

    pub fn get_show_completed_tasks(&self) -> bool {
        self.show_completed_tasks.unwrap_or(false)
    }

    pub fn get_lists_to_use(&self) -> Vec<String> {
        self.lists_to_use.clone().unwrap_or(vec![])
    }

    pub fn get_task_sort_order(&self) -> Vec<String> {
        self.task_sort_order.clone().unwrap_or(vec!["-status".to_string(), "dueDateTime".to_string(), "title".to_string()])
    }

    pub fn get_app_id(&self) -> String {
        self.app_id.clone().unwrap_or(MICROSOFT_APP_ID.to_string())
    }
}

fn validate_check_sort_order(keys: &Vec<String>) -> Result<(), ValidationError> {
    let valid_keys = vec![
        "status".to_string(), "title".to_string(), "id".to_string(), 
        "body".to_string(), "list_id".to_string(), "created_date_time".to_string(), 
        "due_date_time".to_string(), "last_modified_date_time".to_string(), 
        "importance".to_string(), "is_reminder_on".to_string()];
    for key in keys {
        if key.chars().nth(0).unwrap_or_default() == '-' {
            let key = key[1..].to_string();
            if !valid_keys.contains(&key) {
                println!("Invalid sort key {:?}", key);
                return Err(ValidationError::new("Invalid sort key"));
            } else {
                return Ok(());
            }
        }
        if !valid_keys.contains(&key) {
            println!("Invalid sort key {:?}", key);
            return Err(ValidationError::new("Invalid sort key"));
        }
    }
    Ok(())
}

#[derive(Debug, Validate, Deserialize)]
#[allow(unused)]
pub struct WeatherWidget {
    city_name: Option<String>,
    units: Option<String>,
    update_interval: Option<u32>,
    #[validate(length(equal = 32))]
    api_key: String,
}

impl WeatherWidget {
    pub fn get_city_name(&self) -> String {
        self.city_name.clone().unwrap_or("New York".to_string())
    }

    pub fn get_units(&self) -> String {
        self.units.clone().unwrap_or("imperial".to_string())
    }

    pub fn get_update_interval(&self) -> u32 {
        self.update_interval.unwrap_or(600)
    }

    pub fn get_api_key(&self) -> String {
        self.api_key.clone()
    }
}

#[derive(Debug, Validate, Deserialize)]
#[allow(unused)]
pub struct SpotifyWidget {
    update_interval: Option<u32>,
    #[validate(length(equal = 32))]
    client_id: String,
    #[validate(length(equal = 32))]
    client_secret: String,
}

impl SpotifyWidget {
    pub fn get_update_interval(&self) -> u32 {
        self.update_interval.unwrap_or(5)
    }

    pub fn get_client_id(&self) -> String {
        self.client_id.clone()
    }

    pub fn get_client_secret(&self) -> String {
        self.client_secret.clone()
    }
}

#[derive(Debug, Validate, Deserialize)]
#[allow(unused)]
pub struct Settings {
    #[validate(nested)]
    pub to_do_widget: ToDoWidget,
    #[validate(nested)]
    pub weather_widget: WeatherWidget,
    #[validate(nested)]
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

        // You can deserialize (and thus freeze) the entire configuration as
        let settings: Result<Self, ConfigError> =  s.try_deserialize();

        match settings {
            Ok(settings) => {
                settings.validate().map_err(|e| ConfigError::Message(e.to_string())).map(|_| settings)
            },
            Err(e) => Err(e)
        }
    }
}