# ----- deps -----
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ----- builder -----
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Nenhum NEXT_PUBLIC_* aqui: com o BFF o navegador chama /api na mesma origem
# e a URL do backend nunca sai do servidor.
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ----- runner -----
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# standalone output: server.js + deps mínimas; não copia node_modules inteiro.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000

# /api/health fica fora do middleware. A raiz redireciona para o login, e o
# wget seguiria o redirect ate o Keycloak — a saude passaria a depender de
# OUTRO servico.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget --quiet --spider http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
