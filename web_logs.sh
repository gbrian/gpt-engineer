API_PROC_ID=$(pgrep npm)
cat /proc/${API_PROC_ID}/fd/1
