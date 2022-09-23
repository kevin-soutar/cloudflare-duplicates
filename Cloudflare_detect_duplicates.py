import requests
import secretinfo

cloudflare_headers = {
'X-Auth-Email': secretinfo.cloudflare_email ,
'Authorization': secretinfo.cloudflare_api_key,
'Content-Type': 'application/json',
}

def cloudflare_zones(page_num,per_page=100,direction='asc'):
    response = requests.get(f"https://api.cloudflare.com/client/v4/zones?page={page_num}&per_page={per_page}&order=type&direction={direction}", headers=cloudflare_headers)
    return response.json()

def cloudflare_records(page_num,zone_id,per_page=100,direction='asc'):
    response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?page={page_num}&per_page={per_page}&order=type&direction={direction}", headers=cloudflare_headers)
    return response.json()


page_num = 1
original_zone =["No Result"]
zone_ids = {}

while original_zone != [] or None:
    output = cloudflare_zones(page_num)
    page_num = page_num + 1
    original_zone = output['result']
    for domain in output['result']:
        zone_ids.setdefault(domain['id'], set()).add(domain['name'])

a_records = {}

for zone_id in zone_ids:
    page_num =1
    original_output =["No Result"]
    while original_output != []:
        output = cloudflare_records(page_num,zone_id=zone_id)
        page_num = page_num + 1
        original_output = output['result']
        for id, record in enumerate(output["result"]):
            if record["type"] == "A":
                a_records.setdefault(record["content"], set()).add(record["name"])

results = filter(lambda x: len(x) >1, a_records.values())

email_text = f"<html><body> Hostnames that are duplicates are: <br>"

for subdomains in list(results):
    email_text = f"{email_text} <br> Duplicates:<br>"
    for val in subdomains:
        email_text = f"{email_text}{val}<br>"
email_text = f"{email_text}</body></html>"

postmark_headers = {
    'Accept': 'application/json',
    'X-Postmark-Server-Token': secretinfo.postmark_server_token,
}

new_email = {
    'From': secretinfo.postmark_send_email,
    'To': secretinfo.postmark_receive_email,
    'Subject': 'Duplicate DNS Records Detected',
    'HtmlBody': email_text,
    'MessageStream': 'outbound',
}
requests.post('https://api.postmarkapp.com/email', headers=postmark_headers, json=new_email)