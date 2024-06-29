import requests
api_url = 'https://api.api-ninjas.com/v1/babynames?gender=neutral'


class Name:
    def __init__(self, key, names):
        self.key = key
        self.names = names
    def set_key(self, key):
        self.key = key

    def get_name(self):
        print("New names")
        if not self.names:
            print("No names, getting new ones")
            self.new_names()
        print(self.names)
        return self.names.pop(0)

    def new_names(self):
        response = requests.get(api_url, headers={'X-Api-Key': self.key})
        if response.status_code == requests.codes.ok:
            self.names = response.text
            self.names = self.names.replace('[', '')
            self.names = self.names.replace(']', '')
            self.names = self.names.replace(' ', '')
            self.names = self.names.replace('"', '')

            self.names = self.names.split(',')
            print(self.names)

        else:
            print("Error:", response.status_code, response.text)
    def __str__(self):
        return self.names