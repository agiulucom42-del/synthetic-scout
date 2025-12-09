# Synthetic Scout

Synthetic Scout, API/servis sağlık kontrollerini, SSL sertifika takibini, içerik doğrulamalarını ve temel DB ping testlerini aynı Docker imajı içinde koşturan hafif bir sentetik izleme aracıdır. Slack/Telegram bildirimleriyle uyarı akışı sağlar.

## Özellikler
- HTTP smoke testleri (`/health`, `/auth/login`) + performans ölçümü
- SSL sertifika bitiş süresi kontrolü
- İçerikte keyword doğrulaması
- TCP tabanlı DB ping (PostgreSQL, Redis vb.)
- Slack ve Telegram için webhook bildirim plugin’leri
- Fake/real API seçimli HTTP istemcisi (env ile kontrol edilir)

## Hızlı Başlangıç
```bash
# Varsayılan olarak fake API ile lokal çalıştırma
docker build --no-cache -t synthetic-scout .
docker run --rm synthetic-scout
```

Gerçek uçlara karşı koşmak için `.env` dosyası oluştur:
```
ENV=prod
BASE_API_URL=https://status.example.com
IT_TESTER_USE_FAKE_API=0
API_AUTH_TOKEN=...
SSL_EXPIRY_THRESHOLD_DAYS=10
SSL_ENDPOINTS=["status.example.com:443"]
CONTENT_CHECKS=[{"path":"/health","keyword":"status"}]
DB_PINGS=[{"name":"primary","host":"db.internal","port":5432}]
SLACK_WEBHOOK_URL=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```
Ardından:
```bash
docker run --rm --env-file .env synthetic-scout
```

## Parametreler
- `IT_TESTER_USE_FAKE_API`: `1` olduğunda yerleşik fake istemci kullanılır.
- `SSL_ENDPOINTS`: JSON dizi (host:port formatı). Sertifika bitişi eşik altına düşerse test fail olur.
- `CONTENT_CHECKS`: JSON dizi `{ "path": "/health", "keyword": "status" }` formatında.
- `DB_PINGS`: JSON dizi `{ "name": "redis", "host": "cache", "port": 6379 }` formatında.

## Geliştirme
```bash
pip install -r requirements.txt
python main.py --format all
```
Tag bazlı çalıştırma:
```bash
python main.py --tag ssl --format json
```

Dashboard (HTML rapor görüntüleme):
```bash
python main.py --format all
python -m web.dashboard
```

## Plugin Yazmak
`plugins/` altında `get_plugin()` fonksiyonu döndüren bir sınıf tanımla. Örnekler:
- `plugins/console_plugin.py`
- `plugins/slack_plugin.py`
- `plugins/telegram_plugin.py`

## Dağıtım Önerisi
Railway/Render gibi Docker destekli platformlara `Dockerfile` ile deploy edebilirsin. Environment değişkenlerini platformun secrets bölümüne eklemeyi unutma.
