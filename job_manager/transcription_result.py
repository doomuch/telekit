class TranscriptionResult:
    def __init__(self, verbose_answer):
        self._result = {
            "segments": []
        }
        self.duration = verbose_answer["duration"]
        self.verbose_answer = verbose_answer
        for segment in verbose_answer["segments"]:
            self._result["segments"].append({
                "start": segment["start"],
                "text": segment["text"]
            })

    def add_verbose_answer(self, verbose_answer):
        for segment in verbose_answer["segments"]:
            self._result["segments"].append({
                "start": segment["start"] + self.duration,
                "text": segment["text"]
            })

        self.duration += verbose_answer["duration"]

    def get_plain_text(self):
        text = ""
        for segment in self._result["segments"]:
            text += segment["text"]

        text = text[1:] if text[0] == " " else text

        return text

    def get_json(self):
        return self._result
