import httpx,os,json

os.system('cls')

session = httpx.Client()

team_id = "the team id of the server to be pulled"
token = "enter your 'hmac_signed_session' token"

session.headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-length": "131",
    "content-type": "application/json",
    "cookie": f'hmac_signed_session={token}; authenticated=true',
    "guilded-viewer-platform": "desktop",
    "origin": "https://www.guilded.gg",
    "referer": "https://www.guilded.gg/",
    "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

r1 = session.get(url=f'https://www.guilded.gg/api/teams/{team_id}/members')
counter = 1

for x in r1.json()['members']:
    try:
        profile_picture = str(x['profilePicture']).replace('webp','png')
        
        if not profile_picture == "None":
            print(f"[{counter}] Scraped -> " + profile_picture)
            with open('pfps.txt','a',encoding='utf-8') as f:
                f.write(f'{profile_picture}\n')
        counter += 1
    except:
        counter += 1
        continue  

print(f'Completed! Total Scraped URLs -> {counter}.')