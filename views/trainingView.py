from models.player import db, TrainingDay
from flask import request, jsonify


def create_training_day():
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
        return jsonify({'message': 'Training days created successfully'}), 201
    except Exception as e:
        print(f"Error creating training days: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error creating training days'}), 500


def get_training_schedule():
    schedule = TrainingDay.query.all()
    training_schedule = [day.to_dict() for day in schedule]
    return jsonify(training_schedule), 200
