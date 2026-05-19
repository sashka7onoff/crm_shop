FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirments.txt .
RUN pip install -r requirments.txt
COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 8000
CMD ["./entrypoint.sh"]