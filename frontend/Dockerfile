FROM node:20-alpine AS builder

WORKDIR /app

# Install deps (couche mise en cache tant que package.json n'a pas changé)
COPY package.json package-lock.json* ./
RUN npm ci

# Build
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM nginx:1.27-alpine

# Config nginx sur-mesure (SPA routing + gzip + cache)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Exécution en user non-root (bonnes pratiques sécurité)
RUN chown -R nginx:nginx /usr/share/nginx/html \
 && chown -R nginx:nginx /var/cache/nginx \
 && chown -R nginx:nginx /var/log/nginx \
 && chown -R nginx:nginx /etc/nginx/conf.d \
 && touch /var/run/nginx.pid \
 && chown -R nginx:nginx /var/run/nginx.pid
USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
