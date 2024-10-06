import ast
import json
from loguru import logger
import requests
from bs4 import BeautifulSoup
from src.lib.storage_manager import StorageManager
from src.controller.get_cordinate import CordinateCheck
from concurrent.futures import ThreadPoolExecutor

class RSTP:
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://sipukat.kemendesa.go.id',
            'Referer': 'https://sipukat.kemendesa.go.id/petaterpadu.php?v=2021',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }

    def _process_data(self, data):
        response = requests.post('https://sipukat.kemendesa.go.id/i.php', headers=self.headers, data=data)
        logger.info(f'{data} :: {response}')
        datas = response.text
        if datas:
            data = json.loads(datas)
            soup = BeautifulSoup(data['isi'], 'html.parser')

            titles = soup.select_one('h1')
            key = soup.select('tr td:nth-child(1)')
            value = soup.select('tr td:nth-child(3)')

            isi = {}
            for k, v in zip(key, value):
                isi[k.text.strip()] = v.text.strip()

            data.update({'isi': isi})
            data['pol'] = ast.literal_eval(data['pol'])
            data['pol'] = [[coord[1], coord[0]] for coord in data['pol']]

            title = isi.get("title", "")
            tahun = isi.get("Tahun", "")
            metadata = {
                "link": "https://sipukat.kemendesa.go.id/petaterpadu.php?v=2021",
                "tags": [
                    "sipukat",
                    "rtsp"
                ],
                "source": "sipukat.kemendesa.go.id",
                "title": title if title else None,
                "sub_title": None,
                "range_data": tahun if tahun else None,
                "create_date": None,
                "update_date": None,
                "desc": None,
                "category": "RTSP",
                "sub_category": None,
                "data": data,
                "path_data_raw": [],
                "crawling_time": "2024-07-26 22:24:49",
                "crawling_time_epoch": 1722007489,
                "table_name": "judul_tabel",
                "country_name": "Indonesia",
                "level": "Nasional",
                "stage": "Crawling data",
                "update_schedule": "daily"
            }
            return metadata

    def get_cordinate(self, file_path):
        # Membuat instance dari CordinateCheck
        cordinate_check = CordinateCheck()

        # List untuk menyimpan semua metadata
        all_metadata = []

        # Mendapatkan latitude dan longitude dari file
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = []
            for idx, latlong in enumerate(cordinate_check.read_cordinate_data(file_path)):
                for i in range(10, 19):
                    latitude = latlong["latitude"]
                    longitude = latlong["longitude"]

                    data = {
                        'x': latitude,
                        'y': longitude,
                        'mz': f'{i}',
                        'idL': '||||||1|||||||',
                        'idP': 'i_jalan|i_prm|i_sp|i_wst|i_bum|i_pru|i_rtsp|i_rskp|info4|info2|info8|infokp|info',
                        'idR': '10-21|10-21|10-18|4-21|4-21|4-21|10-18|10-18|4-17|4-18|6-21|6-21|6-21',
                    }
                    futures.append(
                        executor.submit(self._process_data, data)
                    )

            # Mengumpulkan semua metadata
            for future in futures:
                metadata = future.result()
                if metadata:
                    all_metadata.append(metadata)

        # Menyimpan semua metadata dalam satu file JSON
        if all_metadata:
            file_name = "src/sempel/RSTP/all_data.json"
            with open(file_name, "w") as f:
                json.dump(all_metadata, f, indent=4)
            logger.success(f"All data saved in: {file_name}")

