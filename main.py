# - *- coding: utf- 8 - *-
from io import BytesIO
import requests
import qrcode
import json

def read_config():
    file = open('settings.json')
    data = json.load(file)
    return data

def get_trackor_type_id(trackor_type, domain, token):
    headers = {
        'accept': '*/*',
        'Authorization': f'Basic {token}',
    }
    response = requests.get(
        f'https://{domain}/api/v3/trackor_types',
        headers=headers,
    )
    trackor_types = response.json()
    for i in range(len(trackor_types)):
        if trackor_types[i]["name"].upper() == trackor_type.upper():
            return trackor_types[i]["id"]
    return False

def upload_qrcode(qr_code_b, trackor_id, qr_field_name, domain, token):
    headers = {
        'accept': '*/*',
        'Authorization': f'Basic {token}',
    }
    params = {'file_name': 'Qr-Code.jpg'}
    files = {'file': qr_code_b}
    requests.post(
        f'https://{domain}/api/v3/trackor/{trackor_id}/file/{qr_field_name}',
        params=params,
        headers=headers,
        files=files,
    )

def make_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#152B42", back_color="transparent")
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    return img_bytes

def get_trackor_ids(trackor_type, domain, token):
    headers = {
        'Authorization': f'Basic {token}',
        'accept': 'application/json', 'Content-Type': 'text/plain',
    }
    params = {
        'fields': 'XITOR_KEY',
        'page': '1','per_page': '100000',
    }
    data = 'is_null(HPT_QRCODE)'
    response = requests.post(
        f'https://{domain}/api/v3/trackor_types/{trackor_type}/trackors/search',
        params=params,
        headers=headers,
        data=data,
    )
    return [data["TRACKOR_ID"] for data in response.json()]

def start(trackor_type, qr_field_name, domain, token):
    trackor_type_id = get_trackor_type_id(trackor_type, domain, token)
    trackor_ids = get_trackor_ids(trackor_type, domain, token)
    for trackor_id in trackor_ids:
        print(trackor_id)
        url = f"https://{domain}/form/ConfigAppForm.do?id={trackor_id}&ttid={trackor_type_id}"
        qr_code_b = make_qr_code(url)
        upload_qrcode(qr_code_b, trackor_id, qr_field_name, domain, token)

data = read_config()
start(data["trackor_type"], data["qr_code_field"], data["domain"], data["token"])