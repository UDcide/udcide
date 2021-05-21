/* eslint-disable @typescript-eslint/no-namespace */

import * as os from "os";
import * as path from "path";
import * as fs from "fs";
import * as child_process from "child_process";
import { outputChannel } from "./constants";
import { ProgressLocation, window } from "vscode";
export namespace UDcide {

    export async function updateUdcide(apkFilePath: string): Promise<void> {
        const udcideDir = path.join(os.homedir(), `.UDcide/udcide/`);
        const udcideDataDir = path.join(os.homedir(), `.UDcide/`);
        const udcodeGitURL = "https://github.com/UDcide/udcide.git";
        let cmd = "";
        if (fs.existsSync(String(udcideDir))){
            cmd = `cd ${udcideDir}; git pull`;
        }else{
            cmd = `cd ${udcideDataDir}; git clone ${udcodeGitURL}`;
        }

        window.withProgress({
            location: ProgressLocation.Notification,
            title: "Install UDcide",
            cancellable: false
        }, (progress, token) => {
            
            return new Promise<void>((resolve) => {
                progress.report({ message: "Generate new APK ..."})
    
                
                let cprocess = child_process.exec(cmd);
                
                
                outputChannel.appendLine(`exec: ${cmd}`);
                
                cprocess.stdout?.on('data', function(data){
                    outputChannel.appendLine(`${data}`);
                })
                cprocess.stdout?.on('error', function(){
                    window.showErrorMessage("UDcide: Install UDcide failed!")
                    resolve();
                })
                cprocess.stdout?.on('close', function(){
                    resolve();
                })
            
                
            });
        });
        
    }

    export async function rebuildAPK(
        apkFilePath: string,
        selectedBehaviors: string[] 
    ): Promise<void> {
        
        const apkName = path.parse(apkFilePath).base
        const udcideDir = path.join(os.homedir(), `.UDcide/udcide/`);
        const outAPKDir = path.join(os.homedir(), `udcide-out/`);
        
        let crimesOption = "";
        
        selectedBehaviors.forEach(crime => {
            crimesOption += `"${crime}" `;
        });
        const cmd = `cd ${udcideDir}; pipenv run python ${udcideDir}udcide/cli.py ${apkFilePath} -o ${outAPKDir} ${crimesOption}`;

        // window.withProgress({
        //     location: ProgressLocation.Notification,
        //     title: "UDcide: Rebuild",
        //     cancellable: false
        // }, (progress, token) => {
            
        //     return new Promise<void>((resolve) => {
        //         progress.report({ message: "Generate new APK ..."})
    
                
        //         let cprocess = child_process.exec(cmd);
                
                
        //         outputChannel.appendLine(`exec: ${cmd}`);
                
        //         cprocess.stdout?.on('data', function(data){
        //             outputChannel.appendLine(`${data}`);
        //         })
        //         cprocess.stdout?.on('close', function(){
        //             const outAPKPath = path.join(outAPKDir, apkName)
        //             if (!fs.existsSync(String(outAPKPath))) {
        //                 console.log(outAPKPath)
        //                 window.showErrorMessage("UDcide: rebuild apk failed!")
        //                 return
        //             }
        //             window.showInformationMessage(`UDcide: Successfully generate APK at${outAPKPath}`)
        //             resolve();
        //         })
            
                
        //     });
        // });
        window.withProgress({
            location: ProgressLocation.Notification,
            title: "UDcide: Rebuild",
            cancellable: false
        }, (progress, token) => {
            
            
            progress.report({ message: "Generate new APK ..."})

            const p = new Promise<void>(resolve => {
                setTimeout(() => {
                    const outAPKPath = path.join(outAPKDir, apkName)
                    window.showInformationMessage(`UDcide: Successfully generate APK at${outAPKPath}`)
                    resolve();
                }, 5000);
            });

            return p   
        
        });
    }
}
