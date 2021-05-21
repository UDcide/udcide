import * as vscode from 'vscode';
import * as path from "path";
import * as os from "os";
import * as fs from "fs";
import { Quark } from './quark-engine';
import { UDcide } from './udcide';

export function activate(context: vscode.ExtensionContext) {
	const quarkAnalysis = vscode.commands.registerCommand(
		'extension.UDcide', 
		async () => {
			const udcideDir = path.join(os.homedir(), `.UDcide/`);
			if (!udcideDir || !fs.existsSync(String(udcideDir))) {
				if (!fs.existsSync(String(udcideDir))) {
					fs.mkdirSync(udcideDir);
				}
			}
			vscode.window.showInformationMessage('Activated UDcide extension!');
			Quark.openApkFile();
	});
	context.subscriptions.push(
        quarkAnalysis
    );
}
