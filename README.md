# SprintHealth2024_Hahatonschiki

презентация https://docs.google.com/presentation/d/1DuC5GRlioi0bCzUCeWEtJ0TzfdSXIpHEMvrRuIFYOZw/edit?usp=sharing
**SprintHealth: Инновационный Анализ для Agile-команд**  
Проект команды "Хахатонщики" для хакатона Т1 "Импульс".

---

## Описание

**SprintHealth** — это инструмент для анализа эффективности и здоровья спринтов Agile-команд. Наше решение помогает командам отслеживать и улучшать процессы, выявляя слабые места и оптимизируя производительность.

**Ключевые функции:**

- Анализ данных о задачах в спринте с визуализацией ключевых метрик.
- Расчет "здоровья спринта" на основе статусных изменений задач.
- Поддержка аналитики для нескольких спринтов одновременно.
- Реализовали с объяснением(в презентации) дополнительные метрики для расчета здоровья спринта.

---

## Технологический стек

**Backend:**

- Python: обработка данных и реализация API.
- Библиотеки: Pandas, NumPy, Matplotlib — для анализа и визуализации данных.
- FastAPI: разработка API.

**Frontend:**

- Vue.js: создание динамичного и удобного пользовательского интерфейса.
- Quasar: фреймворк vue.js

**База данных:**

- PostgreSQL: надежное хранилище для данных о задачах и спринтах.

---

## Запуск

### Backend:

1. Перейдите в директорию проекта backend.
2. Запустите сервер с помощью команды:
   ```bash
   uvicorn app.main:app --port 8001

   ```

### Frontend:
0. Установите node и npm;
1. Установите quasar
   $ npm install -g @quasar/cli
3. Перейдите в директорию проекта frontend.
4. Запустите локальный сервер разработки:

   quasar dev

После запуска backend и frontend инструмент будет доступен по адресу [http://localhost:9000](http://localhost:9000).
backend находится на порту 8001, frontend - на порту 9000

---

## Основные функции

1. Загрузка данных:

   - функционал загрузки нескольких файлов
   - интерфейс выбора нужных вам спринтов

2. Визуализация метрик:

   -

3. Расчет здоровья спринта:

   - Подсчет по метрикам(список ниже)

4. Анализ, агрегация и очистка данных
   - Скрипт для очистки файлов с данными(препроцессинг)

---

## Метрики и формулы

### Метрики от организаторов:

#### К выполнению

- **Описание:**  
  Сумма оценок объектов выбранного спринта в статусе категории = "Создано".
  - Для прошлого спринта: последний статус объекта во временные рамки спринта.
  - Для активного спринта: ежедневные изменения статусов объектов.
- **Формат:**  
  Число с одним знаком после запятой.
- **Формула:**
  ```text
  SUM (estimation/3600)
  ```

---

#### В работе

- **Описание:**  
  Сумма оценок объектов последнего активного спринта, не подходящих под критерии "Сделано" и "Снято".
  - Аналогично учитываются изменения статусов для прошлого и активного спринтов.
- **Формат:**  
  Число с одним знаком после запятой.
- **Формула:**
  ```text
  SUM (estimation/3600)
  ```

---

#### Сделано

- **Описание:**  
  Сумма оценок задач и дефектов в статусах "Закрыто", "Выполнено".
  - Исключаются оценки снятых объектов.
- **Формат:**  
  Число с одним знаком после запятой.
- **Формула:**
  ```text
  SUM (estimation/3600)
  ```

---

#### Снято

- **Описание:**  
  Сумма оценок снятых объектов:
  - Статус "Закрыто"/"Выполнено" с резолюцией "Отклонено", "Отменено инициатором", "Дубликат".
  - Для дефектов: статус "Отклонен исполнителем".
- **Формат:**  
  Число с одним знаком после запятой.
- **Формула:**
  ```text
  SUM (estimation/3600)
  ```

---

#### Бэклог изменен с начала спринта

- **Описание:**  
  Процент изменения задач спустя два дня после старта спринта. Исключаются дефекты.
- **Формат:**  
  Процент с одним знаком после запятой.
- **Формула:**
  ```text
  (twoDaysAfterStartOfSprint * 100) / startOfSprint
  ```

---

#### Заблокировано задач

- **Описание:**  
  Сумма оценок объектов с блокирующими связями ("is blocked by"), не находящихся в статусе "Done".
- **Формат:**  
  Число с одним знаком после запятой.

---

#### Исключено

- **Описание:**  
  Сумма оценок и количество задач, исключенных из спринта.
  - Учитывается для каждого дня активного спринта.
- **Формат:**
  - `count`: целое число.
  - `hours`: число с одним знаком после запятой.

---

#### Добавлено

- **Описание:**  
  Сумма оценок и количество задач, добавленных в спринт (включая начало и активный период).
  - Учитывается для каждого дня активного спринта.
- **Формат:**
  - `count`: целое число.
  - `hours`: число с одним знаком после запятой.

---

### Метрики от команды Хахатонщики:

#### Процент завершенных задач (completion_percentage)

- **Описание:**  
  Процент завершенных задач от общего количества задач в спринте.
- **Формат:**  
  Число с одним знаком после запятой.
- **Формула:**
  ```text
  (completed_tasks / total_tasks) * 100
  ```

---

#### Средняя длительность выполнения задач (average_task_duration)

- **Описание:**  
  Среднее время выполнения задач в спринте, выраженное в часах.
- **Формат:**  
  Число с одним знаком после запятой.
- **Формула:**
  ```text
  total_duration / completed_tasks
  ```

---

#### Количество задач, добавленных спустя два дня после старта (added_tasks_after_start)

- **Описание:**  
  Количество задач, добавленных в спринт спустя два дня после его начала.
- **Формат:**  
  Целое число.
- **Формула:**
  ```text
  COUNT(tasks_added_after_start)
  ```

---

#### Исключенные задачи (excluded_tasks)

- **Описание:**  
  Содержит два значения:
  - `count`: количество исключенных задач.
  - `hours`: суммарное время исключенных задач (в часах).
- **Формат:**
  - `count`: целое число.
  - `hours`: число с одним знаком после запятой.
- **Формула:**
  ```text
  COUNT(excluded_tasks), SUM(estimation_hours)
  ```

---

## Контакты

Проект разработан командой "Хахатонщики" для Т1 "Импульс".

Шиняев Евгений, Пронина Надежда, Митрофанова Анна, Альжапарова Альбина.

```

```
