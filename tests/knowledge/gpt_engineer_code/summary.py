from gpt_engineer.core.ai import AI

SUMMARY_PROMPT = """
    Summarize this file of type [[EXTENSION]]
    Keep all sensitive information extrict like class names, function names and other relevan information.
    Reduce to the maximum.
    File content:
    [[FILE_CONTENT]]
"""


class Summary:
    def __init__(self, ai: AI):
        self.ai = ai

    def summary_file(self, file_name: str, data: bytes):
        extension = os.path.splitext(file_name)[1]
        file_content = data.decode("utf-8")
        prompt = (
            SUMMARY_PROMPT.strip()
            .replace("[[EXTENSION]]", extension)
            .replace("[[FILE_CONTENT]]", file_content)
        )
        # Send the prompt to the AI and get the summarized content
        summarized_content = AI.summarize(prompt)
        # Add the summarized content to the main summary.txt file
        with open("summary.txt", "r+") as f:
            content = f.read()
            start_index = content.find(f"## FILE: {file_name}")
            end_index = content.find(f"< FILE: {file_name}")
            if start_index != -1 and end_index != -1:
                f.seek(start_index)
                f.write(
                    f"## FILE: {file_name}\n{summarized_content}\n< FILE: {file_name}"
                )
            else:
                f.write(
                    f"\n## FILE: {file_name}\n{summarized_content}\n< FILE: {file_name}"
                )
