class Sub:
    def __init__(self, name: str, description: str = "", image: str = "") -> None:
        self.name = name
        self.description = description
        self.image = image

class Store:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name