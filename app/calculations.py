from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .models import Entity, Sprint, History
from .schemas import Sprint as SprintSchema
from sqlalchemy import func

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
        History.history_date <= sprint.end_date
    ).all()

    # Если нет истории изменений, используем дату создания и обновления задачи
    if not entities:
        entities = db.query(Entity).filter(
            Entity.create_date <= sprint.end_date,
            (Entity.update_date >= sprint.start_date) | (Entity.update_date == None)
        ).all()

    # Создаем словарь для хранения последнего статуса каждой задачи в пределах спринта
    entity_statuses = {}

    for entity in entities:
        # Получаем историю изменений статуса для задачи в пределах спринта
        status_histories = db.query(History).filter(
            History.entity_id == entity.entity_id,
            History.history_property_name == 'status',
            History.history_date >= sprint.start_date,
            History.history_date <= sprint.end_date
        ).order_by(History.history_date.desc()).all()

        if status_histories:
            # Берем последний статус в пределах спринта
            last_status = status_histories[0].history_change
        else:
            # Если изменений статуса не было, берем статус на момент закрытия спринта или текущий статус
            last_status = entity.status

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
        'blocked_tasks': 0.0
    }

    # Словари для подсчета бэклога
    estimation_at_start = 0.0
    estimation_after_two_days = 0.0

    # Текущая дата для активного спринта или дата окончания для прошедшего
    current_date = datetime.now() if is_active_sprint else sprint.end_date

    for data in entity_statuses.values():
        entity = data['entity']
        status = data['status']
        estimation = entity.estimation or 0.0

        # Переводим оценку в часы
        estimation_hours = float(estimation) / 3600

        # Логика определения категорий задач
        if status in ['Создано', 'К выполнению']:
            metrics['to_do'] += estimation_hours
        elif status in ['В работе']:
            metrics['in_progress'] += estimation_hours
        elif status in ['Сделано', 'Закрыто', 'Выполнено']:
            # Проверяем резолюцию для "Снято"
            if entity.resolution in ['Отклонено', 'Отменено инициатором', 'Дубликат'] or status == 'Отклонен исполнителем':
                metrics['removed'] += estimation_hours
            else:
                metrics['done'] += estimation_hours
        else:
            metrics['in_progress'] += estimation_hours

        # Подсчет бэклога на начало спринта и после двух дней
        if entity.create_date <= sprint.start_date + timedelta(days=2):
            estimation_at_start += estimation_hours
        elif entity.create_date > sprint.start_date + timedelta(days=2) and entity.create_date <= current_date:
            estimation_after_two_days += estimation_hours


        # Проверка на заблокированные задачи (опционально)
        # Предположим, что есть метод или поле, определяющее связь "Заблокировано"
        if hasattr(entity, 'is_blocked') and entity.is_blocked:
            if status not in ['Сделано', 'Закрыто', 'Выполнено']:
                metrics['blocked_tasks'] += estimation_hours

    # Рассчитываем процент изменения бэклога
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

    return metrics
