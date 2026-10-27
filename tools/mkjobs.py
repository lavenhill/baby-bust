import json
R={k:f"img/ref_{k}.webp" for k in ['afang','jiahao','yijun','zhihao','peishan','laoyan']}
C={'afang':'A-Fang (the mother in the reference)','jiahao':'Jiahao (the kindergarten owner in the reference)','yijun':'Yijun (the preschool teacher in the reference)','zhihao':'Zhihao (the office worker in the reference)','peishan':'Peishan (the office woman in the reference)','laoyan':'Lao Yan (the woman with glasses in the reference)'}
S={
'y2018':(('afang','A-Fang walking her happy 1-year-old son into a bright colorful affordable preschool, both beaming','A-Fang at a cramped kitchen table at night counting banknotes next to a tuition bill and calculator, her son asleep on the sofa'),
         ('jiahao','Jiahao proudly at the door of his cozy private kindergarten with two smiling teachers and waving toddlers','Jiahao standing alone at the doorway of an empty classroom with small chairs stacked and an old electric fan')),
'y2019a':(('jiahao','Jiahao hanging a shiny new sign over his kindergarten gate while parents and kids cheer','Jiahao at his office desk late at night with a stack of government forms and a fee-cap notice, rubbing his forehead'),
          ('yijun','Yijun joyfully leading a circle game with toddlers in a cheerful classroom','Yijun sitting alone in an empty classroom after school looking at a thin payslip, phone showing a message from her mother')),
'y2019b':((None,'a group of young parents cheering and hugging in front of a public kindergarten lottery board, kids jumping','a crowd of anxious parents staring at a public kindergarten lottery board in a school hallway'),
          ('afang','A-Fang and her son smiling at the colorful gate of a preschool','A-Fang holding a waitlist slip, turning away from a public kindergarten gate with her son, shoulders down')),
'y2021':(('afang','A-Fang and her son happily doing an online class together on a tablet at home, thumbs up','A-Fang exhausted at home juggling her work laptop and her son\'s online class, dishes piled, phone ringing'),
         ('zhihao','Zhihao as a smiling office hero giving a thumbs up among grateful coworkers','Zhihao alone in a dim office at night, two monitors, an untouched cold lunch box, two empty desks beside him')),
'y2022c':((None,'a young family with two small children joyfully carrying boxes into a bright rented apartment, holding a subsidy letter','a young family with two small children squeezed among moving boxes in a small old rental flat'),
          ('zhihao','Zhihao smiling in a bright cozy small studio apartment with a window','Zhihao late at night in a tiny windowless rented room, laptop open, a rent increase notice on the bed')),
'y2022d':((None,'a young mother at home happily playing with her toddler on a sunny living room floor','a young mother at home alone overwhelmed, toddler crying, laundry everywhere'),
          ('afang','A-Fang smiling confidently at her office desk wearing a staff ID badge','A-Fang at home placing her staff ID badge into a drawer next to a resignation letter, son tugging her sleeve')),
'y2024':(('afang','A-Fang happily picking up her son at a preschool at six in the evening, warm lights, teacher waving','A-Fang rushing out of an office building at dusk checking her watch, crowded street'),
         ('yijun','Yijun cheerfully reading a picture book to a few children in a warm evening classroom','Yijun at six in the evening still holding hands with three small children at the preschool gate, her water bottle empty, sky darkening')),
'y2025e':((None,'happy parents dropping kids off at a public kindergarten during summer vacation, teachers welcoming, sunshine','parents in summer heat hurrying to drop children at a kindergarten gate before work'),
          ('yijun','Yijun happily waving at a summer day-camp with kids in sun hats','Yijun in a quiet staff room holding a returned leave request form, an airplane ticket printout on the table')),
'y2025f':((None,'a newlywed couple joyfully receiving the keys to a new public housing apartment, confetti','a newlywed couple waiting with a number ticket at a housing office counter'),
          ('zhihao','Zhihao smiling holding up a shiny apartment key','Zhihao alone at the very end of a long queue at a housing office, holding a number ticket')),
'y2026':(('peishan','Peishan cheerfully leaving the office at noon with her bunny tote bag to go see her child, coworkers waving goodbye','Peishan bowing apologetically to her desk neighbor as she leaves the office at noon with her bunny tote bag'),
         ('laoyan','Lao Yan smiling at a tidy desk as a model efficient civil servant, thumbs up','Lao Yan alone at her desk late at night between two tall stacks of case files, a small photo frame and two rings on the desk')),
}
jobs=[]
for n,(U,D) in S.items():
    for half,(who,pp,rr) in (('U',U),('D',D)):
        for kind,txt in (('poster',pp),('real',rr)):
            j={"kind":kind,"out":f"img/{n}_{half}_{kind}.webp","size":"1536x1024","p":(txt.replace(C[who].split(' (')[0],C[who]) if who else txt)}
            if who: j["refs"]=[R[who]]
            jobs.append(j)
six=[R[k] for k in ['afang','jiahao','yijun','zhihao','peishan','laoyan']]
jobs+= [
 {"kind":"real","out":"img/open_back.webp","size":"1536x1024","refs":six,"p":"2018, warm hopeful afternoon light: six young friends (the six people in the references) seen from behind, standing in a row in front of a plain modern government office building, all raising their right hands high together, like a promise. Lao Yan with the camera strap is in the middle."},
 {"kind":"real","out":"img/reunion_front.webp","size":"1536x1024","refs":six,"p":"2026, same plain modern government office building, eight years later: the same six friends (the six people in the references, slightly older) standing in a row facing the camera for a class reunion photo, gentle smiles, faded evening light."},
]
for k,t in [('afang','A-Fang holding her newborn second baby, smiling softly'),('peishan','Peishan holding her newborn baby in a hospital room'),('jiahao','Jiahao holding his newborn baby, proud and tearful'),('yijun','Yijun holding her newborn baby at home')]:
    jobs.append({"kind":"real","out":f"img/baby_{k}.webp","size":"1024x1024","refs":[R[k]],"p":t.replace(C[k].split(' (')[0],C[k])+", warm soft colors, tender."})
json.dump(jobs,open('jobs.json','w'),ensure_ascii=False,indent=0);print(len(jobs))
