import subprocess,sys
W,H,FPS,XF=1080,1920,30,0.4
HEAD=open('../fis/sub.ass').read().split('[Events]')[0]
def ts(t): return f"0:{int(t//60):02d}:{t%60:05.2f}"
def make(name,audio,scenes,subs,end_sub,out):
    T=scenes[-1][2]
    ev="[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    for i,(s,t) in enumerate(subs):
        e=(subs[i+1][0]-0.05) if i<len(subs)-1 else end_sub
        ev+=f"Dialogue: 0,{ts(s)},{ts(e)},S,,0,0,0,,{t}\n"
    open(f'{name}.ass','w').write(HEAD+ev)
    parts=[]
    for i,(f,a,b) in enumerate(scenes):
        dur=b-a+(XF if i<len(scenes)-1 else 0); n=int(round(dur*FPS)); c=f"{name}_clip{i}.mp4"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",f,"-vf",
          f"scale=2160:3840,zoompan=z='min(1+0.0004*on,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p",
          "-frames:v",str(n),"-c:v","libx264","-preset","veryfast","-crf","18",c],check=True); parts.append((c,dur))
    cmd=["ffmpeg","-y","-loglevel","error"]
    for p,_ in parts: cmd+=["-i",p]
    flt=[];prev="[0:v]";off=0
    for i in range(1,len(parts)):
        off+=parts[i-1][1]-XF; flt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); prev=f"[v{i}]"
    cmd+=["-filter_complex",";".join(flt),"-map",prev,"-c:v","libx264","-preset","veryfast","-crf","18",f"{name}_video.mp4"]
    subprocess.run(cmd,check=True)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{name}_video.mp4","-i",audio,"-filter_complex",
      f"[0:v]ass={name}.ass[v];[1:a]apad=pad_dur=3[a]","-map","[v]","-map","[a]","-t",str(T),
      "-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","192k","-movflags","+faststart",out],check=True)

make("u","u.mp3",[("u1.png",0,4.7),("u2.png",4.7,13.3),("u3.png",13.3,18.1),("u4.png",18.1,26.2),("u3.png",26.2,35.0),("u5.png",35.0,40.5),("u6.png",40.5,47.5),("logo.png",47.5,51.5)],
[(0.0,"Uranio arricchito.\\NSembra una cosa da film."),(3.40,"È più semplice."),(4.70,"L'uranio che si estrae dalle miniere\\Ncontiene pochissimo uranio-235,"),(9.42,"quello che si spezza facilmente:\\Nlo 0,7 per cento."),(13.26,"Per far funzionare una centrale\\Nne serve di più,"),(16.18,"tra il 3 e il 5 per cento."),(18.12,"Arricchire vuol dire proprio questo:"),(20.72,"aumentare quella percentuale,"),(22.58,"facendo girare il gas di uranio\\Nin migliaia di centrifughe."),(26.18,"Le armi richiedono livelli molto più alti,\\Noltre il 90 per cento."),(30.34,"Per questo si controlla con attenzione\\Nchi arricchisce e quanto."),(35.02,"I grandi impianti sono pochi:"),(36.84,"in Russia, in Europa,\\Nin Cina e negli Stati Uniti."),(40.52,"E alcuni reattori di nuova generazione\\Nchiedono uranio fino al 20 per cento,"),(44.8,"che finora vendeva quasi solo la Russia."),(47.5,"Un problema strategico per l'Europa.")],49.6,"AtomoeOrbita-Short-04-Uranio-arricchito.mp4")

make("s","s.mp3",[("s1.png",0,6.3),("s2.png",6.3,13.5),("s3.png",13.5,27.3),("s4.png",27.3,35.5),("s5.png",35.5,39.1),("s6.png",39.1,43.3),("logo.png",43.3,49.6)],
[(0.0,"Scorie nucleari."),(1.5,"In Italia ce ne sono già,"),(3.12,"anche se le centrali sono chiuse\\Nda quasi quarant'anni."),(6.32,"Sono quasi 34.000 metri cubi."),(9.12,"Per avere un'idea: riempirebbero\\Npiù o meno 13 piscine olimpiche."),(13.52,"Ma il 99 per cento è\\Na bassa o bassissima attività:"),(17.54,"tute, guanti, filtri,\\Nmetalli delle vecchie centrali"),(21.02,"e rifiuti di ospedali e industria."),(23.48,"La parte pericolosa, ad alta attività,\\Nè piccola in volume."),(27.3,"Una parte è all'estero:"),(28.96,"il vecchio combustibile, mandato a trattare\\Nin Francia e nel Regno Unito."),(33.04,"Per contratto, dovrà tornare in Italia."),(35.52,"Oggi tutto è sparso\\Nin decine di depositi temporanei."),(39.08,"Il Deposito nazionale, che dovrebbe\\Nraccoglierli, non ha ancora un sito."),(43.28,"Dove sono, e dove andranno:\\Nlo spieghiamo su Atomo e Orbita.")],47.5,"AtomoeOrbita-Short-05-Scorie-nucleari.mp4")

make("d","d.mp3",[("d1.png",0,5.6),("d2.png",5.6,11.2),("d3.png",11.2,21.3),("d4.png",21.3,27.5),("d5.png",27.5,38.8),("d6.png",38.8,48.8),("logo.png",48.8,54.2)],
[(0.0,"Deposito geologico."),(1.9,"Dove mettere le scorie più pericolose,\\Nper sempre."),(5.62,"La risposta della scienza è: sotto terra,"),(8.42,"in una roccia stabile da milioni di anni."),(11.18,"La Finlandia lo ha fatto davvero."),(13.26,"Si chiama Onkalo, che in finlandese\\Nvuol dire \"cavità\"."),(16.9,"È scavato nel granito\\Na circa 450 metri di profondità."),(21.28,"Il combustibile usato viene chiuso\\Nin contenitori di rame,"),(24.34,"circondati da argilla,\\Ne sigillato nelle gallerie."),(27.54,"Il 22 ottobre 2026 il governo finlandese\\Ngli ha dato la licenza di esercizio:"),(33.72,"è il primo al mondo."),(35.36,"Il primo contenitore scenderà\\Ndopo l'ultima ispezione."),(38.84,"Per arrivarci ci sono voluti\\Npiù di quarant'anni:"),(41.8,"la ricerca del sito è cominciata nel 1983."),(45.48,"Senza mai cambiare strada\\Ntra un governo e l'altro."),(48.78,"Forse la lezione più importante,\\Nanche per l'Italia.")],52.1,"AtomoeOrbita-Short-06-Deposito-geologico.mp4")
