FROM nginx:alpine

# Copy static frontend assets
COPY index.html /usr/share/nginx/html/index.html
COPY assets/ /usr/share/nginx/html/assets/

# Copy custom Nginx configuration for Cloud Run port 8080
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
