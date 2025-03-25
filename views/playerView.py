import json
import cloudinary
import cloudinary.uploader
from flask import request, jsonify
from redis_config import redis_client
from models.player import db, Player
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLAYER_CACHE_KEY = "player_of_the_month"


def create_player():
    """
    Handle the creation of a new Player of the Month (POTM).

    Accepts a POST request with a full name, position, and 3 to 5 images.
    Uploads images to Cloudinary, replaces any existing POTM,
    saves to the database with `is_potm=True`, and caches in Redis.

    Returns:
        JSON response with success message (201) or error message (400/500).
    """
    full_name = request.form.get('full_name')
    position = request.form.get('position')
    images = request.files.getlist('images')

    if not full_name or not position or not images:
        return jsonify({'message': 'Missing required fields'}), 400

    if not 3 <= len(images) <= 5:
        return jsonify({'message': 'Must upload 3 to 5 images'}), 400

    image_urls = []
    try:
        for image in images:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get('secure_url')
            image_urls.append(image_url)
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {e}")
        return jsonify({'message': 'Error uploading images'}), 500

    previous_potm = Player.query.filter_by(is_potm=True).first()
    if previous_potm:
        try:
            for url in previous_potm.image_urls:
                public_id = url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id)
        except Exception as e:
            logger.error(f"Error deleting image {public_id}: {e}")
        db.session.delete(previous_potm)
        db.session.commit()

    new_player = Player(
        name=full_name,
        position=position,
        image_urls=image_urls,
        is_potm=True
    )
    try:
        db.session.add(new_player)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error saving player to database'}), 500

    player_data = {
        'name': full_name,
        'position': position,
        'image_urls': image_urls,
        'is_potm': True
    }
    try:
        redis_client.set(PLAYER_CACHE_KEY, json.dumps(player_data))
        logger.info("Cached player in Redis successfully")
    except Exception as e:
        logger.error(f"Failed to cache in Redis: {e}")

    return jsonify({'message': 'Player created successfully'}), 201


def get_player():
    """
    Retrieve the current Player of the Month (POTM).

    Tries Redis cache first, falls back to database if not found,
    and caches the result in Redis.

    Returns:
        JSON response with player data (200) or error message (404).
    """
    try:
        cached_player = redis_client.get(PLAYER_CACHE_KEY)
        if cached_player:
            return jsonify(json.loads(cached_player)), 200
    except Exception as e:
        logger.error(f"Failed to fetch from Redis: {e}")

    player = Player.query.filter_by(is_potm=True).first()
    if player:
        player_dict = player.to_dict()
        try:
            redis_client.set(PLAYER_CACHE_KEY, json.dumps(player_dict))
            logger.info("Cached player in Redis successfully")
        except Exception as e:
            logger.error(f"Failed to cache in Redis: {e}")
        return jsonify(player_dict), 200
    else:
        return jsonify({'message': 'Player of the month not found'}), 404
