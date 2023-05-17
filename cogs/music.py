import discord,os,json,math,re,requests,typing
import time as t
from datetime import *
from pytube import *
from discord.ext import commands
from discord import app_commands
import youtube_dl
from asyncio import run_coroutine_threadsafe
from numerize import numerize
from fakemodule import ytb
from gtts import gTTS

class MyView(discord.ui.View): 
    def __init__(self,em,server):
        super().__init__(timeout=None)
        self.em=em
        self.count_numepage={}
        self.count_numepage[server]=0
        self.maxpage=len(em)
        self.back2.disabled =True
        self.back.disabled =True
        self.back.style=discord.ButtonStyle.grey
        self.back2.style=discord.ButtonStyle.grey
        self.count.label=f"0/{len(em)-1}"
        if self.count_numepage[server]==self.maxpage-1:
            self.go2.disabled =True
            self.go.disabled =True
            self.go.style=discord.ButtonStyle.grey
            self.go2.style=discord.ButtonStyle.grey

    async def button_update(self,server):
        text=f"{self.count_numepage[server]}/{self.maxpage-1}"
        self.count.label=text
        if self.count_numepage[server]==0:
            self.back2.disabled =True
            self.back.disabled =True
            self.back.style=discord.ButtonStyle.grey
            self.back2.style=discord.ButtonStyle.grey
        else:
            self.back2.disabled =False
            self.back.disabled =False
            self.back.style=discord.ButtonStyle.green
            self.back2.style=discord.ButtonStyle.green
        if self.count_numepage[server]==self.maxpage-1:
            self.go2.disabled =True
            self.go.disabled =True
            self.go.style=discord.ButtonStyle.grey
            self.go2.style=discord.ButtonStyle.grey
        else:
            self.go2.disabled =False
            self.go.disabled =False
            self.go.style=discord.ButtonStyle.green
            self.go2.style=discord.ButtonStyle.green

    @discord.ui.button( style=discord.ButtonStyle.primary, emoji="⏪")
    async def back2(self, interaction: discord.Interaction, button: discord.ui.Button):
        server= interaction.guild_id
        embedd = self.em
        if self.count_numepage[server] ==0:
            await interaction.response.send_message('Đang ở trang đầu!!!',ephemeral=True)  
            return
        self.count_numepage[server]=0
        await self.button_update(server)
        await interaction.response.edit_message(embed=embedd[0].set_footer(text="Trang: 0"),view=self)
    @discord.ui.button( style=discord.ButtonStyle.primary, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        server= interaction.guild_id
        embedd = self.em     
        if self.count_numepage[server] ==0:
            await interaction.response.send_message('Đang ở trang đầu!!!',ephemeral=True)  
            return
        self.count_numepage[server]-=1
        await self.button_update(server)
        count=self.count_numepage[server]
        await interaction.response.edit_message(embed=embedd[count].set_footer(text=f"Trang: {count}"),view=self)
    @discord.ui.button(style=discord.ButtonStyle.red)
    async def count(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_message('Đã Hủy',delete_after=3)
        await ctx.message.delete()
        self.stop()

    @discord.ui.button( style=discord.ButtonStyle.primary, emoji="➡️")
    async def go(self, interaction: discord.Interaction, button: discord.ui.Button):
        server= interaction.guild_id
        embedd = self.em
        if self.count_numepage[server] ==self.maxpage-1:
            await interaction.response.send_message('Đang ở trang cuối!!!',ephemeral=True)  
            return
        self.count_numepage[server]+=1
        count=self.count_numepage[server]
        await self.button_update(server)
        await interaction.response.edit_message(embed=embedd[count].set_footer(text=f"Trang: {count}"),view=self)

    @discord.ui.button( style=discord.ButtonStyle.primary, emoji="⏩")
    async def go2(self, interaction: discord.Interaction, button: discord.ui.Button):
        server= interaction.guild_id
        embedd = self.em
        maxpagee=self.maxpage-1
        if self.count_numepage[server] ==maxpagee:
            await interaction.response.send_message('Đang ở trang cuối!!!',ephemeral=True)  
            return
        self.count_numepage[server]=maxpagee
        await self.button_update(server)

        await interaction.response.edit_message(embed=embedd[maxpagee].set_footer(text=f"Trang: {maxpagee}"),view=self)



class music(commands.Cog):
    def __init__(self,bot):
        self.bot =bot
        self.laspositon={}
        self.votesk={}
        self.is_playing = {}
        self.is_paused={}
        self.music_queue={}
        self.queueIndex ={}
        self.viewww=discord.ui.View()
        self.ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
        self.ffmpeg_options = {'options': '-vn'}
        self.ytdl = youtube_dl.YoutubeDL(self.ytdl_format_options)
        self.vc = {}
    def creat_embed(self, ctx, song,why):
        title = song['ti']
        link = song['link']
        thumbnail = song['thum']
        you=song['you']
        day=song['day']
        vieww=song['vieww']
        image=song['image']
        channel=song['channel']
        time=song['time']
        author = ctx.user
        avatar = author.avatar.url
        embed = discord.Embed(color=discord.Colour.random())
        if why == "add":
            embed.title="Thêm vào danh sách phát:"
        if why == "delete":
            embed.title="Đã xóa bài hát:"
        if why == "now":
            embed.title="Đang chơi:"
        if why == "loop":
            embed.title="Lặp bài hát:"
        embed.description=f'[{title}]({link})'
        embed.add_field(name="Kênh youtube",value=f'[{you}]({channel})',inline=False)
        embed.add_field(name="Ngày Xuất Bản",value=day)
        embed.add_field(name="Số Người Xem",value=vieww)
        embed.add_field(name="Thời Lượng",value=time)
        embed.set_thumbnail(url=thumbnail)
        embed.set_image(url=image)
        embed.set_footer(text=f'Bài hát được thêm bởi: {str(author)}', icon_url=avatar)
        channell=discord.ui.Button(style=discord.ButtonStyle.link,url=channel,label=you)
        videol=discord.ui.Button(style=discord.ButtonStyle.link,url=link,label="VIDEO")
        four=discord.ui.Button(style=discord.ButtonStyle.link,
                               url="https://www.youtube.com/channel/UCFINNqRcNcOAemuyKdBiDpA?sub_confirmation=1",
                               label="Four Gaming Studio")
        a=self.viewww
        a.clear_items()
        a.add_item(channell)
        a.add_item(videol)
        a.add_item(four)
        return {"em":embed,
                "view":a}
    def clearlist(self,ctx):
        id =int(ctx.guild.id)
        self.music_queue[id]=[]
    def messem(self,ctx,why):
        if why == "pnotvoice":
            why = "Bạn Cần phải ở trong phong voice mới được thực hiện lệnh này!"
        if why == "notlist":
            why = "Cần ít nhất một bài hát trong hàng chờ mới sử dụng được lệnh này!"
        if why == "bnotvoice":
            why = "Bot không ở trong phòng voice!"
        embed = discord.Embed(title=why,description='', color=discord.Colour.random())
        embed.set_footer(text=f'Người sử dụng lệnh: {str(ctx.user)}', icon_url=ctx.user.avatar.url)
        return embed
    @commands.Cog.listener()
    async def on_ready(self):
        print("setup")
        await self.bot.tree.sync()
        for guild in self.bot.guilds:
            id =int(guild.id)
            self.laspositon[id]=0
            self.music_queue[id]=[]
            self.vc[id]=None
            self.votesk[id]=[]
            self.is_paused[id]=False
            self.is_playing[id]=False
        print("done")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # if the trigger was the bot and the action was joining a channel
        id = int(member.guild.id)
        if member.id != self.bot.user.id and before.channel != None and after.channel != before.channel:
            remainingChannelMembers = before.channel.members
            if len(remainingChannelMembers) == 1 and remainingChannelMembers[0].id == self.bot.user.id:
                self.is_playing[id] = False
                self.is_paused[id] = False
                self.vc[id]==None
                await before.channel.send("im out")
                self.clearlist(member)
                await self.vc[id].disconnect()
                
        if member.id != self.bot.user.id and before.channel == None and after.channel != before.channel:
            remainingChannelMembers = after.channel.members
            if len(remainingChannelMembers) >= 1 and remainingChannelMembers[0].id != self.bot.user.id:
                if self.vc[id]==None:
                    self.vc[id]=await after.channel.connect()




    async def join_vc(self,ctx,channel):
        id = int(ctx.guild.id)
        if self.vc[id]==None or not self.vc[id].is_connected():
            self.vc[id]=await channel.connect()
            if self.vc[id]==None:
                await ctx.send("Không thể kết nối tới voice")
                return
        else:
            await self.vc[id].move_to(channel)

    
    def parse_duration(self,duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} Ngày'.format(days))
        if hours > 0:
            duration.append('{} Giờ'.format(hours))
        if minutes > 0:
            duration.append('{} Phút'.format(minutes))
        if seconds > 0:
            duration.append('{} Giây'.format(seconds))

        return ' '.join(duration)
    def search_YT(self,search):
        youtube = ytb.youtube_authenticate()
        if any(c in search for c in ('https://', 'http://')):
            video_id = ytb.get_video_id_by_url(search)
            response = ytb.get_video_details(youtube, id=video_id)
            item=ytb.print_video_infos(youtube,response)
            link=search
        else:
            response = ytb.search(youtube, q=search, maxResults=1)
            items = response.get("items")
            video_id = items[0]["id"]["videoId"]
            link=f'https://www.youtube.com/watch?v={video_id}'
            video_response = ytb.get_video_details(youtube, id=video_id)
            item=ytb.print_video_infos(youtube,video_response)

        channel=item['linkchannel']
        image=item['imagevideo']
        thum=item['imagechannel']
        vieww=numerize.numerize(int(item['views']))
        day=item['Publish_time']
        you=item['Channel_name']
        ti=item['Title']
        time=item['Duration']
        time=self.parse_duration(time)
        a=self.ytdl.extract_info(link,download=False)
        url=a['url']
        return{'where':url,'link':link,'ti':ti,'image':image,'vieww':vieww,
            'you':you,'day':day,'time':time,'channel':channel,'thum': thum
        }
    def play_next(self, ctx):
        channel = self.bot.get_channel(ctx.channel_id)
        id = int(ctx.guild.id)
        if self.vc[id].is_playing==True:
            pass
        if self.music_queue[id] !=[]:
            self.music_queue[id].pop(0)
        if self.music_queue[id] !=[]:
            song = self.music_queue[id][0][0]
            message = self.creat_embed(ctx, song,"now")
            coro =  channel.send(embed=message['em'],view=message['view'])
            fut = run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].play(discord.FFmpegOpusAudio(song['where'], **self.ffmpeg_options), after=lambda e: self.play_next(ctx))
        else:
            em= discord.Embed(title="Tất cả bài hát trong danh sách đã được phát hết",description="",color=discord.Colour.random())
            coro =  channel.send(embed=em)
            fut = run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass
            self.is_playing[id] = False

    async def play_music(self, ctx: discord.Interaction) -> None:
        id = int(ctx.guild.id)
        self.is_playing[id] = True
        self.is_paused[id] = False
        if self.vc[id]==None or not self.vc[id].is_connected():
            await self.join_vc(ctx, self.music_queue[id][0][1])
        song = self.music_queue[id][0][0]
        self.vc[id].play(discord.FFmpegOpusAudio(song['where'], **self.ffmpeg_options), after=lambda e: self.play_next(ctx))
        self.laspositon=datetime.now().strftime("%H:%M:%S")
        message = self.creat_embed(ctx, song,"now")
        await ctx.followup.send(embed=message['em'],view=message['view'])
    @app_commands.command(name="say")
    @app_commands.describe(txt="Văn bản cần nói")
    async def say(self, ctx: discord.Interaction,*,txt:str) -> None:
        await ctx.response.defer()
        id = int(ctx.guild.id)
        try:
            userChannel = ctx.user.voice.channel
        except:
            await ctx.followup.send("Làm ơn kết nối phòng voice trước khi thực hiện lệnh này.")
            return
        song = gTTS(text=txt, lang="vi", slow=False)
        source = discord.FFmpegAudio(song)
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f'Now playing:')
  
    @app_commands.command(name="add")
    @app_commands.describe(url="Từ Khóa Hoặc Link Trên Youtube!")
    async def add(self,  ctx: discord.Interaction,*,url:str) -> None:
        """Thêm bài hát vào danh sách phát"""
        search = "".join(url)
        await ctx.response.defer()
        id = int(ctx.guild.id)
        try:
            userChannel = ctx.user.voice.channel
        except:
            await ctx.followup.send(embed=self.messem(ctx,"Làm ơn kết nối phòng voice trước khi thực hiện lệnh này."))
            return
        song = self.search_YT(search)
        if type(song) == type(True):
            await ctx.followup.send(embed=self.messem(ctx,"Bủ bủ đả dả lờ mao, sai từ khóa hoặc link."))
        else:
            self.music_queue[id].append([song, userChannel])
            message = self.creat_embed(ctx, song,"add")
            await ctx.followup.send(embed=message['em'],view=message['view'])  
    @app_commands.command(name="play")
    @app_commands.describe(url="Chơi nhạc trên youtube hoặc spotyfi!")
    async def play(self,  ctx: discord.Interaction,*,url:str) -> None:
        """Chơi nhạc trên youtube hoặc spotyfi!"""
        search = "".join(url)
        await ctx.response.defer()
        id = int(ctx.guild.id)
        try:
            userChannel = ctx.user.voice.channel
        except:
            await ctx.followup.send(embed=self.messem(ctx,"Làm ơn kết nối phòng voice trước khi thực hiện lệnh này."))
            return
        
        if "/playlist/" in search or '/album/' in search:
            if "/playlist/" in search:
                idl=ytb.getidspo(search)
                a=ytb.playlist(idl)
            if '/album/' in search:
                idl=ytb.getidspo(search)
                a=ytb.ambum(idl)
            for i in a:
                b = ytb.songbyid(i)
                search=f"{b['name']} lyrics - {b['artists']}"
                song = self.search_YT(search)
                self.music_queue[id].append([song, userChannel])
                if not self.is_playing[id]:
                    await self.play_music(ctx)
                else:
                    message = self.creat_embed(ctx, song,"add")
                    await ctx.followup.send(embed=message['em'],view=message['view'])
            return
                
        if "list=" in search:
            playlist = Playlist(search)
            if playlist.video_urls == []:
                await ctx.followup.send(embed=self.messem(ctx,"Bủ bủ đả dả lờ mao, link bị lỗi!, hãy chắc chắn đường link này Không do youtube tạo ra!"))
                return
            else:
                for a in playlist.video_urls:
                    song = self.search_YT(a)
                    self.music_queue[id].append([song, userChannel])
                    if not self.is_playing[id]:
                        await self.play_music(ctx)
                    else:
                        message = self.creat_embed(ctx, song,"add")
                        await ctx.followup.send(embed=message['em'],view=message['view'])
                return
        else:
            if "/track/" in search:
                idl=ytb.getidspo(search)
                a = ytb.songbyid(idl)
                search=f"{a['name']} - {a['artists']}"
                song = self.search_YT(search)
            else: song = self.search_YT(search)
        if type(song) == type(True):
            await ctx.followup.send("Bủ bủ đả dả lờ mao, sai từ khóa hoặc link.")
        else:
            self.music_queue[id].append([song, userChannel])
            if self.is_playing[id] is not True:
                await self.play_music(ctx)
            else:
                message = self.creat_embed(ctx, song,"add")
                await ctx.followup.send(embed=message['em'],view=message['view'])

    @app_commands.command(name="join")
    async def join(self, ctx: discord.Interaction) -> None:
        """Tham Gia Kênh Voice"""
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.response.send_message(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            userChannel = ctx.user.voice.channel
            await self.join_vc(ctx, userChannel)
            await ctx.response.send_message(embed=self.messem(ctx,f'Bot đã tham gia phòng voice {userChannel}'))

    @app_commands.command(name="leave")
    async def leave(self, ctx: discord.Interaction) -> None:
        """Rời Phòng Voice"""
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.response.send_message(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.response.send_message(embed=self.messem(ctx,"bnotvoice"))
            return
        id = int(ctx.guild.id)
        self.is_playing[id] = False
        self.is_paused[id] = False
        self.clearlist(ctx)
        if self.vc[id] != None:
            await ctx.response.send_message("Bot đã rời phòng voice")
            await self.vc[id].disconnect()
            self.vc[id] = None
    @app_commands.command(name="clear")
    async def clear(self, ctx: discord.Interaction) -> None:
        """Xóa Tất Cả Bài Hát Có Trong Danh Sách"""
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.response.send_message(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.music_queue[id] != []:
            self.clearlist(ctx)
            self.is_playing[id] = False
            self.is_paused[id] = False
            self.vc[id].stop()
            await ctx.response.send_message(embed=self.messem(ctx,"Tất cả bài hát có trong danh sách đã được xóa."))
    @app_commands.command(name="skip")
    async def skip(self, ctx: discord.Interaction) -> None:
        """Bỏ Qua Bài Hát Đang Phát"""
        await ctx.response.defer()
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.followup.send(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.followup.send(embed=self.messem(ctx,"bnotvoice"))
            return
        if len(self.music_queue[id]) -1 <=0:
            await ctx.followup.send(embed=self.messem(ctx,"notlist"))
            return
        voter = ctx.user.id
        votesk=self.votesk[id]
        voice=self.vc[id]
        total=len(votesk)
        rolelist=['Admin']
        if any(role in ctx.user.roles for role  in rolelist) or voter==664052500571226112:
            votesk.clear()
            self.vc[id].pause()
            self.music_queue[id].pop(0)
            await self.play_music(ctx)
            return
        max=len(voice.channel.members)-1
        if total >= max//2:
            votesk.clear()
            self.vc[id].pause()
            self.music_queue[id].pop(0)
            await self.play_music(ctx)
            return
        elif voter not in votesk:
            votesk.append(voter)
            voice=self.vc[id]
            total=len(votesk)
            max=len(voice.channel.members)-1

            if total >= max//2:
                votesk.clear()
                self.vc[id].pause()
                self.music_queue[id].pop(0)
                await self.play_music(ctx)
                return
            else:
                await ctx.followup.send(embed=self.messem(ctx,'Số Phiếu Đã Được Cập Nhật **{}/{}**'.format(total,max//2)))
                return

        else:
            await ctx.followup.send(embed=self.messem(ctx,'Bạn Đã Bỏ Phiếu rồi.'))
            return
            

    @app_commands.command(name="remove")
    async def remove(self, ctx: discord.Interaction, number: int) -> None:
        """Xóa Bài Hát Trong Danh Sách Hàng Đợi"""
        await ctx.response.defer()
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.followup.send(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.followup.send(embed=self.messem(ctx,"bnotvoice"))
            return
        if len(self.music_queue[id]) -1 <=0:
            await ctx.followup.send(embed=self.messem(ctx,"notlist"))
            return
        
        if number ==None:
            await ctx.followup.send(embed=self.messem(ctx,"Thiếu số thứ tự bài hát trong hàng chờ!"))
            return
        
        if self.music_queue[id] != []:
            song = self.music_queue[id].pop(number)
            message = self.creat_embed(ctx, song[0],'delete')
            await ctx.followup.send(embed=message['em'],view=message['view'])

        if self.music_queue[id] == []:
            # clear queue and stop playing
            if self.vc[id] != None and self.is_playing[id]:
                self.is_playing[id] = False
                self.is_paused[id] = False
                self.vc[id].stop()

    @app_commands.command(name="pause")
    async def pause(self, ctx: discord.Interaction) -> None:
        """Dừng Phát Bài Hát Đang Phát"""
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.response.send_message(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.response.send_message(embed=self.messem(ctx,"bnotvoice"))
            return
        if self.is_playing[id]:
            await ctx.response.send_message(embed=self.messem(ctx,"Tạm dừng phát nhạc!"))
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()

    # Resume Command

    @app_commands.command(name="resume",)
    async def resume(self, ctx: discord.Interaction) -> None:
        """Phát Bài Hát Đang Dừng"""
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.response.send_message(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.response.send_message(embed=self.messem(ctx,"bnotvoice"))
            return
        if self.is_paused[id]:
            await ctx.response.send_message(embed=self.messem(ctx,"Tiếp tục phát nhạc!"))
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()
    @app_commands.command(name="volume")
    async def volume(self, ctx: discord.Interaction, volume: int)-> None:
        """Changes the player's volume"""
        id = int(ctx.guild.id)
        if ctx.user.voice == None:
            await ctx.response.send_message(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.response.send_message(embed=self.messem(ctx,"bnotvoice"))
            return
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")


    @app_commands.command(name="now")
    async def now(self, ctx: discord.Interaction) -> None:
        """Hiển Thị Bài Hát Đang Phát Và Bài Hát Tiếp Theo"""
        id = int(ctx.guild.id)
        await ctx.response.defer()
        if ctx.user.voice == None:
            await ctx.followup.send(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.followup.send(embed=self.messem(ctx,"bnotvoice"))
            return
        if self.music_queue[id]==[]:
            await ctx.followup.send(embed=self.messem(ctx,"notlist"))
            return
        queue = discord.Embed(title="Bài hát hiện tại và kế tiếp!",description='',color=discord.Colour.random())
        queue.add_field(name="Đang phát:",value=f"[{self.music_queue[id][0][0]['ti']}]({self.music_queue[id][0][0]['link']})",inline=False)
        if len(self.music_queue[id])>=2:
            queue.add_field(name="Kết tiếp:",value=f"[{self.music_queue[id][1][0]['ti']}]({self.music_queue[id][1][0]['link']})",inline=False)
        await ctx.followup.send(embed=queue)

    @app_commands.command(name="list")
    async def list(self, ctx: discord.Interaction) -> None:
        """Hiển Thị Danh Sách Phát Bài Hát"""
        id = int(ctx.guild.id)
        await ctx.response.defer()
        if ctx.user.voice == None:
            await ctx.followup.send(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.followup.send(embed=self.messem(ctx,"bnotvoice"))
            return
        if self.music_queue[id]==[]:
            await ctx.followup.send(embed=self.messem(ctx,"notlist"))
            return
        server= ctx.guild_id
        id = int(ctx.guild.id)
        end=10
        firt=0
        index=0
        embeds=[]
        cc=len(self.music_queue[id])/end
        if cc==0:
            cc=1
        for i in range(math.ceil(cc)):
            aa=self.music_queue[id]
            song=aa[firt:end]
            firt=end
            end+=10
            embed=discord.Embed(title="Danh Sách 10 Bài Hát", color=discord.Colour.random())
            txt=""
            for abc in song:
                txt+= f"{index} | [{abc[0]['ti']}]({abc[0]['link']})\n"
                index+=1
            embed.description=txt
            embeds.append(embed)
        await ctx.followup.send(embed=embeds[0].set_footer(text="Trang: 0"), view=MyView(embeds,server))

    @app_commands.command(name='loop')
    async def _loop(self, ctx: discord.Interaction) -> None:
        """Loops the currently playing song."""
        id = int(ctx.guild.id)
        await ctx.response.defer()
        if ctx.user.voice == None:
            await ctx.followup.send(embed=self.messem(ctx,"pnotvoice"))
            return
        if self.vc[id] == None:
            await ctx.followup.send(embed=self.messem(ctx,"bnotvoice"))
            return
        if self.music_queue[id]==[]:
            await ctx.followup.send(embed=self.messem(ctx,"notlist"))
            return
        
        song =self.music_queue[id][0]
        self.music_queue[id].insert(1,song)
        message = self.creat_embed(ctx, song,"loop")
        await ctx.followup.send(embed=message['em'],view=message['view'])

    @app_commands.command(name="postchannel")
    @app_commands.describe(channel_url="Link Kênh Trên Youtube!")
    async def postchannel(self, ctx: discord.Interaction,*,channel_url:str=None) -> None:
        """Hiển Thị Thông Tin Kênh Youtube"""
        rolelist=['Admin',"Youtuber"]
        if any(role.name in rolelist  for role  in ctx.user.roles):
            try:
                with open('data.json','r') as expp:
                    users = json.load(expp)
                id= users[str(ctx.guild.id)]
            except:
                return await ctx.response.send_message(embed=self.messem(ctx,"Bạn chưa đặt kênh đăng video để thực hiện lênh này!"))
            if channel_url==None:
                return await ctx.response.send_message("url không được để trống!")
            if channel_url:
                youtube = ytb.youtube_authenticate()
                if '/@' in channel_url:
                    r = requests.get(channel_url, allow_redirects=True)
                    channel_id=(re.search(r'(?<=<link rel="canonical" href="https:\/\/www\.youtube\.com\/channel\/)(-?\w+)*(?=">)', r.text).group(0)) 
                else:
                    channel_id = ytb.get_channel_id_by_url(youtube, channel_url)
                response = ytb.get_channel_details(youtube, id=channel_id)

                snippet = response["items"][0]["snippet"]
                statistics = response["items"][0]["statistics"]
                channel_country = snippet["country"]
                channel_description = snippet["description"]
                channel_creation_date = snippet["publishedAt"]
                channel_creation_date=ytb.time_public(channel_creation_date)
                channel_title = snippet["title"]
                res = 0
                max_image = None
                for item in snippet['thumbnails']:
                    if res < snippet['thumbnails'][item]['width']:
                        res = snippet['thumbnails'][item]['width']
                        max_image = item
                channel_image=(snippet['thumbnails'][max_image]['url'])
                channel_title = snippet["title"]
                channel_subscriber_count = statistics["subscriberCount"]
                channel_video_count = statistics["videoCount"]
                channel_view_count  = statistics["viewCount"]
                channel_url=f"https://www.youtube.com/channel/{channel_id}"
                embed = discord.Embed(title="Thông Tin Kênh youtube.",
                description=f'[{channel_title}]({channel_url})', color=discord.Colour.random())
                #embed.add_field(name="Miêu Tả",value=re.sub('\..*','',channel_description),inline=False)
                embed.add_field(name="Lượt Đăng Kí",value=numerize.numerize(int(channel_subscriber_count)),inline=True)
                embed.add_field(name="Lượt Xem",value=numerize.numerize(int(channel_view_count)),inline=True)
                embed.add_field(name="Số Video Đã Đăng Tải",value=numerize.numerize(int(channel_video_count)),inline=True)
                embed.add_field(name="Ngày Tạo Kênh",value=channel_creation_date,inline=True)
                embed.add_field(name="Quốc gia",value=channel_country,inline=True)
                author = ctx.user
                embed.set_image(url=channel_image)
                avatar = author.avatar.url
                embed.set_footer(text=f'Người sử dụng lệnh: {str(author)}', icon_url=avatar)
                a=discord.ui.View()
                channell=discord.ui.Button(style=discord.ButtonStyle.link,url=channel_url,label=channel_title)
                a.add_item(channell)
                channel = self.bot.get_channel(id)
                await ctx.response.send_message(f"Đã đăng video lên kênh {channel.mention}")
                await channel.send(embed=embed,view=a)
        else:
            await ctx.response.send_message(embed=self.messem(ctx,"Bạn không có quyền thực hiện lênh này!"))
    @app_commands.command(name="postvideo")
    @app_commands.describe(video_url="Link Video Trên Youtube!")
    async def postvideo(self, ctx: discord.Interaction,*,video_url:str=None) -> None:
        """Hiển Thị Thông Tin Video"""
        rolelist=['Admin',"Youtuber"]
        if any(role.name in rolelist  for role  in ctx.user.roles):
            try:
                with open('data.json','r') as expp:
                    users = json.load(expp)
                id= users[str(ctx.guild.id)]
            except:
                return await ctx.response.send_message(embed=self.messem(ctx,"Bạn chưa đặt kênh đăng video để thực hiện lênh này!"))
            if video_url==None:
                return await ctx.response.send_message("url không được để trống!")
            if  video_url:
                youtube = ytb.youtube_authenticate()
                video_id = ytb.get_video_id_by_url(video_url)
                response = ytb.get_video_details(youtube, id=video_id)
                item=ytb.print_video_infos(youtube,response)
                link=video_url
                channel=item['linkchannel']
                image=item['imagevideo']
                thum=item['imagechannel']
                vieww=numerize.numerize(int(item['views']))
                day=item['Publish_time']
                you=item['Channel_name']
                dis=item['Description']
                ti=item['Title']
                time=item['Duration']
                time=self.parse_duration(time)
                author = ctx.user
                avatar = author.avatar.url
                embed = discord.Embed(title="Thông Tin Video", description=f'[{ti}]({link})', color=discord.Colour.random())
                embed.add_field(name="Kênh youtube",value=f'[{you}]({channel})',inline=False)
                #embed.add_field(name="Miêu Tả",value=re.sub('\..*','',dis),inline=False)
                embed.add_field(name="Ngày Xuất Bản",value=day,inline=True)
                embed.add_field(name="Thời Lượng",value=time,inline=True)
                embed.add_field(name="Lượt Xem",value=vieww,inline=True)
                embed.set_thumbnail(url=thum)
                embed.set_image(url=image)
                embed.set_footer(text=f'Người sử dụng lệnh: {str(author)}', icon_url=avatar)
                a=discord.ui.View()
                channell=discord.ui.Button(style=discord.ButtonStyle.link,url=channel,label=you)
                videol=discord.ui.Button(style=discord.ButtonStyle.link,url=link,label="VIDEO")
                a.add_item(channell)
                a.add_item(videol)
                channel = self.bot.get_channel(id)
                await ctx.response.send_message(f"Đã đăng video lên kênh {channel.mention}")
                await channel.send(embed=embed,view=a)
        else:
            await ctx.response.send_message(embed=self.messem(ctx,"Bạn không có quyền thực hiện lênh này!"))
    @app_commands.command(name="setpostchannel")
    @app_commands.describe(channel="Kênh Bạn Muốn Đặt Làm Nơi Đăng Video!")
    async def setpostchannel(self, ctx: discord.Interaction,channel:typing.Optional[discord.TextChannel]) -> None:
        rolelist=['Admin',"Youtuber"]
        if any(role.name in rolelist  for role  in ctx.user.roles):
            with open('data.json','r') as expp:
                users = json.load(expp)
            users[str(ctx.guild.id)]=channel.id
            with open('data.json','w') as expp:
                json.dump(users, expp,indent=4)
            await ctx.response.send_message(f"Đã đặt kênh {channel.mention} làm kênh đăng video!")
        else:
            await ctx.response.send_message(embed=self.messem(ctx,"Bạn không có quyền thực hiện lênh này!"))

async def setup(bot):
    await bot.add_cog(music(bot))