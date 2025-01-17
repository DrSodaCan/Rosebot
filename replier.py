from random import randint

movie_list = {}
class movies:
    #Make a dictionary for the movies
    def __init__(self, name):
        self.name = name
        self.responses = []
        movie_list[name] = self

    def add_response(self, response):
        self.responses.append(response)

    def add_response(self, *args):
        for response in args:
            self.responses.append(response)

    def get_response(self):
        return self.responses[randint(0, len(self.responses) - 1)]