from datetime import date
from flask import Flask, json, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import pika
import requests
import sys

db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Borrow(db.Model):
    __tablename__ = 'borrow'
    studentid = db.Column(db.String(20), primary_key=True)
    bookid = db.Column(db.String(20), primary_key=True)

    def to_dict(self):
        return dict(studentid=self.studentid, bookid=self.bookid)

with app.app_context():
    db.create_all()

def start_consumer():

    credentials = pika.PlainCredentials(
    os.getenv("RABBITMQ_DEFAULT_USER"),
    os.getenv("RABBITMQ_DEFAULT_PASS")
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue='borrow_book')
    channel.basic_qos(prefetch_count=1)

    def borrowBook(ch, method, properties, body):
        with app.app_context():
            try:
                print(f"Received {body.decode()}")
                payload = json.loads(body.decode())

                studentid = payload["studentid"]
                bookid = payload["bookid"]

                # Fetch user
                user = requests.get(f"http://user-service:5002/users/{studentid}")
                if user.status_code != 200:
                    print("User not found")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Fetch book
                book = requests.get(f"http://book-service:5006/books/{bookid}")
                if book.status_code != 200:
                    print("Book not found")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Borrow limit check
                count = Borrow.query.filter_by(studentid=studentid).count()
                if count >= 5:
                    print("Borrow limit exceeded")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Create borrow record
                borrow = Borrow(studentid=studentid, bookid=bookid)
                db.session.add(borrow)
                db.session.commit()

                print(f"Borrow entry saved: {payload}")

                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                print("Error processing message:", e)
                ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='borrow_book', on_message_callback=borrowBook, auto_ack=False)

    channel.start_consuming()

@app.route("/borrow/<studentid>", methods=["GET"])
def borrowed_books(studentid):
    entries = Borrow.query.filter_by(studentid=studentid).all()
    return jsonify([e.to_dict() for e in entries])

def check_rabbit_or_die():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_DEFAULT_USER"),
        os.getenv("RABBITMQ_DEFAULT_PASS")
    )
    try:
        conn = pika.BlockingConnection(
            pika.ConnectionParameters("rabbitmq", 5672, "/", credentials)
        )
        conn.close()
    except pika.exceptions.AMQPConnectionError as e:
        print("RabbitMQ not reachable at startup, exiting...", e)
        os._exit(1)


if __name__ == "__main__":
    check_rabbit_or_die()
    import threading
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    
    app.run(host="0.0.0.0", port=5003)