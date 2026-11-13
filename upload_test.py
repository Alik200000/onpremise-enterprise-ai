import urllib.request

with open('c:/Users/ASUS Vivobook/Documents/antigravity/onpremise-enterprise-ai/data/samples/KM_04_2026_REAL_DRAWING.dxf', 'rb') as f:
    dxf_data = f.read()

boundary = '----WebKitFormBoundarySampleUpload'
header = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="KM_04_2026_REAL_DRAWING.dxf"\r\n'
    f'Content-Type: application/octet-stream\r\n\r\n'
).encode('utf-8')
footer = f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8080/api/upload',
    data=header + dxf_data + footer,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode('utf-8'))
