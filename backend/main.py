import random
from pathlib import Path
from fastapi import FastAPI,Body,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database import init_db,ensure_user,get_profile,conn

app=FastAPI()
init_db()
BASE=Path(__file__).resolve().parent.parent
app.mount("/static",StaticFiles(directory=BASE/"miniapp"),name="static")

@app.get("/")
def home():
    return FileResponse(BASE/"miniapp/index.html")

@app.post("/api/auth")
def auth(data:dict=Body(...)):
    tid=int(data["telegram_id"])
    ensure_user(tid,data.get("username",""),data.get("first_name","Player"))
    u,i=get_profile(tid)
    return {"user":u,"inventory":i}

@app.get("/api/catalog")
def catalog():
    c=conn();rows=[dict(x) for x in c.execute("SELECT * FROM nft_catalog ORDER BY price").fetchall()];c.close()
    return rows

@app.post("/api/bonus")
def bonus(data:dict=Body(...)):
    tid=int(data["telegram_id"]);ensure_user(tid)
    c=conn();u=c.execute("SELECT stars,bonus_claimed FROM users WHERE telegram_id=?",(tid,)).fetchone()
    if u["bonus_claimed"]:
        r={"ok":False,"message":"Бонус уже получен","stars":u["stars"]}
    else:
        c.execute("UPDATE users SET stars=stars+1000,bonus_claimed=1 WHERE telegram_id=?",(tid,))
        c.commit()
        stars=c.execute("SELECT stars FROM users WHERE telegram_id=?",(tid,)).fetchone()[0]
        r={"ok":True,"message":"+1000 ⭐","stars":stars}
    c.close();return r

def calc(a,b):
    return round(max(1,min(95,a/b*100*0.96)),2)

@app.get("/api/upgrade/suggest/{inventory_id}/{mode}")
def suggest(inventory_id:int,mode:str):
    c=conn()
    stake=c.execute('''SELECT nft_catalog.price FROM inventory JOIN nft_catalog ON nft_catalog.id=inventory.nft_id WHERE inventory.id=?''',(inventory_id,)).fetchone()
    if not stake:c.close();raise HTTPException(404,"NFT not found")
    items=[dict(x) for x in c.execute("SELECT * FROM nft_catalog WHERE price>? ORDER BY price",(stake["price"],)).fetchall()]
    if not items:c.close();raise HTTPException(404,"Target not found")
    if mode.startswith("x"):
        wanted=stake["price"]*float(mode[1:])
        target=min(items,key=lambda x:abs(x["price"]-wanted))
    else:
        wanted=float(mode.replace("%",""))
        target=min(items,key=lambda x:abs(calc(stake["price"],x["price"])-wanted))
    c.close()
    return {"target":target,"chance":calc(stake["price"],target["price"])}

@app.post("/api/upgrade")
def upgrade(data:dict=Body(...)):
    tid=int(data["telegram_id"]);sid=int(data["stake_inventory_id"]);target_id=int(data["target_nft_id"])
    c=conn()
    stake=c.execute('''SELECT inventory.id,nft_catalog.price FROM inventory JOIN nft_catalog ON nft_catalog.id=inventory.nft_id WHERE inventory.id=? AND inventory.telegram_id=?''',(sid,tid)).fetchone()
    target=c.execute("SELECT * FROM nft_catalog WHERE id=?",(target_id,)).fetchone()
    if not stake or not target or target["price"]<=stake["price"]:
        c.close();raise HTTPException(400,"Invalid upgrade")
    ch=calc(stake["price"],target["price"]);won=random.random()*100<ch
    c.execute("DELETE FROM inventory WHERE id=?",(sid,))
    if won:c.execute("INSERT INTO inventory(telegram_id,nft_id) VALUES(?,?)",(tid,target_id))
    c.execute("INSERT INTO upgrades(telegram_id,target_nft_id,chance,won) VALUES(?,?,?,?)",(tid,target_id,ch,int(won)))
    c.commit();c.close()
    return {"won":won,"chance":ch,"target":dict(target)}
