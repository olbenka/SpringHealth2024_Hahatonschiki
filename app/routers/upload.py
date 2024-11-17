from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
import pandas as pd
from .. import models
from sqlalchemy.dialects.postgresql import insert
import numpy as  np

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)

def process_entities_file(file: UploadFile, db: Session):
    # Чтение файла в DataFrame
    entities_data = pd.read_csv(
        file.file,
        sep=';',
        encoding='utf-8',
        skiprows=1
    )

    # Удаление полных дубликатов
    initial_shape = entities_data.shape
    entities_data = entities_data.drop_duplicates()
    duplicates_removed = initial_shape[0] - entities_data.shape[0]
    if duplicates_removed > 0:
        print(f"Удалено {duplicates_removed} полных дубликатов из entities_data.")

    # Предобработка данных
    for date_column in ['create_date', 'update_date']:
        if date_column not in entities_data.columns:
            entities_data[date_column] = None
        else:
            entities_data[date_column] = pd.to_datetime(
                entities_data[date_column],
                errors='coerce'
            )

    # Удаление ненужных столбцов
    columns_to_drop = [
        'created_by', 'updated_by', 'assignee', 'owner',
        'rank', 'workgroup', 'name', 'due_date', 'state', 'parent_ticket_id'
    ]
    entities_data.drop(columns=[col for col in columns_to_drop if col in entities_data.columns], inplace=True)

    # Заполнение пропусков
    entities_data['priority'] = entities_data['priority'].fillna('Не указано')
    entities_data['resolution'] = entities_data['resolution'].fillna('Нет решения')

    # Замена NaN на None в числовых полях
    entities_data['estimation'] = entities_data['estimation'].replace({np.nan: None})
    entities_data['spent'] = entities_data['spent'].replace({np.nan: None})

    # Преобразование DataFrame в список словарей
    entities_list = entities_data.to_dict(orient='records')

    # Подготовка выражения вставки с ON CONFLICT DO UPDATE
    stmt = insert(models.Entity).values(entities_list)
    update_columns = {c.name: c for c in stmt.excluded if c.name not in ['entity_id']}
    stmt = stmt.on_conflict_do_update(
        index_elements=['entity_id'],
        set_=update_columns
    )

    # Выполнение выражения
    try:
        db.execute(stmt)
        db.commit()
        print("Entities data uploaded successfully.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def process_history_file(file: UploadFile, db: Session):
    try:
        history_data = pd.read_csv(
            file.file,
            sep=';',
            engine='python',
            dtype={'history_version': 'Int64', 'entity_id': 'Int64'},
            encoding='utf-8',
            skiprows=1,
            skip_blank_lines=True
        )
        logger.info(f"Файл history прочитан. Размер: {history_data.shape}")

        columns_to_drop = ['Unnamed: 7', 'Столбец1']
        columns_present = [col for col in columns_to_drop if col in history_data.columns]
        if columns_present:
            history_data.drop(columns=columns_present, inplace=True)
            logger.info(f"Удалены столбцы: {columns_present}")

        history_data['history_property_name'] = history_data['history_property_name'].fillna('Неизвестно')
        history_data['history_change_type'] = history_data['history_change_type'].fillna('Неизвестно')
        history_data['history_change'] = history_data['history_change'].fillna('<Нет изменений>')
        logger.info("Пропуски в столбцах 'history_property_name', 'history_change_type' и 'history_change' заполнены.")

        history_data['history_date'] = pd.to_datetime(
            history_data['history_date'],
            errors='coerce',
            infer_datetime_format=True
        )
        logger.info("Столбец 'history_date' преобразован в datetime с использованием инференции формата.")

        initial_shape = history_data.shape
        history_data = history_data.dropna(subset=['history_date', 'entity_id'])
        duplicates_removed_date = initial_shape[0] - history_data.shape[0]
        if duplicates_removed_date > 0:
            logger.info(f"Удалено {duplicates_removed_date} строк с некорректными датами или отсутствующим 'entity_id' из history_data.")

        initial_shape_dup = history_data.shape
        history_data = history_data.drop_duplicates()
        duplicates_removed_dup = initial_shape_dup[0] - history_data.shape[0]
        if duplicates_removed_dup > 0:
            logger.info(f"Удалено {duplicates_removed_dup} полных дубликатов из history_data.")

        # Преобразование DataFrame в список словарей
        history_list = history_data.to_dict(orient='records')
        logger.info(f"Преобразовано {len(history_list)} записей для вставки.")

        if not history_list:
            logger.warning("Нет записей для вставки после предобработки.")
            return {"message": "No valid history records to upload."}

        # Подготовка выражения вставки с ON CONFLICT DO NOTHING
        stmt = insert(models.History).values(history_list)
        stmt = stmt.on_conflict_do_nothing()

        # Выполнение выражения
        db.execute(stmt)
        db.commit()
        logger.info("History data uploaded successfully.")

    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обработке файла history: {e}")
        raise HTTPException(status_code=400, detail=str(e))


    
def process_sprints_file(file: UploadFile, db: Session):
    # Чтение данных спринтов из файла
    sprints_data = pd.read_csv(
        file.file,
        sep=';',
        encoding='utf-8',
        skiprows=1,
        skip_blank_lines=True
    )

    # Удаление полных дубликатов на основе 'sprint_name' и всех остальных столбцов
    initial_shape = sprints_data.shape
    sprints_data = sprints_data.drop_duplicates()
    duplicates_removed = initial_shape[0] - sprints_data.shape[0]
    if duplicates_removed > 0:
        print(f"Удалено {duplicates_removed} полных дубликатов из sprints_data.")

    # Переименование столбцов для соответствия модели
    sprints_data.rename(columns={
        'sprint_names': 'sprint_name',
        'sprint_start_date': 'start_date',
        'sprint_end_date': 'end_date'
    }, inplace=True)

    # Обработка дат
    for date_col in ['start_date', 'end_date']:
        if date_col in sprints_data.columns:
            sprints_data[date_col] = pd.to_datetime(sprints_data[date_col], errors='coerce')

    # Заполнение отсутствующих значений
    sprints_data['sprint_name'] = sprints_data['sprint_name'].fillna('Неизвестный спринт')
    sprints_data['sprint_status'] = sprints_data['sprint_status'].fillna('Неизвестно')

    for _, row in sprints_data.iterrows():
        # Проверяем, существует ли спринт с таким именем
        sprint = db.query(models.Sprint).filter_by(sprint_name=row['sprint_name']).first()
        if not sprint:
            # Создаем новый спринт
            sprint = models.Sprint(
                sprint_name=row['sprint_name'],
                sprint_status=row['sprint_status'],
                start_date=row['start_date'],
                end_date=row['end_date'],
            )
            db.add(sprint)
            db.commit()  # Получаем sprint_id

        # Обрабатываем поле entity_ids
        entity_ids_str = row.get('entity_ids', '')
        if pd.isna(entity_ids_str) or not entity_ids_str:
            continue  # Нет связанных задач

        # Разделяем entity_ids и преобразуем их в числа
        entity_ids = [int(eid.strip()) for eid in str(entity_ids_str).strip('{}').split(',') if eid.strip().isdigit()]

        # Получаем задачи из базы данных
        entities = db.query(models.Entity).filter(models.Entity.entity_id.in_(entity_ids)).all()

        # Добавляем задачи в спринт через связь
        for entity in entities:
            if entity not in sprint.entities:
                sprint.entities.append(entity)

        db.commit()
    print("Sprints data uploaded successfully.")


@router.post("/entities")
async def upload_entities(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.filename.endswith('.csv'):
        try:
            process_entities_file(file, db)
            return {"message": "Entities data uploaded successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

@router.post("/history")
async def upload_history(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.filename.endswith('.csv'):
        try:
            process_history_file(file, db)
            return {"message": "History data uploaded successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

@router.post("/sprints")
async def upload_sprints(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.filename.endswith('.csv'):
        try:
            process_sprints_file(file, db)
            return {"message": "Sprints data uploaded successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
