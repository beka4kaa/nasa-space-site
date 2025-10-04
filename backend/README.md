# NASA Hackathon – Astronautics Data Portal Backend

## Endpoints
- `POST /upload` — загрузка CSV, возвращает JSON (первые 100 строк)
- `GET /download/{filename}` — скачать оригинальный CSV
- `GET /ping` — health-check

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

## Docker
См. корневой README.md
