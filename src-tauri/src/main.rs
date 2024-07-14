// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod settings;
mod widgets { pub mod weather; }
mod layout_config;

use tauri::Manager;
use tauri_plugin_log::{Target, TargetKind};
use chrono::Local;

fn main() {
    #[cfg(debug_assertions)]
    let log_targets: [Target; 2] = [
        Target::new(TargetKind::Stdout), 
        Target::new(TargetKind::Webview),
    ];
    
    #[cfg(not(debug_assertions))]
    let log_targets: [Target; 2] = [
        Target::new(TargetKind::Stdout), 
        Target::new(TargetKind::LogDir { file_name: None })
    ];

    tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::new().targets(log_targets)
            .format(|callback, message, record| {
                callback.finish(format_args!(
                    "{}[{:=<30}][{: <5}] {}", 
                    Local::now().format("[%Y-%m-%d][%H:%M:%S]"),
                    format!("{}:{} ", record.file().unwrap_or("svelte"), record.line().unwrap_or(0)),
                    tauri_plugin_log::fern::colors::ColoredLevelConfig::default().color(record.level()), 
                    message))
            })
            .level(log::LevelFilter::Debug)
            .build())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            app.manage(settings::Settings::new()?);

            app.manage(layout_config::new()?);

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            widgets::weather::get_weather,
            settings::get_setting,
            layout_config::get_layout_config])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
