FROM node:20

WORKDIR /frontend

COPY package* .

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]