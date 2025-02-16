import cloudinary
import cloudinary.uploader
from models.player import db, Player
from flask import Flask, request, jsonify


def create_player():
    full_name = request.form.get('full_name')
    position = request.form.get('position')
    image = request.files.get('image')

    if not full_name or not position or not image:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result.get('secure_url')

        previous_potm = Player.query.filter_by(is_potm=True).first()
        if previous_potm:
            previous_potm.is_potm = False
            db.session.commit()

        new_player = Player(
            full_name=full_name,
            position=position,
            image_url=image_url,
            is_potm=True,
        )
        db.session.add(new_player)
        db.session.commit()

        return jsonify({'message': 'Player created successfully'}), 201

    except Exception as e:
        print('error uploading to cloudinary or saving to db', e)
        db.session.rollback()
        return jsonify({'message': 'Error updating player information'}), 500


def get_player():
    player = Player.query.first()
    if player:
        return jsonify(player.to_dict()), 200
    else:
        return jsonify({'message': 'Player of the month not found'}), 404
