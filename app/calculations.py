from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .models import Entity, Sprint, History

def calculate_metrics(db: Session, sprint_id: int):
    # Получаем данные спринта
    sprint = db.query(Sprint).filter(Sprint.sprint_id == sprint_id).first()
    if not sprint:
        return None

    # Проверяем, является ли спринт активным
    is_active_sprint = sprint.start_date <= datetime.now() <= sprint.end_date

    # Получаем все задачи, связанные со спринтом
    entities = db.query(Entity).join(History, Entity.entity_id == History.entity_id).filter(
        History.history_date >= sprint.start_date,
        History.history_date <= sprint.end_date,
        History.history_property_name == 'Спринт',
        History.history_change == sprint.sprint_name  # Используем имя спринта для фильтрации
    ).all()

    # Если нет задач с историей изменений в рамках спринта, используем задачи, созданные или обновлённые в спринте
    if not entities:
        entities = db.query(Entity).filter(
            Entity.create_date <= sprint.end_date,
            (Entity.update_date >= sprint.start_date) | (Entity.update_date == None)
        ).all()

    # Словарь для хранения последнего статуса каждой задачи
    entity_statuses = {}
    for entity in entities:
        status_histories = db.query(History).filter(
            History.entity_id == entity.entity_id,
            History.history_property_name == 'Статус',
            History.history_date >= sprint.start_date,
            History.history_date <= sprint.end_date
        ).order_by(History.history_date.desc()).all()

        if status_histories:
            # Извлекаем новый статус из последнего изменения
            last_change = status_histories[0].history_change
            if '->' in last_change:
                old_status, new_status = last_change.split('->')
                new_status = new_status.strip()
            else:
                new_status = last_change.strip()
            last_status = new_status
        else:
            last_status = entity.status  # Если нет истории, используем текущий статус задачи
        entity_statuses[entity.entity_id] = {
            'entity': entity,
            'status': last_status
        }

    # Инициализируем метрики
    metrics = {
        'to_do': 0.0,
        'in_progress': 0.0,
        'done': 0.0,
        'removed': 0.0,
        'backlog_changed_percentage': 0.0,
        'blocked_tasks': 0.0,
        'completion_percentage': 0.0,
        'average_task_duration': 0.0,
        'added_tasks_after_start': 0,
        'excluded_tasks': {'count': 0, 'hours': 0.0},
        'sprint_health_index': 0.0,
        'done_tasks_over_time': {},
        'last_day_done_percentage': 0.0,
        'to_do_percentage': 0.0,
        'removed_percentage': 0.0
    }

    # Подсчёт метрик
    estimation_at_start = 0.0
    estimation_after_two_days = 0.0
    total_duration = 0.0
    completed_tasks = 0
    total_tasks = len(entity_statuses)

    total_estimation_hours = 0.0  # Общая суммарная оценка задач

    current_date = datetime.now() if is_active_sprint else sprint.end_date

    # Получаем даты спринта
    sprint_days = (sprint.end_date - sprint.start_date).days + 1
    sprint_dates = [sprint.start_date + timedelta(days=i) for i in range(sprint_days)]

    # Инициализируем словарь для хранения количества задач "Сделано" по датам
    done_tasks_over_time = {date.strftime('%Y-%m-%d'): 0 for date in sprint_dates}

    for data in entity_statuses.values():
        entity = data['entity']
        status = data['status']
        estimation = entity.estimation or 0.0

        estimation_hours = float(estimation) / 3600

        total_estimation_hours += estimation_hours  # Общая оценка


        # Логика определения категорий задач с исправленными статусами
        if status in ['created', 'to do']:
            metrics['to_do'] += estimation_hours
        elif status in ['in progress', 'analysis', 'fixing', 'testing', 'st', 'stCompleted', 'ift', 'at', 'introduction', 'development', 'readyForDevelopment', 'design']:
            metrics['in_progress'] += estimation_hours
        elif status in ['closed']:
            if entity.resolution in ['Отклонено', 'Отменено инициатором', 'Дубликат', 'Отклонен исполнителем']:
                metrics['removed'] += estimation_hours
            else:
                metrics['done'] += estimation_hours
                completed_tasks += 1
                if entity.create_date and entity.update_date:
                    total_duration += (entity.update_date - entity.create_date).total_seconds() / 3600  # Время выполнения в часах
        else:
            metrics['in_progress'] += estimation_hours

        # Подсчет бэклога
        if entity.create_date <= sprint.start_date + timedelta(days=2):
            estimation_at_start += estimation_hours
        elif sprint.start_date + timedelta(days=2) < entity.create_date <= current_date:
            estimation_after_two_days += estimation_hours

        # Подсчёт задач, добавленных после начала спринта
        if entity.create_date > sprint.start_date + timedelta(days=2):
            metrics['added_tasks_after_start'] += 1  # Увеличиваем счётчик

        # Исключённые задачи
        if hasattr(entity, 'is_excluded') and entity.is_excluded:
            metrics['excluded_tasks']['count'] += 1
            metrics['excluded_tasks']['hours'] += estimation_hours

        # Сбор данных о задачах "Сделано" по датам с исправлениями
        status_histories = db.query(History).filter(
            History.entity_id == entity.entity_id,
            History.history_property_name == 'Статус',
            History.history_date >= sprint.start_date,
            History.history_date <= sprint.end_date
        ).order_by(History.history_date).all()

        if status_histories:
            for history in status_histories:
                date_str = history.history_date.strftime('%Y-%m-%d')
                if '->' in history.history_change:
                    old_status, new_status = history.history_change.split('->')
                    new_status = new_status.strip()
                else:
                    new_status = history.history_change.strip()

                if new_status == 'closed' and date_str in done_tasks_over_time:
                    done_tasks_over_time[date_str] += 1
        else:
            # Проверяем, что задача была закрыта в течение спринта
            if status == 'closed' and sprint.start_date <= entity.update_date <= sprint.end_date:
                date_str = entity.update_date.strftime('%Y-%m-%d')
                if date_str in done_tasks_over_time:
                    done_tasks_over_time[date_str] += 1

    # Добавляем данные в метрики
    metrics['done_tasks_over_time'] = done_tasks_over_time

    # Процент выполнения
    if total_tasks > 0:
        metrics['completion_percentage'] = round((completed_tasks / total_tasks) * 100, 1)
    else:
        metrics['completion_percentage'] = 0.0

    # Средняя длительность выполнения задач
    if completed_tasks > 0:
        metrics['average_task_duration'] = round(total_duration / completed_tasks, 1)
    else:
        metrics['average_task_duration'] = 0.0

    # Процент изменения бэклога
    if estimation_at_start > 0:
        backlog_change_percentage = (estimation_after_two_days * 100) / estimation_at_start
        metrics['backlog_changed_percentage'] = round(backlog_change_percentage, 1)
    else:
        metrics['backlog_changed_percentage'] = 0.0


    # Округляем метрики до одного знака после запятой
    metrics['to_do'] = round(metrics['to_do'], 1)
    metrics['in_progress'] = round(metrics['in_progress'], 1)
    metrics['done'] = round(metrics['done'], 1)
    metrics['removed'] = round(metrics['removed'], 1)
    metrics['blocked_tasks'] = round(metrics['blocked_tasks'], 1)

    # Вычисляем процентные показатели "К выполнению" и "Снято" от общего объёма
    if total_estimation_hours > 0:
        to_do_percentage = (metrics['to_do'] / total_estimation_hours) * 100
        removed_percentage = (metrics['removed'] / total_estimation_hours) * 100
    else:
        to_do_percentage = 0.0
        removed_percentage = 0.0

    metrics['to_do_percentage'] = round(to_do_percentage, 1)
    metrics['removed_percentage'] = round(removed_percentage, 1)

    # Определение массового перевода задач в последний день
    last_day = sprint.end_date.strftime('%Y-%m-%d')
    tasks_done_last_day = metrics['done_tasks_over_time'].get(last_day, 0)
    total_done_tasks = sum(metrics['done_tasks_over_time'].values())

    if total_done_tasks > 0:
        last_day_done_percentage = (tasks_done_last_day / total_done_tasks) * 100
    else:
        last_day_done_percentage = 0.0

    metrics['last_day_done_percentage'] = round(last_day_done_percentage, 1)

    # Расчёт Индекса Здоровья Спринта с учётом скорректированных штрафов
    sprint_health_index = 100.0  # Начальное значение

    # Штраф за "К выполнению" > 20%
    if metrics['to_do_percentage'] > 20:
        penalty = (metrics['to_do_percentage'] - 20) * 0.5  # Штраф 0.5% за каждый процент сверх 20%
        if penalty > 10:
            penalty = 10  # Максимальный штраф 10%
        sprint_health_index -= penalty

    # Штраф за "Снято" > 10%
    if metrics['removed_percentage'] > 10:
        penalty = (metrics['removed_percentage'] - 10) * 0.7  # Штраф 0.7% за каждый процент сверх 10%
        if penalty > 7:
            penalty = 7  # Максимальный штраф 7%
        sprint_health_index -= penalty

    # Штраф за бэклог изменён более чем на 20%
    if metrics['backlog_changed_percentage'] > 20:
        penalty = (metrics['backlog_changed_percentage'] - 20) * 0.5  # Штраф 0.5% за каждый процент сверх 20%
        if penalty > 10:
            penalty = 10  # Максимальный штраф 10%
        sprint_health_index -= penalty

    # Штраф за массовое закрытие задач в последний день (если более 50% задач закрыты в последний день)
    if metrics['last_day_done_percentage'] > 50:
        penalty = (metrics['last_day_done_percentage'] - 50) * 0.5  # Штраф 0.5% за каждый процент сверх 50%
        if penalty > 15:
            penalty = 15  # Максимальный штраф 15%
        sprint_health_index -= penalty
    
    # Штраф за низкий процент выполнения
    if metrics['completion_percentage'] < 80:
       penalty = (80 - metrics['completion_percentage']) * 0.5
    if penalty > 20:
        penalty = 25  # Максимальный штраф 20%
    sprint_health_index -= penalty


    # Проверяем границы индекса здоровья
    if sprint_health_index < 0:
        sprint_health_index = 0.0
    elif sprint_health_index > 100:
        sprint_health_index = 100.0

    metrics['sprint_health_index'] = round(sprint_health_index, 1)

    return metrics
