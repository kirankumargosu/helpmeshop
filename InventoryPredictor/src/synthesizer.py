
class Synthesizer:
    __instance = None
    __ = None

    def __init__(self):
        if Synthesizer.__instance is not None:
            raise Exception("I'm Singleton")
        else:
            Synthesizer.__instance = self

    @staticmethod
    def get_instance():
        if Synthesizer.__instance is None:
            Synthesizer.__instance = Synthesizer()
        return Synthesizer.__instance

    def curate_data(self):
        self.__ = None
