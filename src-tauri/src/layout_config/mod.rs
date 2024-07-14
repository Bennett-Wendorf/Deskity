use std::fs::File;
use directories_next::ProjectDirs;
use serde_json::{Map, Value};

#[derive(serde::Deserialize, serde::Serialize)]
struct Widget {
    #[serde(rename = "type")]
    widget_type: String,
    props: Value,
}

#[tauri::command]
pub async fn get_layout_config(state: tauri::State<'_, Value>) -> Result<String, String> {
    Ok(state.to_string())
}

pub fn new() -> Result<Value, String> {
    log::debug!("Getting layout config");

    let mut layout_config_file: Option<String> = None;

    if let Some(proj_dirs) = ProjectDirs::from("com", "bennettwendorf", "deskity") {
        match proj_dirs.config_dir().to_str() {
            Some(config_dir) => {
                // TODO: Give a better error if this file doesn't exist
                layout_config_file = Some(format!("{}/layout.json", config_dir));
            }
            None => { }
        }
    }

    match layout_config_file {
        Some(layout_config_file) => {
            let file = File::open(&layout_config_file).map_err(|e| e.to_string())?;

            let contents: Value = serde_json::from_reader(file).map_err(|e| e.to_string())?;

            validate_object(&contents)?;

            Ok(contents)
        }
        None => {
            Err("Failed to find layout config file".to_string())
        }
    } 
}

fn validate_object(object: &Value) -> Result<(), String> {
    log::debug!("Validating layout config object");

    let widget: Widget = serde_json::from_value(object.clone())
        .map_err(|e| e.to_string())?;

    log::debug!("Validating widget of type: {}", widget.widget_type);

    validate_widget(&widget)
}

fn validate_widget(widget: &Widget) -> Result<(), String> {
    let props = widget.props.as_object();

    match props {
        Some(map) => {
            match widget.widget_type.as_str() {
                "hsplit" => {
                    validate_hsplit(map)
                },
                "vsplit" => {
                    validate_vsplit(map)
                },
                _ => { Ok(())}
            }
        },
        None => {
            Err(format!("props must be an object for widget of type: {0}", widget.widget_type))
        }
    }
}

fn validate_recursive_props(widget_type: &str, key: &str, props: &Map<String, Value>) -> Result<(), String> {
    match props.get(key) {
        Some(value) => {
            let widget: Widget = serde_json::from_value(value.clone())
                .map_err(|e| e.to_string())?;

            log::debug!("Validating widget of type: {}", widget.widget_type);

            validate_widget(&widget)
        },
        None => {
            Err(format!("{widget_type} widgets must contain a \"{key}\" property"))
        }
    }
}

fn validate_hsplit (props: &Map<String, Value>) -> Result<(), String> {
    log::debug!("Validating hsplit widget props");
    
    validate_recursive_props("hsplit", "left", props)?;

    validate_recursive_props("hsplit", "right", props)?;

    Ok(())
}

fn validate_vsplit (props: &Map<String, Value>) -> Result<(), String> {
    log::debug!("Validating vsplit widget props");

    validate_recursive_props("vsplit", "top", props)?;

    validate_recursive_props("vsplit", "bottom", props)?;

    Ok(())
}