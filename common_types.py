class Location:
	def __init__(self, latitude=None,longitude=None, radius=10, imperial_units=True):
		self.latitude = latitude
		self.longitude = longitude
		self.radius = radius
		self.imperial_units = imperial_units