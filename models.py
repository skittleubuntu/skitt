class User:
    def __init__(self, id, name):
        self.name = name
        self.id = id


class Post:
    def __init__(self, id, author,title,text,day):
        self.text = text
        self.title = title
        self.author = author
        self.id = id
        self.day = day

class Reply:
    def __init__(self, author, text, day):
        self.text = text
        self.author = author
        self.day = day







