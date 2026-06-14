FROM node:22-alpine
ARG BUILD_MODE
ENV NODE_ENV=production
WORKDIR /app
COPY package.json .
EXPOSE 3000
CMD ["node", "server.js"]
