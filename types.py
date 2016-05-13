class Location:
	def __init__(self, longitude=None, latitude=None, radius=10, imperial_units=True):
		self.longitude = longitude
		self.latitude = latitude
		self.radius = radius
		self.imperial_units = imperial_units