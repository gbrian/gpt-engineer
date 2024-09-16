API_PROC_ID=$(pgrep gpt-engineer)
cat /proc/${API_PROC_ID}/fd/1
