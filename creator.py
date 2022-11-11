import httpx,json,string,sqlite3,threading
from random import choice,choices
from time import sleep
from pystyle import System
from modules.console import Tools,Console
from modules.username_creator import getUsername

System.Size(200,40)

class Generator:
    def __init__(self) -> None: 
        self.tools = Tools()
        self.tools.clear()
        self.tools.printLogo()
        
        self.config_file = json.load(open('data/config.json','r',encoding='utf-8'))
        self.usernames = open('data/usernames.txt','r',encoding='utf-8').read().splitlines()
        self.proxies = open('data/proxies.txt','r',encoding='utf-8').read().splitlines()
        self.bioes = open('data/bioes.txt','r',encoding='utf-8').read().splitlines()
        self.taglines = open('data/taglines.txt','r',encoding='utf-8').read().splitlines()
        self.pfps = open('data/pfps.txt','r',encoding='utf-8').read().splitlines()

        self.save_method = self.config_file['save_method']
        self.threads = self.config_file['threads']
        self.invite_code = self.config_file['invite_code']
        self.use_proxy = self.config_file['use_proxy']
        self.random_usernames = self.config_file['random_usernames']
        
        self.created = 0
        self.tools.setTitle(self.threads, len(self.proxies), self.created)
        
        self.console = Console()
        
        self.connection = sqlite3.connect('saved/database.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        
        self.cursor.execute('CREATE TABLE IF NOT EXISTS accounts (ID TEXT, Username TEXT, Password TEXT, Mail TEXT, Token TEXT)')
        
        self.lock = threading.Lock()
        
        if len(self.usernames) == 0: self.random_usernames = 'y'
        if len(self.proxies) == 0: self.use_proxy = 'n'
            
    def print(self, arg):
        self.lock.acquire()
        print(arg)
        self.lock.release()
        
    def getClientID(self):
        chars = '0123456789abcdef'
        value1 = "".join(choices(chars,k=8))
        value2 = "".join(choices(chars,k=4))
        value3 = "".join(choices(chars,k=4))
        value4 = "".join(choices(chars,k=4))
        value5 = "".join(choices(chars,k=12))
        return "-".join((value1,value2,value3,value4,value5))
    

    def formatCookies(self, items: dict) -> str:
        cookies_text = str()
        for cookie in items: cookies_text += f'{cookie[0]}={cookie[1]}; '
        return cookies_text[:len(cookies_text)-2]
    
    def getCookies(self, session: httpx.Client) -> str:
        while True:
            try:
                headers = {
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.7",
                    "dnt": "1",
                    "guilded-client-id": self.getClientID(),
                    "guilded-viewer-platform": "desktop",
                    "referer": "https://www.guilded.gg/",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "sec-gpc": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
                    "x-requested-with": "XMLHttpRequest"
                }

                r = session.get(url='https://www.guilded.gg/api/me?isLogin=false&v2=true',headers=headers, timeout=15)
                return self.formatCookies(r.cookies.items()),r.cookies.get('guilded_mid')
            except httpx.ProxyError:
                self.console.printe('Proxy error, retrying...')
                continue

    def joinServer(self, session: httpx.Client):
       session.headers['content-length'] = "19"
       
       r = session.put(url=f'https://www.guilded.gg/api/invites/{self.invite_code}', data=json.dumps({"type":"consume"}))
       
       if r.status_code == 200:
           self.console.printjs(f"{self.invite_code} invite code joined.")
       else:
           self.console.printe('Joining server.')
           # * print(r.text,r.status_code) debugging 
    
    def Humanization(self, session: httpx.Client, id: str):
        while True:
            bio = choice(self.bioes)
            bio = bio.replace('"','').replace('ı','i').replace('ğ','g').replace('İ','I').replace('ş','s')  # ! PLEASE USE UTF-8 CODING @GUILDED.GG
            tagline = choice(self.taglines)
            payload = {
                "userId": id,
                "aboutInfo": {
                    "bio": bio,
                    "tagLine": tagline
                }
            }


            session.headers["content-length"] = str(len(json.dumps(payload)))
            
            r = session.put(url=f'https://www.guilded.gg/api/users/{id}/profilev2', data=json.dumps(payload))
            
            
            session.headers["content-length"] = str(len(json.dumps({"imageUrl": choice(self.pfps)})))
            
            r2 = session.post(url='https://www.guilded.gg/api/users/me/profile/images', data=json.dumps({"imageUrl": choice(self.pfps)}))
            
            if r.status_code == 200 and r2.status_code == 200:
                self.console.printhm('Bio and pfp successfully changed.')
                break
            elif 'Bio has invalid characters' in r.text:
                self.console.printe(f'Invalid bio: \'{bio}\', retrying...')
                sleep(1)
            else:
                self.console.printe('Bio Error! Retrying...')
                # * print(r.text,r.status_code) debugging
        
    def saveData(self, id: str, username: str, password: str, mail: str, token: str):
        if self.save_method == 'both' or self.save_method =='sqlite':
            self.cursor.execute('Insert into accounts Values(?,?,?,?,?)', (id, username, password, mail, token))
            self.connection.commit()
        
        if self.save_method == 'both' or self.save_method == 'text':
            with open('saved/accounts.txt','a',encoding='utf-8') as f:
                f.write(f'{username}:{mail}:{password}:{token}\n')
    
    def createAccount(self):
        while True:
            try:
                if self.use_proxy == 'y':
                    proxy = choice(self.proxies)

                    proxies = {
                        "http://": f"http://{proxy}",
                        "https://": f"http://{proxy}"
                    }

                    session = httpx.Client(proxies=proxies)
                else:
                    session = httpx.Client()
                cookies = self.getCookies(session)

                str_cookies = cookies[0]
                client_id = cookies[1]

                if self.random_usernames == 'y':
                    username = getUsername()
                else:
                    username = choice(self.usernames)
                
                text = choices(string.ascii_lowercase+string.digits,k=16)
                
                mail_text = str()
                for x in text: mail_text += x
                
                mail_address = f"{mail_text}{choice(['@gmail.com','@yahoo.com','@outlook.com','@hotmail.com'])}"
                
                password = "".join(choices(string.ascii_letters+string.digits,k=12))
                
                payload = {
                    "extraInfo": {
                        "platform": "desktop"
                    },
                    "name": username,
                    "email": mail_address,
                    "password": password,
                    "fullName": username
                }

                session.headers = {
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "content-length": str(len(json.dumps(payload))),
                    "content-type": "application/json",
                    "cookie": str_cookies,
                    "guilded-client-id": client_id,
                    "guilded-stag": "".join(choices('0123456789abcdef',k=32)),
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

                while True:
                    try:
                        r = session.post(url='https://www.guilded.gg/api/users?type=email', json=payload, timeout=30)
                        break
                    except:
                        continue
                
                session.headers["cookie"] = str_cookies + "; " + self.formatCookies(r.cookies.items())
                
                token = r.cookies.get('hmac_signed_session')
                if r.status_code == 200 and token != None:
                    id = r.json()['user']['id']
                    self.console.printsc(f'{username} created by name.')
                    self.created += 1
                    self.tools.setTitle(self.threads, len(self.proxies), self.created)

                    self.saveData(id,username,password,mail_address,token)
                    self.joinServer(session)
                    self.Humanization(session, id)

                elif "You have been banned" in r.text:
                    self.console.printe(f'Banned IP: {proxy}, retrying...')
                    sleep(1)  
                else:
                    self.console.printe('Account not created, retrying...')
                    sleep(1)
            except Exception as e:
                self.console.printe(str(e).capitalize()+".")
                sleep(1)
               
    def Run(self):
        while threading.active_count() < self.threads+1:
            threading.Thread(target=self.createAccount).start()      
            sleep(0.75) 
            
if __name__ == '__main__':
    gen = Generator()
    gen.Run()
    