from datetime import datetime
import cloudinary
import cloudinary.uploader
from flask import request, jsonify

from models.player import ClubAnnouncement, db


def club_announcement():
    caption = request.form.get('caption')
    author = request.form.get('author')
    images = request.files.getlist('images')

    if not caption or not author or not images:
        return jsonify({'message': 'Missing required fields'}), 400

    if len(images) != 4:
        return jsonify({'message': 'Exactly 4 images must be uploaded'}), 400

    image_urls = []
    try:
        for image in images:
            upload_result = cloudinary.uploader.upload(image)
            image_urls.append(upload_result['secure_url'])
    except Exception as e:
        print('Error uploading to Cloudinary:', e)
        return jsonify({'message': 'Error uploading images'}), 500

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
        return jsonify({'message': 'Club announcement uploaded successfully'}), 201
    except Exception as e:
        print('Error saving to database:', e)
        db.session.rollback()
        return jsonify({'message': 'Error saving announcement'}), 500


def get_club_announcement():
    announcement = ClubAnnouncement.query.first()
    if announcement:
        return jsonify(announcement.to_dict()), 200
    else:
        return jsonify({'message': 'No club announcement found'}), 404
