class Expenses:
    data = None
    wordCloud = None
    __instance = None

    def __init__(self):
        if Expenses.__instance is not None:
            raise Exception("I'm Singleton")
        else:
            Expenses.__instance = self

    @staticmethod
    def get_instance():
        if Expenses.__instance is None:
            Expenses.__instance = Expenses()
        return Expenses.__instance
