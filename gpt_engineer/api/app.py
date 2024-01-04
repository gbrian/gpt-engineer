from flask import Flask, jsonify
from gpt_engineer.core import gtp_engineer

app = Flask(__name__)
app_config = {}


def run_api(
    project_path,
    model,
    temperature,
    steps_config,
    improve_mode,
    lite_mode,
    azure_endpoint,
    ai_cache,
    use_git,
    verbose
):
    app_config.update(
        project_path=project_path,
        model=model,
        temperature=temperature,
        steps_config=steps_config,
        improve_mode=improve_mode,
        lite_mode=lite_mode,
        azure_endpoint=azure_endpoint,
        ai_cache=ai_cache,
        use_git=use_git,
        verbose=verbose,
    )
    app.run()


@app.route("/gtp_engineer", methods=["POST"])
def run_gtp_engineer():
    try:
        data = request.get_json()
        gtp_engineer(
            project_path=data.get("project_path"),
            model=data.get("model"),
            temperature=data.get("temperature"),
            steps_config=data.get("steps_config"),
            improve_mode=data.get("improve_mode"),
            lite_mode=data.get("lite_mode"),
            azure_endpoint=data.get("azure_endpoint"),
            ai_cache=data.get("ai_cache"),
            use_git=data.get("use_git"),
            prompt_file=data.get("prompt_file"),
            verbose=data.get("verbose"),
            prompt=data.get("prompt"),
        )
        return jsonify({"message": "Operation completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
