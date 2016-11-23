import threading
try:
    import queue
except ImportError:
    import Queue as queue


class Notifier(object):

    def __init__(self, bus, listeners, timeout=None):
        """Manages the distribution of **Messages** from a given bus to a
        list of listeners.

        :param bus: The :ref:`bus` to listen too.
        :param listeners: An iterable of :class:`~can.Listeners`
        :param timeout: An optional maximum number of seconds to wait for any message.
        """
        self.listeners = listeners
        self.bus = bus
        self.timeout = timeout

        self.running = threading.Event()
        self.running.set()

        self._reader = threading.Thread(target=self.rx_thread)
        self._reader.daemon = True

        self._reader.start()

    def stop(self):
        """Stop notifying Listeners when new :class:`~can.Message` objects arrive
         and call :meth:`~can.Listener.stop` on each Listener."""
        self.running.clear()
        if self.timeout is not None:
            self._reader.join(self.timeout + 0.1)

    def rx_thread(self):
        while self.running.is_set():
            msg = self.bus.recv(self.timeout)
            if msg is not None:
                for callback in self.listeners:
                    callback(msg)

        for listener in self.listeners:
            listener.stop()
