from abc import ABC, abstractmethod


class JobFetcher(ABC):
    @abstractmethod
    def source_name(self):
        raise NotImplementedError

    @abstractmethod
    def fetch_jobs(self):
        raise NotImplementedError
