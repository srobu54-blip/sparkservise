# SPARK — сайт сервисного центра Apple (Одесса)

Статический лендинг сервисного центра SPARK: ремонт iPhone, MacBook, iMac,
Apple Watch, iPad и AirPods. Стили и скрипты вынесены из HTML в отдельные файлы.

## Структура

```
sparkservice/
├── index.html              # разметка страницы
├── css/
│   └── styles.css          # все стили
├── js/
│   └── main.js             # калькулятор цен, формы, модалка, появление CTA-бара
├── assets/
│   └── img/
│       ├── logo.png         # логотип для шапки
│       └── logo-footer.png  # логотип для футера
├── robots.txt
├── .gitignore
└── README.md
```

JSON-LD разметка (Organization, FAQ, ElectronicsStore) намеренно осталась
внутри `index.html` в `<head>` — так правильно для SEO.

## Локальный просмотр

Поскольку css/js/картинки теперь внешние, открывайте через локальный сервер:

```bash
python3 -m http.server 8000
# затем откройте http://localhost:8000
```

## Загрузка в GitHub

```bash
cd sparkservice
git init
git add .
git commit -m "Initial commit: SPARK landing"
git branch -M main
git remote add origin <URL-вашего-репозитория>
git push -u origin main
```

## Деплой на GitHub Pages

В репозитории: **Settings → Pages → Source: Deploy from a branch → Branch: `main`,
папка `/ (root)` → Save**. Через пару минут сайт будет на
`https://<ваш-ник>.github.io/<репозиторий>/`.

Для своего домена (sparkservice.od.ua) добавьте файл `CNAME` с доменом
и настройте DNS у регистратора.
