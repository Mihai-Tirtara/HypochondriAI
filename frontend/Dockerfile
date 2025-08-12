# Multi-stage build for React frontend
FROM node:20-alpine AS build

WORKDIR /app

# Accept build arguments
ARG VITE_SUPERUSER_NAME
ENV VITE_SUPERUSER_NAME=$VITE_SUPERUSER_NAME

# Debug: Print the environment variable value
RUN echo "Build arg VITE_SUPERUSER_NAME: $VITE_SUPERUSER_NAME"

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build production artifacts
RUN npm run build

# Verify build output exists
RUN ls -la /app/dist/

# Production stage with Nginx
FROM nginx:alpine AS production

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Verify files were copied
RUN ls -la /usr/share/nginx/html/ && \
    test -f /usr/share/nginx/html/index.html || (echo "ERROR: index.html not found!" && exit 1)

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start Nginx with logging
CMD ["sh", "-c", "echo 'Starting nginx...' && nginx -t && echo 'Nginx config test passed' && nginx -g 'daemon off;'"]
