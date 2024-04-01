const vscode = require('vscode');
const outputChannel = vscode.window.createOutputChannel("gpt-engineer");

const log = (...args) => outputChannel.appendLine(args.map(JSON.stringify).join(" "))

class GPTViewProvider {

	static viewType = 'gptExtensionTabView';
	_view;

	constructor(
		_extensionUri,
	) { }

	resolveWebviewView(
		webviewView,
		context,
		_token,
	) {
		log("resolveWebviewView")

		this._view = webviewView;

		webviewView.webview.options = {
			// Allow scripts in the webview
			enableScripts: true,

			localResourceRoots: [
				this._extensionUri
			]
		};
		const settings = vscode.workspace.getConfiguration('gptengineer');
		
		this._getHtmlForWebview(webviewView.webview, settings).then(html => {
			webviewView.webview.html = html;
			log("_getHtmlForWebview ", settings, html)
			webviewView.webview.onDidReceiveMessage(data => {
				log("onDidReceiveMessage ", data)
			});
		})
	}

	async _getHtmlForWebview(webview, settings) {
		// const res = await fetch(settings.url)
		// return res.text()
		// fetch setting.url and return the html
		return settings.url ? `
		<html>
			<head>
				<style>
					html, body, iframe {
						border:none;
						width:99% !important;
						height:100% !important
					}
				</style>
			</head>
			<body>
				<iframe src="${settings.url}" />
			</body>
		</html>` : '<h2>Please set gpt-engineer extension settings</h2>'
	}
}

function getNonce() {
	let text = '';
	const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	for (let i = 0; i < 32; i++) {
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}
	return text;
}

function activate(context) {
    log("Activating extension");
	try {
		const provider = new GPTViewProvider(context.extensionUri);
		log("Create provider");

		context.subscriptions.push(
			vscode.window.registerWebviewViewProvider(GPTViewProvider.viewType, provider));
		
		log("Provider registered");
	} catch (ex) {
		log("Error activating extension: " + ex);
	}
}

function deactivate () {
}

module.exports = {
	activate,
	deactivate
}