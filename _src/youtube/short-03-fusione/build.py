import subprocess
W,H=1080,1920; FPS=30; XF=0.4
scenes=[("a.png",0,3.0),("b.png",3.0,13.6),("c.png",13.6,15.7),("d.png",15.7,23.9),("e.png",23.9,30.5),("f.png",30.5,40.7),("g.png",40.7,47.6)]
parts=[]
for i,(f,a,b) in enumerate(scenes):
    dur=b-a+(XF if i<len(scenes)-1 else 0); n=int(round(dur*FPS)); out=f"clip{i}.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",f,"-vf",
      f"scale=2160:3840,zoompan=z='min(1+0.0004*on,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p",
      "-frames:v",str(n),"-c:v","libx264","-preset","veryfast","-crf","18",out],check=True)
    parts.append((out,dur))
cmd=["ffmpeg","-y","-loglevel","error"]
for p,_ in parts: cmd+=["-i",p]
flt=[];prev="[0:v]";off=0
for i in range(1,len(parts)):
    off+=parts[i-1][1]-XF
    flt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); prev=f"[v{i}]"
cmd+=["-filter_complex",";".join(flt),"-map",prev,"-c:v","libx264","-preset","veryfast","-crf","18","video.mp4"]
subprocess.run(cmd,check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","video.mp4","-i","voce.mp3","-filter_complex",
  "[0:v]ass=sub.ass[v];[1:a]apad=pad_dur=3[a]","-map","[v]","-map","[a]",
  "-t","47.6","-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","192k","-movflags","+faststart",
  "AtomoeOrbita-Short-03-Fusione.mp4"],check=True)
