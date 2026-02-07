class Composer:
    def __init__(self, composer_id: int | None = None, name: str | None = None, catalogue_source: str | None = None):
        self.composer_id = composer_id
        self.name = name
        self.catalogue_source = catalogue_source


class Work:
    def __init__(self, work_id: int | None = None,
                 composer_id: int | None = None,
                 title: str | None = None,
                 genre: str | None = None,
                 creation_year: int | None = None,
                 detail_url: str | None = None,
                 composer: str | None = None,
                 decade: str | None = None):
        self.work_id = work_id
        self.composer_id = composer_id
        self.title = title
        self.genre = genre
        self.creation_year = creation_year
        self.detail_url = detail_url
        self.composer = composer
        self.decade = decade

    def to_dict(self):
        return {
            'work_id': self.work_id,
            'composer_id': self.composer_id,
            'title': self.title,
            'genre': self.genre,
            'creation_year': self.creation_year,
            'detail_url': self.detail_url,
            'composer': self.composer,
            'decade':self.decade
        }
