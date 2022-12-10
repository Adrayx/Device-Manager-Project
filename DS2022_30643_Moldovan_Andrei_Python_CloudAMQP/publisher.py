import pika, os, json, time, threading, logging

url = os.environ.get('CLOUDAMQP_URL', 'amqps://pxujpuqb:0QNynshiRNg12vK9kM785aqE05h2y66l@goose.rmq2.cloudamqp.com/pxujpuqb')
params = pika.URLParameters(url)

def enqueue(id, sleep_time, event):
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.exchange_declare('test_exchange')
    channel.queue_declare(queue='test_queue')
    channel.queue_bind('test_queue', 'test_exchange', 'tests')

    with open('sensor.csv', 'r') as file:
        lines = file.readlines()
        for line in lines:
            channel.basic_publish(
                body=json.dumps({
                    'id': id,
                    'measurement': line.strip()
                }),
                exchange='test_exchange',
                routing_key='tests'
            )

            time.sleep(sleep_time)
            if event.is_set():
                break
    channel.close()
    connection.close()


if __name__ == '__main__':
    event = threading.Event()
    threads = []
    try:
        while(True):
            keyboardInput = input("Create new thread to enqueue measurements?[Y / N]")
            if keyboardInput == 'Y' or keyboardInput == 'y':
                id = int(input("ID of the device: "))
                sleep_time = int(input("Frequency of measurements: "))
                print("Main    : before creating thread")
                threads.append(threading.Thread(target=enqueue, args=(id, sleep_time, event)))
                print("Main    : before running thread")
                threads[len(threads) - 1].start()
            else:
                if(len(threads) == 0):
                    break
                print("Waiting for the started threads to end reading the file");
                print("Press CTRL + C to end the program")
    except KeyboardInterrupt:
        print("Interrupted main thread")
        print("Main    : set event")
        event.set()
    finally:
        for thread in threads:
            thread.join()
        logging.info("Main    : thread joined")