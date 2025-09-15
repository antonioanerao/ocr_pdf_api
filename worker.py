import os
from redis import Redis
from rq import Worker, Queue

listen = ["ocr"]
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
conn = Redis.from_url(redis_url)

if __name__ == "__main__":
    # Cria as filas e inicia o worker usando a conexão direta
    queues = [Queue(name, connection=conn) for name in listen]
    worker = Worker(queues, connection=conn)
    worker.work()
