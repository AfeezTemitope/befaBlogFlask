import cloudinary
import cloudinary.uploader
from models.player import db, Player
from flask import Flask, request, jsonify


def create_player():
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

        previous_potm = Player.query.filter_by(is_potm=True).first()
        if previous_potm:
            for url in previous_potm.image_urls:
                public_id = url.split('/')[-1].split('.')[0]
                try:
                    cloudinary.uploader.destroy(public_id)
                except Exception as e:
                    print(f"Error deleting image {public_id}: {e}")
            db.session.delete(previous_potm)
            db.session.commit()

        new_player = Player(
            name=full_name,
            position=position,
            image_urls=image_urls,
            is_potm=True
        )
        db.session.add(new_player)
        db.session.commit()

        return jsonify({'message': 'Player created successfully'}), 201

    except Exception as e:
        print('Error uploading to Cloudinary or saving to DB:', e)
        db.session.rollback()
        return jsonify({'message': 'Error updating player information'}), 500


def get_player():
    player = Player.query.filter_by(is_potm=True).first()
    if player:
        return jsonify(player.to_dict()), 200
    else:
        return jsonify({'message': 'Player of the month not found'}), 404
