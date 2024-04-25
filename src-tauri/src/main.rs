// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod settings;

use log::warn;
use tauri_plugin_log::{Target, TargetKind};
use chrono::Local;

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    warn!("This is a warning message from Rust");
    format!("Hello, {}! You've been greeted from Rust!", name)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::new().targets([
                Target::new(TargetKind::Stdout),
                Target::new(TargetKind::Webview),
            ])
            .format(|callback, message, record| {
                callback.finish(format_args!(
                    "{}[{}:{}][{}] {}", 
                    Local::now().format("[%Y-%m-%d][%H:%M:%S]"),
                    record.file().unwrap_or("unknown"),
                    record.line().unwrap_or(0),
                    tauri_plugin_log::fern::colors::ColoredLevelConfig::default().color(record.level()), 
                    message))
            })
            .build())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
