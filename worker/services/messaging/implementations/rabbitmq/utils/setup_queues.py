from shared.utils.promise import Promise


def create_temporal_exchange_queue(channel, exchange_name: str) -> Promise[str]:
    promise = Promise[str]()
    resolve, reject = promise.handlers
    channel.queue_declare(queue='', exclusive=True, auto_delete=True,
                          callback=lambda frame: resolve(frame.method.queue))
    promise.then(lambda q_name: channel.queue_bind(exchange=exchange_name,
                                                   queue=q_name))
    return promise
