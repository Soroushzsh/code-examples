from confluent_kafka import Consumer
from decouple import config

import sys
from datetime import datetime
import socket
import os.path
from pathlib import Path
import logging

KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_GROUP_ID = config('KAFKA_GROUP_ID')
KAFKA_AUTO_OFFSET_RESET = config('KAFKA_AUTO_OFFSET_RESET')
KAFKA_TOPIC = config('KAFKA_LOGS_TOPIC')

consumer_identifier = socket.gethostname()


def setup_error_log_file(taday):
    current_file = Path(__file__).resolve()
    parent = current_file.parent
    logs_dir = os.path.join(parent, 'logs')

    if not (os.path.exists(logs_dir) and os.path.isdir(logs_dir)):
        os.makedirs(logs_dir)

    file_name = os.path.join(logs_dir, f'consumer_error_{consumer_identifier}_{today}.log')

    logging.basicConfig(
        filename=file_name,
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )


def setup_data_file():
    today = datetime.now().strftime('%Y-%m-%d')
    file_name = f'{KAFKA_TOPIC}_{consumer_identifier}_{today}.log'

    try:
        file = open(file_name, 'a')
    except Exception as e:
        logging.error('[setup_data_file]-[e: %s]' % e)
    
    return file, file_name


def get_today_filename():
    today = datetime.now().strftime('%Y-%m-%d')
    file_name = f'{KAFKA_TOPIC}_{consumer_identifier}_{today}.log'

    return file_name


def consume_data():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'client.id': consumer_identifier,
        'auto.offset.reset': KAFKA_AUTO_OFFSET_RESET,
    }

    consumer = Consumer(conf)
    consumer.subscribe([KAFKA_TOPIC])
    data_file, file_name = setup_data_file()

    while True:
        try:
            msg = consumer.poll(timeout=1.0)
        except Exception as e:
            logging.error('[consume_data] - [polling] - [identifier: %s] - [e: %s]' % 
                            consumer_identifier, msg.error())
            continue

        if msg is None:
            continue
        
        if msg.error():
            logging.error('[consume_data] - [identifier: %s] - [topic: %s] - [partition: %d] - [offset: %d] -[e: %s]' % 
                            (consumer_identifier, msg.topic(), msg.partition(), msg.offset(), msg.error()))
            continue
        else:
            if file_name != get_today_filename():
                data_file.close()
                data_file, file_name = setup_data_file()

            try:
                data_file.write(msg.value().decode('utf-8') + '\n')
            except Exception as e:
                logging.error(
                    '[consume_data]- [write] - [identifier: %s] - [topic: %s] - [partition: %d] - [offset: %d] -[e: %s]' % 
                    (consumer_identifier, msg.topic(), msg.partition(), msg.offset(), e)
                )
                continue

    consumer.close()


if __name__ == "__main__":
    sys.stdout.write(f'consumer {consumer_identifier} script started...')
    today = datetime.now().strftime('%Y-%m-%d')
    setup_error_log_file(today)
    consume_data(today)

