from abc import ABC


class Classifier(ABC):
    name = "sampleName"
    sample_data = None

    def classify(self, sample_data):
        self.sample_data = sample_data
        return 0

    def get_name(self):
        return self.name
