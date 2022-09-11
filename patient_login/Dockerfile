FROM node:12.18.1
WORKDIR /usr/src/app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install 
COPY . .
EXPOSE 3001
CMD [ "npm", "start" ]