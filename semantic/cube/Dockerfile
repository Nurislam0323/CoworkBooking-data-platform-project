    FROM cubejs/cube:v0.36
    WORKDIR /cube/conf
    COPY package*.json ./
    RUN npm install --omit=dev || true
    COPY schema ./schema
