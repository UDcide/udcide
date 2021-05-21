/* eslint-disable @typescript-eslint/no-namespace */
import * as os from "os";
import * as path from "path";
import * as fs from "fs";
import * as child_process from "child_process";
import * as vscode from "vscode";
import { outputChannel } from "./constants";
import { quarkSummaryReportHTML } from "./quark-html";
import { UDcide } from "./udcide";
import { window } from "vscode";

function executeProcess(title: string, cmd: string): Thenable<void> {
    return window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: title,
        cancellable: false
    }, (progress, token) => {
        return new Promise<void>((resolve) => {
            progress.report({ increment: 1 });

            try {
                child_process.exec(cmd);
                outputChannel.appendLine(`exec: ${cmd}`);
            } catch (error) {
                outputChannel.appendLine(`Caught error from Udcide install check`);
                outputChannel.append(String(error)); 
            }
            resolve();
        });
    });
}

function parseReport(reportPath: string) {
    const quarkReportJSON: any = JSON.parse(
        fs.readFileSync(reportPath, "utf8")
    );
    const crimes = quarkReportJSON.crimes;

    const report: { [key: string]: any } = {};

    for (let crimeIndex = 0; crimeIndex < crimes.length; crimeIndex++) {
        const crimeObj = crimes[crimeIndex];
        const crimeId = `c${crimeIndex}`;

        if (crimeObj.confidence == "100%") {
            const newFunctionObj: { [key: string]: any } = {};

            for (
                let functionIndex = 0;
                functionIndex < crimeObj.register.length;
                functionIndex++
            ) {
                const functionObj = crimeObj.register[functionIndex];
                const [items] = Object.entries(functionObj);
                const parentFunction: string[] = items[0].split(" ");
                const apiCalls: any = items[1];

                const parentClassName = parentFunction[0].replace(";", "");
                delete parentFunction[0];
                const parentMethodName: string = parentFunction.join("");
                const functionId = `${crimeId}-f${functionIndex}`;

                newFunctionObj[functionId] = {
                    function: {
                        class: parentClassName,
                        method: parentMethodName,
                    },
                    apis: [apiCalls["first"], apiCalls["second"]],
                };
            }

            report[crimeId] = {
                crime: crimeObj.crime,
                score: crimeObj.score,
                weight: crimeObj.weight,
                confidence: crimeObj.confidence,
                api_call: newFunctionObj,
            };
        }
    }
    return report;
}

export namespace Quark {

     export async function openApkFile(): Promise<void> {

        const result = await window.showOpenDialog({
            canSelectFolders: false,
            filters: {
                APK: ["apk"],
            },
            openLabel: "Select an APK file",
        });
        if (result && result.length === 1) {

            // project directory name
            const apkFilePath = result[0].fsPath;

            let projectDir = path.join(
                path.dirname(apkFilePath),
                "udcide-out"
            );

            // don't delete the existing dir if it already exists
            while (fs.existsSync(projectDir)) {
                projectDir = projectDir + "1";
            }

            // quark analysis
            await Quark.analyzeAPK(apkFilePath);
            

        } else {
            outputChannel.appendLine("UDcide: no APK file was chosen");
        }
    }
    
    export function checkQuarkInstalled(): boolean {
        const cmd = "quark";

        outputChannel.appendLine(`exec: ${cmd}`);

        try {
            child_process.execSync(cmd);
            return true;
        } catch (error) {
            outputChannel.appendLine(`Caught error from Quark install check`);
            outputChannel.append(String(error));
            return false;
        }
    }

    export async function analyzeAPK(
        apkFilePath: string,
    ): Promise<void> {

        const jsonReportPath = path.join(
            os.homedir(), 
            `.UDcide/quarkReport.json`
        );
        
        const cmd = `quark -a ${apkFilePath} -o ${jsonReportPath}`;

        await executeProcess(
            `Quark analysis: Analyzing ${apkFilePath}`, cmd
        );
				
        const quarkReportFile = path.join(
            os.homedir(),
            ".UDcide/quarkReport.json"
        );
        if (fs.existsSync(quarkReportFile)) {
            showSummaryReport(quarkReportFile, apkFilePath);
        }
            
    }

    export async function showSummaryReport(reportPath: string, apkFilePath:string): Promise<void> {

        const report: { [key: string]: any } = parseReport(reportPath);


        const panel = vscode.window.createWebviewPanel(
            "quark summary report",
            "Quark Summary Report",
            vscode.ViewColumn.One,
            {
                enableScripts: true,
            }
        );

        panel.webview.html = quarkSummaryReportHTML(report);
        // Handle messages from the webview
        panel.webview.onDidReceiveMessage((message) => {
            switch (message.command) {
                case "rebuild":
                    
                    // UDcide.updateUdcide(apkFilePath);
                    UDcide.rebuildAPK(apkFilePath, message.crimes);
                    break;
            }
        });
    }
}
