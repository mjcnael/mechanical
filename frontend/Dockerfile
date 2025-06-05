FROM oven/bun

WORKDIR /app

COPY bun.lock .
COPY package.json .

RUN bun install

COPY . .

EXPOSE 3000

CMD ["bun", "run", "dev", "--host"]
