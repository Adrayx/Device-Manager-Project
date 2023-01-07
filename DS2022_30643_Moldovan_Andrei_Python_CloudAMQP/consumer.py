import pika, os, json

url = os.environ.get('CLOUDAMQP_URL', 'amqps://pxujpuqb:0QNynshiRNg12vK9kM785aqE05h2y66l@goose.rmq2.cloudamqp.com/pxujpuqb')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='measurements_queue')

def callback(ch, method, properties, body):
    print('[x] Received: ')
    obj = json.loads(str(body, 'UTF-8'))
    print(obj)

channel.basic_consume(
    'measurements_queue',
    callback,
    auto_ack=True
)

print('[x] Waiting for messages: ')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Force close")
connection.close()