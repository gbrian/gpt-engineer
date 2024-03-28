# Start from a Python 3.10 image
FROM debian

# Set the working directory in the container to /app
WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl

# Add the current directory contents into the container at /app
ADD . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Make port 5000 available to the world outside this container
EXPOSE 8001

# Run the command to start uVicorn server and Vite server
CMD ["bash", "/app/gpt-web.sh"]