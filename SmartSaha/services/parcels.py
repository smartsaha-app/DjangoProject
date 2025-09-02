class ParcelService:
    def __init__(self, parcel):
        self.parcel = parcel

    def add_points_bulk(self, points_list):
        for idx, p in enumerate(points_list):
            self.parcel.add_point(p['lat'], p['lng'], idx)
        return self.parcel
