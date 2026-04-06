#that one enthusiastic swim bro
#應用程式ID:1489533432529813617
#公開金鑰:6234cb9c32858e004a68c66c759f1235222fadfcfe20705089640429276567b5
#權杖:MTQ4OTUzMz_MY_TOKEN_IS_SECRET_OOCGs
TOKEN = "MTQ4OTUzMz_MY_TOKEN_IS_SECRET_OOCGs"

#await    等待結果，但不會卡住整個程式 等資料回來 → 同時可以做其他事
import discord
import aiohttp
import asyncio
import datetime
import json
import time




CHANNEL_ID = 1489570609599090869  
intents = discord.Intents.default()
#意圖（權限設定）

#建立一個 bot（繼承 Discord 的 client）
class MyClient(discord.Client):
    #非同步 asynchronous 這個函式是非同步的（可以用 await）
    async def setup_hook(self):
        # 啟動背景任務 把 check_pool 丟到背景一直執行
        self.bg_task = self.loop.create_task(self.check_pool())
        #back ground  task
        
        # 狀態變數
        self.waiting_reply=False
        self.stop_today = False     # 今天是否停止通知

    async def check_pool(self):
        
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        
        #連線會話 / 請求會話  aiohttp 裡的，管理「你對網站的所有請求」
        #session = 一個「持續的網路連線環境」 ，不用每次都重新打電話，而是保持一條線
        async with aiohttp.ClientSession() as session:
            while not self.is_closed():
                now=datetime.datetime.now().hour
                
                if now<=8 or 22<=now:
                    print('gym now is closed, will check again in 2 hours')
                    self.stop_today=False
                    await asyncio.sleep(3600*2)
                    continue
                    
                    # 👉 如果今天已經按「走」，就不再通知
                if self.stop_today:
                    await asyncio.sleep(3600)
                    continue

                try:#HTTP POST 向伺服器「發送資料並請求回應」
                    async with session.post(
                        'https://cssc.cyc.org.tw/api',
                        headers={"User-Agent": "Mozilla/5.0"},
            #告訴網站「你是誰、用什麼方式來」「我是瀏覽器，不是機器人」
                        
                        ssl=False
                    ) as resp:

                        # 👉 先拿文字（避免 JSON 錯誤）
                        text = await resp.text()
                        print("API回傳：", text,datetime.datetime.now())

                        # 👉 嘗試轉成 JSON
                        data = json.loads(text)

                        # 👉 抓泳池人數
                        people = int(data['swim'][0])
                        print("目前人數：", people)

                        # ========= 判斷 =========
                        msg = None
                        if people < 20:
                            msg = f"🔥 超空！現在只有 {people} 人，走不走？"
                        elif people < 35:
                            msg = f"👌 空！現在 {people} 人，走不走？"

                        # ========= 發送通知 =========
                        if msg and not self.waiting_reply:
                           
                            view = ConfirmView(self)#設定按鈕介面 下面的class
                            await channel.send(msg, view=view)
                            #網路操作等discord回應 發訊息和按鈕



                except Exception as e:
                    print("錯誤：", e)

                await asyncio.sleep(60*5)

    #on_ready event（Discord event） 當 bot 成功登入 Discord 時觸發
    async def on_ready(self):
        print(f"已登入 {self.user}")


# ========= 按鈕 =========
class ConfirmView(discord.ui.View):
    def __init__(self, client):
        
        super().__init__(timeout=60*5)#timeout 多久之後失效
    #呼叫「原本類別的初始化或功能」，我繼承別人的功能 → 但我要先把原本的初始化跑完
    
        self.client = client

    # 👉 按「走」
    @discord.ui.button(label="走", style=discord.ButtonStyle.green)
    async def go(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🏊‍♂️ 出發！今天不再通知", ephemeral=False)

        self.client.stop_today = True
        self.client.waiting_reply = False

    # 👉 按「不走」
    @discord.ui.button(label="不走", style=discord.ButtonStyle.red)
    async def stay(self, interaction: discord.Interaction, button: discord.ui.Button):
                            
                                             #ephemeral=True 讓訊息「只有按按鈕的人看得到」
        await interaction.response.send_message("👌 好，30分鐘後再提醒", ephemeral=False) 

        self.client.waiting_reply = True

        # 👉 30分鐘後恢復通知
        async def delay():
            await asyncio.sleep(1800)
            self.client.waiting_reply = False
           

        asyncio.create_task(delay())


# ========= 啟動 =========


client = MyClient(intents=intents)
client.run(TOKEN)





