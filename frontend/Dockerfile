# Use an official Node.js runtime as a parent image
FROM node:21.6.0

# Set the working directory in the container
WORKDIR /

# Copy the frontend files into the container
COPY . .

# Install http-server globally
RUN npm install -g http-server

# Expose port 8080 to the outside world
EXPOSE 8080

# Command to run the http-server and serve the HTML file with CORS enabled
CMD ["http-server", "./src", "--cors", "-p", "8080"]
