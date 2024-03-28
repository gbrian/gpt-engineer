#!/bin/bash
cd /app
uvicorn main:app --host 0.0.0.0 --port 8000
cd /app/gpt_engineer/api/client_chat
npm run dev