FROM node:21-bookworm
WORKDIR /frontend
COPY package.json ./
RUN npm i -g bun
RUN bun i
RUN bun i i18next svelte-i18next
RUN bun i http-proxy-middleware
COPY . .
EXPOSE 5173
CMD bun run dev