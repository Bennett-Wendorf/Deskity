import { invoke } from "@tauri-apps/api/core";
import { debug } from "@tauri-apps/plugin-log";

export function setUpdateCommand(command: string | ((args?: any) => any), interval: number, updateCallback: (success: boolean, response: any) => void, args?: any) : () => void {
    let intervalID: number;
    if (typeof command === "string") {
        invoke(command, args).then((response: any) => {
            updateCallback(true, response);
        })
        .catch((error: any) => {
            updateCallback(false, error);
        });
        intervalID = setInterval(() => {
            invoke(command, args)
                .then((response: any) => {
                    updateCallback(true, response);
                })
                .catch((error: any) => {
                    updateCallback(false, error);
                });
        }, interval);
    } else {
        command(args)
            .then((response: any) => {
                updateCallback(true, response);
            })
            .catch((error: any) => {
                updateCallback(false, error);
            });
        intervalID = setInterval(() => {
            command(args)
                .then((response: any) => {
                    updateCallback(true, response);
                })
                .catch((error: any) => {
                    updateCallback(false, error);
                });
        }, interval);
    }
    return () => clearInterval(intervalID);
} 