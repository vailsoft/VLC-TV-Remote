import os,json,time,socket,base64,subprocess,urllib.request,urllib.parse
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path

HOST="0.0.0.0"; PORT=8787; VLC_PORT=8080; PASSWORD="vlctv"

HTML=r"""<!doctype html><html lang="pt-BR"><head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>VLC TV Remote</title><style>
*{box-sizing:border-box}body{margin:0;background:#101114;color:#fff;font-family:Arial}
.wrap{max-width:560px;margin:auto;padding:16px}.card{background:#1b1d22;border-radius:18px;padding:16px;margin-bottom:14px}
h1{text-align:center;margin:6px 0 18px}.title{font-size:20px;font-weight:bold;line-height:1.3}
.now{font-size:13px;color:#aaa;margin-top:5px}.status{text-align:center;color:#aaa;font-size:13px;margin:7px}
.progress,.vol{width:100%}.time{display:flex;justify-content:space-between;color:#aaa;font-size:12px}
.grid3{display:grid;grid-template-columns:1fr 1.5fr 1fr;gap:9px;margin-top:12px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:9px}
button{border:0;border-radius:14px;background:#292c33;color:#fff;padding:15px 7px;font-size:15px;font-weight:bold}.main{background:#eee;color:#111}
.list{display:flex;flex-direction:column;gap:8px;margin-top:10px}.ep{font-size:14px;padding:14px;text-align:left}
.ep.selected{outline:2px solid #fff;background:#3b3f48}.ep .mark{float:right;font-size:12px}
.error{color:#ff8080;text-align:center;font-size:12px;min-height:18px}
</style></head><body><div class="wrap"><h1>📺 VLC TV</h1>
<div class="card"><div class="now">REPRODUZINDO AGORA</div><div id="title" class="title">Conectando...</div>
<div id="status" class="status">--</div><input id="seek" class="progress" type="range" min="0" max="1000" value="0">
<div class="time"><span id="cur">00:00</span><span id="len">00:00</span></div>
<div class="grid3"><button onclick="cmd('previous')">⏮ Anterior</button><button class="main" onclick="cmd('pause')">▶ / ⏸</button><button onclick="cmd('next')">Próximo ⏭</button></div>
<div class="grid2"><button onclick="cmd('seek_rel',-30)">↶ 30 s</button><button onclick="cmd('seek_rel',30)">30 s ↷</button></div><div id="error" class="error"></div></div>
<div class="card"><div class="status">Volume</div><input id="vol" class="vol" type="range" min="0" max="100" value="100">
<div class="grid2"><button onclick="cmd('mute')">🔇 Mudo</button><button onclick="cmd('fullscreen')">⛶ Tela cheia</button></div></div>
<div class="card"><div class="status">EPISÓDIOS / PLAYLIST</div><div id="playlist" class="list"></div></div>
</div>
<script>
let dragging=false,$=id=>document.getElementById(id);
function fmt(s){s=Math.max(0,Math.floor(s||0));let h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;return(h?h+':':'')+String(m).padStart(2,'0')+':'+String(x).padStart(2,'0')}
async function api(u){try{return await (await fetch(u,{cache:'no-store'})).json()}catch(e){return null}}
async function cmd(c,v){let u='/cmd?c='+encodeURIComponent(c)+(v!==undefined?'&v='+encodeURIComponent(v):'');let d=await api(u);if(d&&!d.ok)$('error').textContent=d.error||'Erro';else $('error').textContent='';setTimeout(refresh,150)}
$('seek').oninput=()=>dragging=true;$('seek').onchange=e=>{dragging=false;cmd('seek_percent',e.target.value)};
$('vol').oninput=e=>{clearTimeout(window.v);window.v=setTimeout(()=>cmd('volume',e.target.value),100)};
function renderPlaylist(items,currentId){
 const box=$('playlist');box.innerHTML='';
 if(!items.length){box.innerHTML='<div class="status">Nenhum episódio na playlist.</div>';return}
 items.forEach((x,i)=>{
   let b=document.createElement('button');b.className='ep'+(String(x.id)===String(currentId)?' selected':'');
   b.innerHTML=(i+1)+'. '+escapeHtml(x.name)+(String(x.id)===String(currentId)?' <span class="mark">▶ TOCANDO</span>':'');
   b.onclick=()=>cmd('play_item',x.id);box.appendChild(b);
 })
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
async function refresh(){
 let d=await api('/status');if(!d){$('error').textContent='Sem comunicação com VLC';return}
 $('title').textContent=d.title||'Sem vídeo';
 $('status').textContent=d.state==='playing'?'▶ Reproduzindo':d.state==='paused'?'⏸ Pausado':'⏹ '+(d.state||'parado');
 $('cur').textContent=fmt(d.time);$('len').textContent=fmt(d.length);
 if(!dragging&&d.length)$('seek').value=Math.round(d.time/d.length*1000);
 if(d.volume!==undefined)$('vol').value=Math.round(d.volume/256*100);
 let p=await api('/playlist');if(p)renderPlaylist(p.items,d.current_id);
}
setInterval(refresh,1000);refresh();
</script></body></html>"""

def find_vlc():
    for p in [os.getenv("VLC_PATH",""),r"C:\Program Files\VideoLAN\VLC\vlc.exe",r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"]:
        if p and Path(p).exists(): return p
    return None

class VLC:
    def __init__(self):
        self.path=find_vlc()

    def auth(self):
        return "Basic "+base64.b64encode((":"+PASSWORD).encode()).decode()

    def request(self, endpoint, params=None, want_json=True):
        url=f"http://127.0.0.1:{VLC_PORT}{endpoint}"
        if params:
            url+="?"+urllib.parse.urlencode(params)
        req=urllib.request.Request(url,headers={"Authorization":self.auth()})
        with urllib.request.urlopen(req,timeout=4) as r:
            raw=r.read().decode("utf-8","replace")
            if not want_json:
                return raw
            if not raw.strip():
                return {}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {}

    def get(self,endpoint,params=None):
        return self.request(endpoint,params,True)

    def command(self,c,**p):
        # VLC may answer an HTTP command with an empty body.
        # Do not try to decode that body as JSON.
        return self.request("/requests/status.json",
                            {"command":c,**p}, False)

    def start(self):
        if not self.path:
            return False
        subprocess.Popen(
            [self.path,"--extraintf=http","--http-port",str(VLC_PORT),
             "--http-password",PASSWORD],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(40):
            time.sleep(.25)
            try:
                d=self.get("/requests/status.json")
                if isinstance(d,dict):
                    return True
            except:
                pass
        return False

    def status(self):
        return self.get("/requests/status.json")

    def playlist(self):
        d=self.get("/requests/playlist.json")
        out=[]
        def walk(x):
            if isinstance(x,dict):
                if x.get("type")=="leaf" and x.get("id") is not None:
                    out.append({"id":x["id"],
                                "name":x.get("name") or x.get("uri","")})
                for c in x.get("children",[]):
                    walk(c)
            elif isinstance(x,list):
                for c in x:
                    walk(c)
        walk(d)
        return out

vlc = VLC()

def local_ip():
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:s.connect(("8.8.8.8",80));return s.getsockname()[0]
    except:return "127.0.0.1"
    finally:s.close()

class H(BaseHTTPRequestHandler):
    saved_volume=256
    def log_message(self,*a):pass
    def out(self,o):
        b=json.dumps(o,ensure_ascii=False).encode();self.send_response(200)
        self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        u=urllib.parse.urlparse(self.path);q=urllib.parse.parse_qs(u.query)
        try:
            if u.path=="/":
                b=HTML.encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b);return
            if u.path=="/status":
                d=vlc.status()

                def find_text(obj, keys):
                    if isinstance(obj,dict):
                        for k in keys:
                            v=obj.get(k)
                            if isinstance(v,str) and v.strip():
                                return v.strip()
                        for v in obj.values():
                            r=find_text(v,keys)
                            if r:return r
                    elif isinstance(obj,list):
                        for v in obj:
                            r=find_text(v,keys)
                            if r:return r
                    return ""

                meta=find_text(d,["title","episode","filename"])
                if not meta:
                    meta=find_text(d,["name"])
                if not meta:
                    # Last fallback: use the current playlist entry.
                    try:
                        cur=d.get("currentplid")
                        for item in vlc.playlist():
                            if str(item.get("id"))==str(cur):
                                meta=item.get("name","")
                                break
                    except:
                        pass

                self.out({"ok":True,
                          "state":d.get("state"),
                          "title":meta or "Vídeo sem título",
                          "time":d.get("time",0),
                          "length":d.get("length",0),
                          "volume":d.get("volume",0),
                          "current_id":d.get("currentplid")})
                return
            if u.path=="/playlist":self.out({"ok":True,"items":vlc.playlist()});return
            if u.path=="/cmd":
                c=q.get("c",[""])[0];v=q.get("v",[""])[0]
                if c=="pause":vlc.command("pl_pause")
                elif c=="next":vlc.command("pl_next")
                elif c=="previous":vlc.command("pl_previous")
                elif c=="fullscreen":vlc.command("fullscreen")
                elif c=="volume":vlc.command("volume",val=str(round(max(0,min(100,float(v)))*2.56)))
                elif c=="mute":
                    d=vlc.status()
                    cur=int(d.get("volume",256) or 0)
                    if cur>0:
                        H.saved_volume=cur
                        vlc.command("volume",val="0")
                    else:
                        restore=H.saved_volume if H.saved_volume>0 else 256
                        vlc.command("volume",val=str(restore))
                elif c=="seek_percent":
                    d=vlc.status()
                    target=float(d.get("length",0))*max(0,min(1000,float(v)))/1000
                    vlc.command("seek",val=str(int(target)),type="absolute")
                elif c=="seek_rel":
                    d=vlc.status()
                    cur=float(d.get("time",0))
                    total=float(d.get("length",0))
                    target=max(0,min(total,cur+float(v))) if total>0 else max(0,cur+float(v))
                    vlc.command("seek",val=str(int(target)),type="absolute")
                elif c=="play_item":vlc.command("pl_play",id=str(int(v)))
                else:raise ValueError("Comando desconhecido")
                self.out({"ok":True});return
            self.send_response(404);self.end_headers()
        except Exception as e:self.out({"ok":False,"error":str(e)})

if __name__=="__main__":
    if not vlc.start():
        print("VLC não encontrado ou interface HTTP não respondeu.");input("ENTER para sair...")
    else:
        print("\nVLC TV REMOTE V1.5")
        print("CELULAR: http://%s:%d/"%(local_ip(),PORT))
        print("PC e celular precisam estar no mesmo Wi-Fi.")
        print("Se o Firewall perguntar, permita rede privada.\n")
        ThreadingHTTPServer((HOST,PORT),H).serve_forever()
