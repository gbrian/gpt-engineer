const vscode = require('vscode');

function activate(context) {
  let disposableWebview = undefined;

  let runTask = vscode.commands.registerCommand('gpt-engineer.runTask', function () {
    if (disposableWebview) {
      disposableWebview.dispose();
    }
    disposableWebview = vscode.window.createWebviewPanel(
      'runTask', 
      'Run Task', 
      vscode.ViewColumn.One, 
      {}
    );
    // Implementation for running a task in webview
  });

  let improveTask = vscode.commands.registerCommand('gpt-engineer.improveTask', function () {
    if (disposableWebview) {
      disposableWebview.dispose();
    }
    disposableWebview = vscode.window.createWebviewPanel(
      'improveTask', 
      'Improve Task', 
      vscode.ViewColumn.One, 
      {}
    );
    // Implementation for improving a task in webview
  });

  let newTask = vscode.commands.registerCommand('gpt-engineer.newTask', function () {
    if (disposableWebview) {
      disposableWebview.dispose();
    }
    disposableWebview = vscode.window.createWebviewPanel(
      'newTask', 
      'New Task', 
      vscode.ViewColumn.One, 
      {}
    );
    // Implementation for creating a new task in webview
  });

  context.subscriptions.push(runTask);
  context.subscriptions.push(improveTask);
  context.subscriptions.push(newTask);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};