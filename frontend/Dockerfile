FROM node:lts-iron

# Create app directory
WORKDIR /frontend

# Copy package.json and package-lock.json
COPY package*.json ./

# Use ali source
# RUN npm config set registry http://registry.npm.taobao.org

# Install dependencies
RUN npm install

# Copy the rest of the files
COPY . .

# Expose the port
EXPOSE 5173

CMD npm run dev