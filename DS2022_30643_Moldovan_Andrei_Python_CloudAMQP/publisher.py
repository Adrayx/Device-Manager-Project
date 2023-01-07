import pika, os, json, time, threading, logging, time

url = os.environ.get('CLOUDAMQP_URL', 'amqps://pxujpuqb:0QNynshiRNg12vK9kM785aqE05h2y66l@goose.rmq2.cloudamqp.com/pxujpuqb')
params = pika.URLParameters(url)

def enqueue(id, sleep_time, event):
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.exchange_declare('exchange_measurements')
        channel.queue_declare(queue='measurements_queue')
        channel.queue_bind('measurements_queue', 'exchange_measurements', 'measurements')

        with open('sensor.csv', 'r') as file:
            lines = file.readlines()
            for line in lines:
                channel.basic_publish(
                    body=json.dumps({
                        'id': id,
                        'timestamp': int(time.time()),
                        'measurement': line.strip()
                    }),
                    exchange='exchange_measurements',
                    routing_key='measurements'
                )

                time.sleep(sleep_time)
                if event.is_set():
                    break
        channel.close()
        connection.close()
    except pika.exceptions.ProbableAccessDeniedError:
        print('\033[91m' + 'Connection limit reached!')


if __name__ == '__main__':
    event = threading.Event()
    threads = []
    try:
        while(True):
            keyboardInput = input("Create new thread to enqueue measurements?[Y / N]")
            if keyboardInput == 'Y' or keyboardInput == 'y':
                try:
                    id = int(input("ID of the device: "))
                    sleep_time = int(input("Frequency of measurements: "))
                    print("Main    : before creating thread")
                    threads.append(threading.Thread(target=enqueue, args=(id, sleep_time, event)))
                    print("Main    : before running thread")
                    threads[len(threads) - 1].start()
                except ValueError:
                    print("Value Error, retry!")
            else:
                if(len(threads) == 0):
                    break
                print("Waiting for the started threads to end reading the file");
                print("Press CTRL + C to end the program")
                while(True):
                    time.sleep(1000)
    except KeyboardInterrupt:
        print("Interrupted main thread")
        print("Main    : set event")
    finally:
        event.set()
        for thread in threads:
            thread.join()
        logging.info("Main    : thread joined")