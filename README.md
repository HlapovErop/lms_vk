# he*LMS*man - Система управления образовательными курсами

## Запуск проекта

`docker compose up --build`

### Примечания
- Описание ТЗ можно увидеть в [документе с ТЗ](https://drive.google.com/file/d/1Ebto7OIO4k6tQGAqZ5GBml0JPxtt3Iag/view?usp=sharing)
- Swagger-схема находится на корневом маршруте 
- [Swagger-Editor](https://editor.swagger.io/) поддерживает схему лишь частично (разница поддержки схем и requestBody), 
но для ознакомления можно закинуть файл `helmsman_api/djangoapp/swagger.yaml` в [Swagger-Editor](https://editor.swagger.io/)
- Миграции создаются автоматически
- Сиды находятся в `helmsman_api/djangoapp/fixtures/initial_data.json`
- he*LMS*man потому что LMS, и потому что смотрел сериал Сегун во время размышлений о нейминге. Таков путь
