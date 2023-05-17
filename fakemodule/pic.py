from PIL import Image,ImageDraw,ImageFont
import requests
from io import BytesIO
from numerize import numerize
def pic(username,av,rank,level,current_exp,max_exp,url):

    response = requests.get(url)
    back = Image.open(BytesIO(response.content))
    response = requests.get(av)
    av = Image.open(BytesIO(response.content))

    back=back.resize((1000, 333))
    cut = Image.new("RGBA", (950, 333-50) , (0, 0, 0, 200))
    back.paste(cut, (25, 25) ,cut)


    av = av.resize((260, 260))
    mask = Image.open("./avpic/curveborder.png").resize((260, 260))
    new = Image.new("RGBA", av.size, (0, 0, 0))
    try:
        new.paste(av, mask=av.convert("RGBA").split()[3])
    except:
        new.paste(av, (0,0))

    back.paste(new, (53, 73//2), mask.convert("L"))
    myFont = ImageFont.truetype("./avpic/levelfont.otf",50)
    draw = ImageDraw.Draw(back)

    if rank is not None:
        combined = "LEVEL: " + str(level) + "       " + "RANK: " + str(rank)
    else:
        combined = "LEVEL: " + level
    w = draw.textlength(combined, font=myFont)
    draw.text((950-w,40), combined,font=myFont, fill="white",stroke_width=1,stroke_fill=(0, 0, 0))

    draw.text((330,130), username,font=myFont, fill="white",stroke_width=1,stroke_fill=(0, 0, 0))
    exp = f"{numerize.numerize(int(current_exp))}/{numerize.numerize(int(max_exp))}"
    w = draw.textlength(exp, font=myFont)
    draw.text((950-w,130), exp,font=myFont, fill="white",stroke_width=1,stroke_fill=(0, 0, 0))

    bar_exp = (current_exp/max_exp)*619
    if bar_exp <= 50:
            bar_exp = 50  

    im = Image.new("RGBA", (620, 51))
    draw = ImageDraw.Draw(im, "RGBA")
    draw.rounded_rectangle((0, 0, 619, 50), 30, fill=(255,255,255,225))
    draw.rounded_rectangle((0, 0, bar_exp, 50), 30, fill=(0,193,192,255))
    back.paste(im, (330, 235))

    image = BytesIO()
    back.save(image, 'PNG')
    image.seek(0)
    return image

