from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def save(self, entity):
        pass

    @abstractmethod
    def update(self, entity):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def find_by_id(self, entity_id):
        pass

    @abstractmethod
    def delete_by_id(self, entity_id):
        pass