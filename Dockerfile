FROM node:18-alpine AS react_builder


WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.14 AS runner

WORKDIR /app

COPY server/requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY server/ ./server/
COPY resources/ ./resources/

COPY --from=react_builder /app/dist ./frontend/dist

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]