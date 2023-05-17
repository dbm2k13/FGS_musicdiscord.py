
from discord.ext import commands
from discord import app_commands
import discord,json
class rule(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.rulee={
    1: "1. Không toxic, bắt nạt người khác.",
    2: "2. Không spam, làm phiền người khác.",
    3: "3. Không NSFW, nội dung phản cảm, bạo lực.",
    4: "4. Sử dụng các kênh, lệnh đúng cách.",
    5: "5. Không tương tác với người người phá luật, thay vào đó hãy báo cáo họ.",
    6: "6. Không nói về các vấn đề chính trị, tôn giáo, phân biệt chủng tộc, phân biệt giới tính.",
    7: "7. Không mention(đề cập) các vai trò một cách bừa bãi.",
    8: "8. Không quảng cáo, spam link nếu chưa có sự cho phép của admin"
}
    @commands.command()
    async def senthis(self,ctx):
        em= discord.Embed(title="V7.0 Phiên bản 144",description="""- Đã sửa lỗi nút môi trường "bất kỳ (Any)" trông phần sửa bản đồ không bật
- Đã khắc phục sự cố liên quan đến quy tắc thử nghiệm (chế độ thử nghiệm ) được bật trên một số server nhất định
- Đã sửa lỗi lag do máy phân loại (sorter) cập nhật bản đồ nhỏ (minimap) rất nhanh
- Đã sửa lỗi các cơ sở được tạo bởi Serpulo đôi khi có các dây điện không được kết nối
- Đã sửa lỗi các hành tinh/khu vực/hiệu ứng trạng thái JSON không có tiền tố tên mod - điều này có thể làm hỏng các bản dịch 
- Đã sửa lỗi chỉ số tiêu thụ chất lỏng không hợp lệ trên các máy khoan plasma
- Nhân đôi kích thước tối đa của bản thiết kế 
- Các khối canvas hiện hiển thị bản xem trước hình ảnh của chúng trong danh sách bản thiết kế
- Các bản đồ và bản thiết kế mới được tạo hiện sử dụng tên được cung cấp làm tên tệp thay vì các số ngẫu nhiên (Giới hạn ở các ký tự chữ và số)
- Đã thêm hình chữ nhật camera vào chế độ xem bản đồ, nhấp chuột phải để di chuyển camera [Chỉ cho máy tính]
- Đã thêm các mũi tên chỉ thiệt hại của công trình vào bản đồ nhỏ
- Đã thêm hướng dẫn tìm đường logic(pathfind) - hỗ trợ tọa độ tùy ý(Yeah cuối cùng thì cũng có)
- Đã thêm quy tắc hệ số máu của lính
- Đã thêm quy tắc bản đồ 'kết thúc sau đợt' (Được đóng góp bởi @JniTrRny)
- Đã thêm thanh tìm kiếm cho giao diện người dùng wave (Được đóng góp bởi @JniTrRny)
- Đã thêm các sprite khí và lỏng Erekir mới (Đóng góp bởi @stacktrace-error)
- Đã thêm chức năng để đặt lớp phủ/tầng trong các bản mod (hoặc máy chủ có quy tắc RevealBlocks đã chỉnh sửa)
- Đã thêm các vùng pít-tông vào các khối không có chúng (Đóng góp bởi @MEEPofFaith)
- Đã thêm thanh tìm kiếm vào menu trò chơi tùy chỉnh
- Đã thêm nút 'xây dựng lại khu vực' cho thiết bị di động - lưu ý rằng kích thước sơ đồ mod V2.7.54 phá vỡ chức năng này - hãy tắt hoặc cập nhật nó để sử dụng tính năng này đúng cách!
- Cải thiện giao diện người dùng danh sách máy chủ""", color=discord.Colour.orange())
        await ctx.send(embed=em)
    @app_commands.command()
    @app_commands.describe(number='Số Thứ Tự Luật')
    async def rule(self, ctx: discord.Interaction,number:int=0):
        """Hiển Thị Luật Lệ"""
        em= discord.Embed(title="Luật Lệ",description="", color=discord.Colour.random())
        if number !=0:
            em.add_field(name=self.rulee[number],value="",inline=False)
        if number==0:
            for i in self.rulee:
                em.add_field(name=self.rulee[i],value="",inline=False)
        em.add_field(name="Các hành vi phá hoại, không tuân thủ luật tùy mức độ thì sẽ bị xử phạt chính đáng.",value="",inline=False)
        em.set_footer(text="-  -  -  Dội NGũ ADMIN XIN CHÂN THÀNH CẢM ƠN  -  -  -")
        em.set_thumbnail(url=ctx.guild.icon)
        em.set_author(icon_url=ctx.user.avatar.url,name=f"{ctx.user.name} | {ctx.guild.name}")
        await ctx.response.send_message(embed=em)

async def setup(bot):
    await bot.add_cog(rule(bot))
