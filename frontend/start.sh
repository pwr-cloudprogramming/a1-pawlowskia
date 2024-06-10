#!/bin/bash

# Fetch instance metadata
API_URL="http://169.254.169.254/latest/api"
TOKEN=$(curl -X PUT "$API_URL/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 600")
TOKEN_HEADER="X-aws-ec2-metadata-token: $TOKEN"
METADATA_URL="http://169.254.169.254/latest/meta-data"
IP_V4=$(curl -H "$TOKEN_HEADER" -s $METADATA_URL/public-ipv4)

# Update the socket.js file with the correct IP address
echo 'const socket = io("ws://'${IP_V4}':3000");' | cat - /usr/local/apache2/htdocs/js/socket.js > /usr/local/apache2/htdocs/js/temp && mv /usr/local/apache2/htdocs/js/temp /usr/local/apache2/htdocs/js/socket.js

# Start the Apache server
httpd-foreground
