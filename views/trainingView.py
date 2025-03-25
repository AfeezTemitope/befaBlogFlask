import json
from flask import request, jsonify
from redis_config import redis_client
from models.player import db, TrainingDay
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TRAINING_SCHEDULE_CACHE_KEY = "training_schedule"


def create_training_day():
    """
    Handle the creation of multiple training days.

    Accepts a POST request with a JSON list of training day objects, each containing
    day, date, time, venue, and jersey_color fields. Saves all training days to the
    database in a single transaction and caches the updated schedule in Redis.

    Returns:
        JSON response with success message (201) or error message (400/500).
    """
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({'message': 'Invalid data provided. Expecting a list of training days.'}), 400

    try:
        for day_data in data:
            new_training_day = TrainingDay(
                day=day_data['day'],
                date=day_data['date'],
                time=day_data['time'],
                venue=day_data['venue'],
                jersey_color=day_data['jersey_color']
            )
            db.session.add(new_training_day)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error creating training days: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error creating training days'}), 500

    try:
        schedule = TrainingDay.query.all()
        training_schedule = [day.to_dict() for day in schedule]
        redis_client.set(TRAINING_SCHEDULE_CACHE_KEY, json.dumps(training_schedule))
        logger.info("Cached training schedule in Redis successfully")
    except Exception as e:
        logger.error(f"Failed to cache training schedule in Redis: {e}")

    return jsonify({'message': 'Training days created successfully'}), 201


def get_training_schedule():
    """
    Retrieve the full training schedule.

    Tries Redis cache first, falls back to database if not found,
    and caches the result in Redis.

    Returns:
        JSON response with training schedule list (200).
    """
    try:
        cached_schedule = redis_client.get(TRAINING_SCHEDULE_CACHE_KEY)
        if cached_schedule:
            return jsonify(json.loads(cached_schedule)), 200
    except Exception as e:
        logger.error(f"Failed to fetch from Redis: {e}")

    schedule = TrainingDay.query.all()
    training_schedule = [day.to_dict() for day in schedule]
    try:
        redis_client.set(TRAINING_SCHEDULE_CACHE_KEY, json.dumps(training_schedule))
        logger.info("Cached training schedule in Redis successfully")
    except Exception as e:
        logger.error(f"Failed to cache in Redis: {e}")

    return jsonify(training_schedule), 200
