import json
from datetime import datetime
import cloudinary
import cloudinary.uploader
from flask import request, jsonify

from config import Config
from redis_config import cache, redis_client
from models.player import ClubAnnouncement, db

ANNOUNCEMENT_CACHE_KEY = "club_announcement"


def club_announcement():
    """
    Handle the creation and upload of a club announcement.

    This endpoint accepts a POST request with a caption, author, and exactly 4 images.
    It uploads the images to Cloudinary, deletes any previous announcement (including its images),
    saves the new announcement to the database, and caches it in Redis.

    Returns:
        JSON response with a success message and HTTP status 201 on success,
        or an error message with an appropriate HTTP status code on failure.
    """
    caption = request.form.get('caption')
    author = request.form.get('author')
    images = request.files.getlist('images')

    # Validate required fields
    if not caption or not author or not images:
        return jsonify({'message': 'Missing required fields'}), 400

    # Ensure exactly 4 images are uploaded
    if len(images) != 4:
        return jsonify({'message': 'Exactly 4 images must be uploaded'}), 400

    # Upload images to Cloudinary
    image_urls = []
    try:
        for image in images:
            upload_result = cloudinary.uploader.upload(image)
            image_urls.append(upload_result['secure_url'])
    except Exception as e:
        print('Error uploading to Cloudinary:', e)
        return jsonify({'message': 'Error uploading images'}), 500

    # Delete previous announcement and its images from Cloudinary
    previous_announcement = ClubAnnouncement.query.first()
    if previous_announcement:
        try:
            for url in previous_announcement.image_urls:
                public_id = url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print('Error deleting images from Cloudinary:', e)

        db.session.delete(previous_announcement)
        db.session.commit()

    # Create and save the new announcement
    date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_announcement = ClubAnnouncement(
        image_urls=image_urls,
        caption=caption,
        date_posted=date_posted,
        author=author
    )

    try:
        db.session.add(new_announcement)
        db.session.commit()
        print(f"Attempting to cache with REDIS_URL: {Config.REDIS_URL}")
        # Cache the announcement in Redis
        announcement_data = {
            'image_urls': image_urls,
            'caption': caption,
            'date_posted': date_posted,
            'author': author,
        }
        redis_client.set(ANNOUNCEMENT_CACHE_KEY, json.dumps(announcement_data))
        return jsonify({'message': 'Club announcement uploaded successfully'}), 201
    except Exception as e:
        print('Error saving to database:', e)
        db.session.rollback()
        return jsonify({'message': 'Error saving announcement'}), 500


def get_club_announcement():
    """
    Retrieve the current club announcement.

    This endpoint first attempts to fetch the announcement from Redis cache.
    If not found in cache, it queries the database, caches the result in Redis,
    and returns it. If no announcement exists, it returns a 404 error.

    Returns:
        JSON response with the announcement data and HTTP status 200 on success,
        or an error message with HTTP status 404 if no announcement is found.
    """
    # Try to get the announcement from Redis first
    cached_announcement = redis_client.get(ANNOUNCEMENT_CACHE_KEY)
    if cached_announcement:
        return jsonify(json.loads(cached_announcement)), 200

    # Fallback to database if not in Redis
    announcement = ClubAnnouncement.query.first()
    if announcement:
        announcement_dict = announcement.to_dict()
        # Cache it in Redis for future requests
        redis_client.set(ANNOUNCEMENT_CACHE_KEY, json.dumps(announcement_dict))
        return jsonify(announcement_dict), 200
    else:
        return jsonify({'message': 'No club announcement found'}), 404
