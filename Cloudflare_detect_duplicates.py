import requests
import secretinfo

cloudflare_headers = {
    'X-Auth-Email': secretinfo.cloudflare_email ,
    'Authorization': secretinfo.cloudflare_api_key,
    'Content-Type': 'application/json',
}

response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{secretinfo.cloudflare_zone_id}/dns_records", headers=cloudflare_headers)
output = response.json()

a_records = {}

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
