import csv
import re
import sys

class CordinateCheck:
    def read_cordinate_data(self, file_path):
        coordinates = []
        try:
            # Meningkatkan batas ukuran field CSV
            csv.field_size_limit(sys.maxsize)
            
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    point = row.get('coordinate')  # Nama kolom 'coordinate' sesuai dengan kolom di CSV Anda
                    if point:
                        match = re.search(r"POINT \(([-\d.]+) ([-\d.]+)\)", point)
                        if match:
                            latitude = float(match.group(1))
                            longitude = float(match.group(2))

                            coordinates.append({
                                'latitude': latitude,
                                'longitude': longitude
                            })

            # Print each coordinate
            for coordinate in coordinates:
                # print(coordinate)
                yield coordinate

        except FileNotFoundError:
            print(f"File {file_path} tidak ditemukan.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

    def proccess(self, file_path):
        for coordinate in self.read_cordinate_data(file_path):
            print(coordinate)
