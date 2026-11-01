import subprocess, json
from PIL import Image, ImageFilter, ImageDraw, ImageFont
W,H=1080,1920
FONT="/usr/share/fonts/opentype/inter/Inter-Regular.otf"
import glob
fonts=glob.glob("/usr/share/fonts/opentype/inter/Inter-*.otf")
def photo_frame(src,out,credit):
    im=Image.open(src).convert("RGB")
    bg=im.resize((int(im.width*H/im.height),H)).crop(((int(im.width*H/im.height)-W)//2,0,(int(im.width*H/im.height)-W)//2+W,H))
    bg=bg.filter(ImageFilter.GaussianBlur(40))
    bg=Image.blend(bg,Image.new("RGB",(W,H),(18,20,23)),0.55)
    fg=im.resize((W,int(im.height*W/im.width)))
    y=(H-fg.height)//2-180
    bg.paste(fg,(0,y))
    d=ImageDraw.Draw(bg)
    f=ImageFont.truetype(FONT,26)
    d.text((90,y+fg.height+14),credit,font=f,fill=(190,196,202))
    bg.save(out)
photo_frame("foto-A-akademik-lomonosov.jpg","f-A.png","Foto: Elena Dider, CC BY-SA 4.0, Wikimedia Commons")
photo_frame("foto-C-linglong.jpg","f-C.png","Foto: China News Service, CC BY 4.0, Wikimedia Commons")
photo_frame("foto-B-darlington.jpg","f-B.png","Foto: Robert T Bell, CC BY 2.0, Wikimedia Commons")
# scenes (file, start, end)
scenes=[("01-titolo-SMR.png",0,5.6),("f-A.png",5.6,10.45),("02-confronto-potenza.png",10.45,16.5),
        ("f-C.png",16.5,24.45),("f-B.png",24.45,32.25),("03-italia-2033-2035.png",32.25,36.8),("04-chiusura-logo.png",36.8,42.6)]
FPS=30; XF=0.4
parts=[]
for i,(f,a,b) in enumerate(scenes):
    dur=b-a+(XF if i<len(scenes)-1 else 0)
    n=int(round(dur*FPS))
    out=f"clip{i}.mp4"
    z="min(1+0.0009*on,1.08)" if f.startswith("f-") else "min(1+0.0004*on,1.03)"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",f,"-vf",
      f"scale=2160:3840,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p",
      "-frames:v",str(n),"-c:v","libx264","-preset","veryfast","-crf","18",out],check=True)
    parts.append((out,dur))
# xfade chain
cmd=["ffmpeg","-y","-loglevel","error"]
for p,_ in parts: cmd+=["-i",p]
flt=[];prev="[0:v]";off=0
for i in range(1,len(parts)):
    off+=parts[i-1][1]-XF
    flt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); prev=f"[v{i}]"
cmd+=["-filter_complex",";".join(flt),"-map",prev,"-c:v","libx264","-preset","veryfast","-crf","18","video.mp4"]
subprocess.run(cmd,check=True)
