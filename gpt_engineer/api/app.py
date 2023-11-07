from flask import Flask, request, jsonify
from gpt_engineer.core import gtp_engineer

app = Flask(__name__)


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
            use_custom_preprompts=data.get("use_custom_preprompts"),
            ai_cache=data.get("ai_cache"),
            use_git=data.get("use_git"),
            prompt_file=data.get("prompt_file"),
            verbose=data.get("verbose"),
        )
        return jsonify({"message": "Operation completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
