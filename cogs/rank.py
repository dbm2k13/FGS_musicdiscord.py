import asyncio,discord,math,random,json,typing
from discord.ext import commands
from fakemodule import pic


async def update_data(users, user,server):
    if not str(server.id) in users:
        users[str(server.id)] = {}
        if not str(user.id) in users[str(server.id)]:
            users[str(server.id)][str(user.id)] = {}
            users[str(server.id)][str(user.id)]['exp'] = 0
            users[str(server.id)][str(user.id)]['level'] = 1
            users[str(server.id)][str(user.id)]['custom'] ={}
            users[str(server.id)][str(user.id)]['custom']['back']='https://cdn.discordapp.com/attachments/1010412857541799997/1065528346068402186/dfdf.png'
            users[str(server.id)][str(user.id)]['rank'] = 0
    elif not str(user.id) in users[str(server.id)]:
            users[str(server.id)][str(user.id)] = {}
            users[str(server.id)][str(user.id)]['exp'] = 0
            users[str(server.id)][str(user.id)]['level'] = 1
            users[str(server.id)][str(user.id)]['custom'] ={}
            users[str(server.id)][str(user.id)]['custom']['back']='https://cdn.discordapp.com/attachments/1010412857541799997/1065528346068402186/dfdf.png'
            users[str(server.id)][str(user.id)]['rank'] = 0
async def updaterank(users,id):
    leaderboard = {}
    total=[]
    x=len(users[str(id)])      
    for user in list(users[str(id)]):
        name = int(user)
        total_amt = users[str(id)][str(user)]['exp']
        leaderboard[total_amt] = name
        total.append(total_amt)
        total = sorted(total,reverse=True)
    index = 1
    for amt in total:
        sid = leaderboard[amt]
        users[str(id)][str(sid)]['rank'] = index
        if index == x:
            break
        else:
            index += 1


async def add_experience(users, user):
  users[str(user.guild.id)][str(user.author.id)]['exp'] += random.randint(1,3)

async def level_up(users, user):
    exp = users[str(user.guild.id)][str(user.id)]['exp']
    users[str(user.guild.id)][str(user.id)]['level'] =exp//100
class rankup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener("on_message")
    async def on_message(self,message):
        if not message.author.bot:
            with open('jsonfile/rank.json','r') as expp:
                users = json.load(expp)
            await update_data(users, message.author,message.guild)
            await add_experience(users, message)
            await level_up(users, message.author)
            await updaterank(users,message.guild.id)
            with open('jsonfile/rank.json','w') as expp:
                json.dump(users, expp,indent=4)
    @commands.command(name="level")
    async def level(self, ctx: discord.Interaction, member:  typing.Optional[discord.Member]=None):
        with open('jsonfile/rank.json', 'r') as f:
            users = json.load(f)
        server=ctx.guild.id
        if member == None:
            id = ctx.user.id
            us=ctx.user
        else:
            id = member.id
            us=member
        avatar=us.display_avatar.url
        name=us.name
        lvl=users[str(server)][str(id)]['level']
        exp=users[str(server)][str(id)]['exp']
        rank=users[str(server)][str(id)]['rank']
        maxelv=int((lvl*10)+90)
        back=users[str(server)][str(id)]['custom']['back']
        image = pic.pic(name,avatar,rank,lvl,exp,maxelv,back)
        await ctx.response.send_message(file=discord.File(image, filename="rank.png"))

    @commands.command()
    async def Top5rank(self, ctx: discord.Interaction):
        with open('jsonfile/rank.json', 'r') as f:
            users = json.load(f)
        x=5
        leaderboard = {}
        total=[]
        
        for user in list(users[str(ctx.guild.id)]):
            name = int(user)
            total_amt = users[str(ctx.guild.id)][str(user)]['exp']
            leaderboard[total_amt] = name
            total.append(total_amt)

        total = sorted(total,reverse=True)
        
        em = discord.Embed(
            title = f'Top {x} Người có level cao nhất trong {ctx.guild.name}',
            description = ''
        ,color=discord.Colour.random())
        
        index = 1
        for amt in total:
            id = leaderboard[amt]
            lvl=users[str(ctx.guild.id)][str(id)]['level']
            maxelv=int((lvl*10)+90)
            namee = await self.client.fetch_user(int(id))           
            member = namee.name

            em.add_field(name = f'{index}: {member}', value = f'LEVEL: ``{lvl}``\nEXP: ``{amt}``/``{maxelv}``', inline=False)
            
            
            if index == x:
                break
            else:
                index += 1
            
        await ctx.response.send_message(embed = em)



async def setup(bot):
    await bot.add_cog(rankup(bot))

