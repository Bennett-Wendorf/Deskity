import { invoke } from "@tauri-apps/api/core";
import { debug } from "@tauri-apps/plugin-log";

export function setUpdateCommand(command: string | ((args?: any) => any), interval: number, updateCallback: (success: boolean, response: any) => void, args?: any) : () => void {
    let intervalID: number;
    debug(`Setting update command with interval: ${interval}ms`);
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
        debug(`Identified command as function`);
        command(args)
            .then((response: any) => {
                debug(`Initial command response: ${JSON.stringify(response)}. Running update callback...`);
                updateCallback(true, response);
            })
            .catch((error: any) => {
                updateCallback(false, error);
            });
        intervalID = setInterval(() => {
            command(args)
                .then((response: any) => {
                    debug(`Update command response: ${JSON.stringify(response)}. Running update callback...`);
                    updateCallback(true, response);
                })
                .catch((error: any) => {
                    updateCallback(false, error);
                });
        }, interval);
    }
    return () => clearInterval(intervalID);
} 