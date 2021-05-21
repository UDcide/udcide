import * as os from "os";
import * as path from "path";
import * as vscode from "vscode";

const outputChannelName = "UDcide";
export const outputChannel = vscode.window.createOutputChannel(
    outputChannelName
);
export const extensionConfigName = "udcide";
export const udcideDir = path.join(os.homedir(), ".UDcide");
