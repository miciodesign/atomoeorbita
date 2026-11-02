import subprocess
W,H=1080,1920; FPS=30; XF=0.4
scenes=[("a.png",0,1.98),("b.png",1.98,12.38),("c.png",12.38,22.0),("d.png",22.0,29.2),
        ("e.png",29.2,35.08),("f.png",35.08,39.64),("g.png",39.64,42.6)]
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
  "[0:v]ass=sub.ass[v];[1:a]atrim=start=1.0,asetpts=PTS-STARTPTS,apad=pad_dur=3[a]","-map","[v]","-map","[a]",
  "-t","42.6","-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","192k","-movflags","+faststart",
  "AtomoeOrbita-Short-02-Fissione.mp4"],check=True)
