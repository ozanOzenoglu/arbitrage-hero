class Info:
    def __init__(self):
        self._json_message = None

    def to_json(self):
        if self._json_message == None:
            assert Exception("Message element is none")

        return self._json_message._to_string()

