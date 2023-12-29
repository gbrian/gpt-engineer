const vscode = require('vscode');

function activate(context) {
  let runTask = vscode.commands.registerCommand('gpt-engineer.runTask', function () {
    vscode.window.showInformationMessage('Running Task...');
    // Implementation for running a task
  });

  let improveTask = vscode.commands.registerCommand('gpt-engineer.improveTask', function () {
    vscode.window.showInformationMessage('Improving Task...');
    // Implementation for improving a task
  });

  let newTask = vscode.commands.registerCommand('gpt-engineer.newTask', function () {
    vscode.window.showInformationMessage('Creating New Task...');
    // Implementation for creating a new task
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