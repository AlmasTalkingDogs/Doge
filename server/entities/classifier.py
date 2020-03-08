class Classifier():

    def _init_(self):
    	self.name = "sampleName"
    	self.sample_data = None
    def classify(self, sample_data):
    	self.sample_data = sample_data
        return "chuchu", 0

    def get_name(self):
        return self.name
