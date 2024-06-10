FROM httpd:latest
RUN apt-get update && apt-get install -y curl
COPY . /usr/local/apache2/htdocs/
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh
EXPOSE 80
ENTRYPOINT ["/usr/local/bin/start.sh"]
