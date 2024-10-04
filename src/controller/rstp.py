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
                data_akhir = {
                    'title': titles.text.strip(),
                    k.text.strip(): v.text.strip(),
                }
                isi.update(data_akhir)
            data.update({'isi': isi})

            data['pol'] = ast.literal_eval(data['pol'])
            data['pol'] = [[coord[1], coord[0]] for coord in data['pol']]

            file_name = f'{data["isi"]["title"]}_{data["isi"]["Kawasan"]}_{data["isi"]["Lokasi"]}.json'
            json_path = f"sempel/sipukat/rtsp/json/{file_name.replace(' ', '_').replace('/', '_')}"

            return print({
                "link": "https://e-database.kemendagri.go.id/kemendagri/dataset/532/tabel-data",
                "tags": [
                    "sipukat",
                    "rtsp"
                ],
                "source": "sipukat.kemendesa.go.id",
                "title": data['isi']['title'],
                "sub_title": "",
                "range_data": data["isi"]["Tahun"],
                "create_date": "",
                "update_date": "",
                "desc": "",
                "category": "RTSP",
                "sub_category": "",
                "data":data,
                "path_data_raw": [
                    json_path
                ],
                "crawling_time": "2024-07-26 22:24:49",
                "crawling_time_epoch": 1722007489,
                "table_name": "judul_tabel",
                "country_name": "Indonesia",
                "level": "Nasional",
                "stage": "Crawling data",
                "update_schedule": "daily"
            })
    
    def get_cordinate(self, file_path):
        # Membuat instance dari CordinateCheck
        cordinate_check = CordinateCheck()

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

                for future in futures:
                    metadata = future.result()
                    if(metadata):
                        with open(f"src/sempel/RSTP/{latitude}_{longitude}.json", "w") as f:
                            f.write(json.dumps(metadata))
                        logger.success(json.dumps(metadata))
                        break