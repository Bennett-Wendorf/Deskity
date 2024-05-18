// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod settings;
mod widgets { pub mod weather; }

use tauri_plugin_log::{Target, TargetKind};
use chrono::Local;

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    log::debug!("The user is about to be greeted");
    format!("Hello, {}! You've been greeted from Rust!", name)
}

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
        .invoke_handler(tauri::generate_handler![
            greet,
            widgets::weather::get_weather,
            settings::get_setting])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
