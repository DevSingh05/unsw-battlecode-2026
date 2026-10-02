# unswbc 1.2.6 map changes and queen safety, 2026-10-02
Scripts: scratchpad nm/{crop,cut,pocket,crops2,fetch,fetch2,an,agg2,aggold}.py (sim2-based). Queen = the id in {0,1} whose map DRAGON team is T.
Server sides are randomly swapped (DRAGON team bits flipped in replays), so queen ids must be read from each replay's map.
Late server Schooltime replays (857166, 857187) lack 4 kelp edges at y=30 (EDGE 3726/3737/3765/3776) that maps/schooltime.map has; not near the queens.

## What changed (queen = first DRAGON line per team)
| map | change | queen now | protected? |
| Default | 4 kelp edges at the wrap corner: W+N of (0,0), W of (0,31), N of (31,0) | same L4 at (0,0)/(31,31) | No pocket. Only splits the two queens: they were 2 apart across the corner (head-on at r1), now 6. Head exits S (A) / N (B) only |
| Schooltime | 8 kelp edges per queen seal a 2x2 box (2..3,1..2) and (56..57,1..2) | same L4 | SEALED forever: 4 tiles, no exit. She can never leave. Max livable length 3 (own tail blocks before it moves); (3,1)/(56,1) spawns pearls (gap 20-200) |
| Trophy | queens moved (4,2)->(4,9) and (20,2)->(20,9), into the trophy cup; cup top sealed (new N kelp of (5,7) etc.), 125 tiles set to no-pearl | L3 in a 39-tile cup | Pocket with ONE 2-tile entrance at the stem ((5,14),(6,13) / mirror), 25 steps from the enemy queen (was 9). Cup is pearl-free |
| Slithery | DRAGON order swapped: queen is now the L25 spiral (3,22)/(59,4), not the L7 in the dead-end; 8 pocket-mouth tiles set to no-pearl | L25, head at spiral centre, all 4 neighbours own body | Not a pocket (map-connected), but she must split at r0 to move |
| Dilemma | order swapped: queen is the L3 at (3,6)/(28,9), not the L11 in the dead-end corridor | L3, open area | No. The old forced r5-7 death is gone |
| Autarky | order swapped: queen is the L3 at (7,1)/(46,16), not the L14 in the dead-end; 16 pearl tiles changed | L3, open area | No. The old forced r10 death is gone |

### ASCII crops (team A queen; Q head, q body, E enemy queen, o/x other dragons; | and __ kelp; tile chars = pearl rate, blank = no pearls)
```
default OLD: team A queen head (0, 0) L4
               ______
28  . .|. . . . . . .
29  . .|. . . . . . .
   ____        ______
30  . . . . . . . . .
31  E E E E . . . . .
 0  . . . . Q q q q o
 1  . . . . . . . . .
   ____        ______
 2  . . . . . .|. . .
 3  . . . . . .|. . .
   ____              
 4  . . . . . .|. . .
default NEW: team A queen head (0, 0) L4
               ______
28  . .|. . . . . . .
29  . .|. . . . . . .
   ____        ______
30  . . . . . . . . .
31  E E E E|. . . . .
         ____        
 0  . . . .|Q q q q o
 1  . . . . . . . . .
   ____        ______
 2  . . . . . .|. . .
 3  . . . . . .|. . .
   ____              
 4  . . . . . .|. . .
schooltime OLD: team A queen head (3, 2) L4
38  . . . . . . . . .
39  . . . . . . . . .
   __________________
 0                   
 1        q q        
 2  o o   q Q        
 3                   
               ____  
 4             |   | 
 5             |   | 
               ____  
 6          o        
schooltime NEW: team A queen head (3, 2) L4
38  . . . . . . . . .
39  . . . . . . . . .
   __________________
 0                   
         ____        
 1       |q q|       
 2  o o  |q Q|       
         ____        
 3                   
               ____  
 4             |   | 
 5             |   | 
               ____  
 6          o        
trophy OLD: team A queen head (4, 2) L3
22  x . . . . o o o . . . . . . .
23  . . . . . . . . . . . . . . .
24  . . . . . . . . . . . . . . .
 0  . . . . . . . . . . . . . . .
 1  . . . . . . . . . . . . . . .
 2  E . . . . q q Q . . . . . . .
 3  . . . . . . . . . . . . . . .
                       __________
 4  . . . . . . . . . .|. . . . .
                     __          
 5  . . . . . . . . .|. . . . . .
   __        ____                
 6  .|. . . .|. .|. .|. . . . . .
     __    __    __              
 7  . .|. .|. . . . .|. . . . . .
 8  . .|. .|. . . . .|. . . . o o
 9  . .|. .|. . . . .|. . . . . o
10  . .|. .|. . . . .|. . . . . o
                     __          
11  . .|. .|. . . . . .|. . . . .
trophy NEW: team A queen head (4, 9) L3
                       __________
 4  . . . . . . . . . .|. . . . .
                     __          
 5  . . . . . . . . .|. . . . . .
   __        ____                
 6   |. . . .|   |. .|. . . . . .
     __    __    ____            
 7     |. .|        .|. . . . . .
 8     |. .|        .|. . . . o o
 9  E  |. .|  q q Q  |. . . . . o
10     |. .|         |. . . . . o
                     __          
11     |. .|          .|. . . . .
     __    __                    
12   |  . .  |        .|. . . . .
   __        __                  
13 |. . . . . .|      .|. . . . .
               __                
14  . . . . . .  |     |. . . . .
                 __    __        
15  . . . . . . . . .    |. . . .
                       __        
16  . . . . . . . . . . . . . . .
17  . . . . . . . . . . . . . . .
18  . . . . . . . . . . . . .|. .
slithery_fight OLD: team A queen head (8, 10) L7
 6                   
 7                   
           __________
 8         |#|       
 9         |#|       
10         |Q|       
11          q        
   ____              
12 |+ +|    q        
13 |+ +|    q        
   ____              
14          q        
slithery_fight NEW: team A queen head (3, 22) L25
18   |               
19   |               
20   |  q q q q q    
21  .|. q q q q q    
22  .|. q q Q q q    
23  .|. q q q q q    
24  .|. q q q q q    
25  .|. . . . . . .  
26  .|. . . . . . .  
dilemma OLD: team A queen head (14, 2) L11
   __                
14         |#|. .|#| 
15         |#|. .|#| 
   __________________
 0         |#|. .|#| 
 1         |#|. .|#| 
 2         |Q|. .|#| 
   __                
 3   |    .|q|. .|E|.
 4   |  . . q . . E .
 5   |  . . q . . E .
   __                
 6      . . q . . E .
dilemma NEW: team A queen head (3, 6) L3
 2   |               
 3   |               
 4   |               
 5   |               
 6   |  q q Q        
 7   |               
 8   |               
 9   |               
10   |               
autarky OLD: team A queen head (18, 2) L14
16         |#|       
             __      
17         |# +|o o o
   __________________
 0         |# +|    o
             __      
 1         |#|+     o
 2         |Q|      o
   __                
 3   |      q        
 4   |      q        
 5   |      q        
   __                
 6          q   .    
autarky NEW: team A queen head (7, 1) L3
   ______            
15          o o o    
16                   
17                   
   __________________
 0                   
 1          Q q q    
 2                   
   ______            
 3 |     |           
 4 |     |           
 5 |     |           
```

## Server, new maps (all battles >= 04:15 UTC 10-02; ours = 29 battles/123 ranked-map games, others = 300 sampled games, 30/map)
Classes at game end: elim; Q1 = r500, one queen alive (alive queen won 87/87); QQ> = both alive, longer queen won (13/13); QQ= = both alive equal (longest won 16/16); long = both dead.
```
ALL games (ours+others), per queen:
map               n   Qalive_end  Qalive@r500(of r500 games)  medQdeath  elim Q1 QQ> QQ= long | ours: n win  usQend themQend usQmed themQmed  decided(elim/Q1/QQ>/QQ=/long) W by class
Default            39    19%        6/28 = 21%           165.5    25   4   1   0   9 |  9  9   7   1    500    61  7/1/1/0/0  W 7/1/1/0/0
Schooltime         42    68%       53/76 = 70%           500.0     4  17   2  16   3 | 12  9  10   7  500.0 500.0  0/5/1/5/1  W 0/4/1/3/1
Trophy             43    26%        0/4  =  0%           105.5    41   0   0   0   2 | 13 12   9   1    500   116  13/0/0/0/0  W 12/0/0/0/0
Slithery Fight     47    13%       10/90 = 11%           132.5     2  10   0   0  35 | 17  8   4   2    222   157  0/6/0/0/11  W 0/4/0/0/4
Prisoners Dilemma  44    26%       12/24 = 50%            96.5    32   8   2   0   2 | 14  7   7   5  496.0 227.0  8/3/2/0/1  W 4/1/1/0/1
Autarky            40    21%        6/34 = 18%           183.0    23   6   0   0  11 | 10  6   2   1  188.0  91.0  5/3/0/0/2  W 4/2/0/0/0
Portals            42     5%        4/80 =  5%           104.0     2   4   0   0  36 | 12  8   0   0  140.5  91.0  1/0/0/0/11  W 1/0/0/0/7
Devil              41    16%        2/14 = 14%            88.5    34   2   0   0   5 | 11  6   0   2    102    97  11/0/0/0/0  W 6/0/0/0/0
Queen Of Spades    43    17%        4/30 = 13%           158.0    28   4   0   0  11 | 13 10   6   0    212   105  12/1/0/0/0  W 9/1/0/0/0
Trauma             42    49%       40/80 = 50%           491.0     2  26   7   0   7 | 12 10  12   4  500.0 126.5  0/8/4/0/0  W 0/8/2/0/0
```
Old maps (pre-04:12, our A/B vs top-10: v35d/v36/v37c/v37d/v37e srv folders, 50/map; v37d_other 10/map):
```
Devil             n10 win5 usQend1 themQend1 medQdeath(all)77.0 us107.5 them35.0 cls 9/1/0/0/0
Default           n10 win7 usQend3 themQend0 medQdeath(all)171.0 us193.5 them66.5 cls 7/0/0/0/3
Autarky           n10 win6 usQend0 themQend0 medQdeath(all)10.0 us10.0 them8.0 cls 6/0/0/0/4
Trauma            n10 win9 usQend9 themQend1 medQdeath(all)495.0 us500.0 them166.5 cls 1/7/1/0/1
Queen Of Spades   n10 win7 usQend7 themQend1 medQdeath(all)234.0 us500.0 them100.0 cls 8/1/0/0/1
Prisoners Dilemma n50 win43 usQend0 themQend0 medQdeath(all)7.0 us7.0 them5.0 cls 47/0/0/0/3
Trophy            n50 win21 usQend8 themQend10 medQdeath(all)95.0 us112.0 them85.5 cls 50/0/0/0/0
Slithery Fight    n50 win17 usQend0 themQend0 medQdeath(all)5.0 us5.0 them5.0 cls 0/0/0/0/50
Schooltime        n50 win17 usQend2 themQend13 medQdeath(all)143.0 us158.0 them142.5 cls 2/15/0/0/33
Portals           n50 win17 usQend2 themQend4 medQdeath(all)95.5 us154.0 them53.0 cls 0/6/0/0/44
```
Queen median death round, all queens, old -> new: Dilemma 7 -> 97, Slithery 5 -> 133, Autarky 10 -> 183, Schooltime 143 -> 500 (alive), Trophy 95 -> 106, Default 171 -> 166.
Our queen alive at game end, old -> new: Dilemma 0/50 -> 7/14, Slithery 0/50 -> 4/17, Schooltime 2/50 -> 10/12, Trophy 8/50 -> 9/13 (elim wins), Default 3/10 -> 7/9, Autarky 0/10 -> 2/10.
Our ranked-map record on new maps: 85/123 (.69, ladder opponents, not the top-10 set). Losses 38: elim 14, long 13, queen-decided 11
(Q1 with our queen dead: 6 = Schooltime 852620, Slithery 854409/856320, Dilemma 854961/856317, Autarky 856311; we had the longer longest in 5;
QQ> 3 = Dilemma 852619, Trauma 852782 / 854966 (Trauma: longest 39 vs 5, lost on queen length); QQ= 2 = Schooltime 852770, 857187).

## Schooltime box: our queen bug
Queen spawns in the sealed box, is L5 at r0 and every bot that survives splits k=2 at r0 (child dies, queen eats its pearl -> L3 and cycles).
Our deaths: 852780 r0 (MOVE W into own tail, v38 before v38m was live), 852620 r156 and 856025 r152: at L3 she ate the box pearl at (56,1) -> L4, next turn MOVE E into herself.
v38m main.cpp:4988 trapped split needs tailHasExit(myLen-2), false in a full box, so no split. Locally the same bug hits both bots (below).

## Local, v38m vs v35, seeds 7001-7005, both seats (10 games/map)
| map | v38m wins | v38m queen alive end | v35 queen alive end | v38m queen deaths |
| Schooltime | 5 | 6/10 | 7/10 | 4x HitSelf at L4 in the box (r132-464) |
| Trophy | 3 | 2/10 | 4/10 | 7 head-on (r57-161), 1 HitSelf |
| Default | 4 | 4/10 | 0/10 (med r42) | 6 head-on (med r379) |

## Conclusions
- Queen safety now decides games on Schooltime (19/42 games Q1/QQ>, 16 more QQ= ties; queens are immortal unless the bot errs), Dilemma (10/44), Slithery (10/47 Q1),
  Autarky (6/40) and Trauma (33/42, unchanged map). Trophy (41/43 elim), Devil, QoS and Default stay elimination maps.
- Fix first (new, not parked): QBOX. If the queen's reachable region R is sealed and L >= R (no legal move), SPLIT 2 without tailHasExit; never stay at L4 in the
  Schooltime box; be at L3 (not L2) near r495 for the QQ tiebreak. Costs us 1 server loss so far (852620), 4/10 local queen deaths. Opponents lose their box queen at r0 in 9/42 games.
- QGUARD (v37e): re-test on Dilemma/Autarky/Slithery (open spawns now; our queen deaths there are HitSelf/HitOtherBody at L2-3 after splits). QG_MIN=5 must be off when
  the queen's region is < 6 tiles (fatal in the Schooltime box). The floor also targets the 3 QQ> losses (Trauma 39 v 5 longest, lost on queen length).
- QSTATE (v37a): re-test on Schooltime/Dilemma/Trauma. Must treat a boxed enemy queen as unreachable (no hunt), and turtle when ours is alive and theirs is dead.
- QSPLIT_ROOM (v39a): re-test on Slithery (spiral queen, k=2 peel x4 at r0-3, then HitSelf at L2-3 r80-450). QALLY_KEEP (v38): Dilemma/Autarky.
- New behaviour: Trophy cup queen: stay in the pearl-free cup (one 2-tile entrance at the stem), maybe with an ally plugging the stem. A live hidden queen denies
  elimination, and at r500 a lone queen wins (87/87). Slithery: keep the queen big after the r0 spiral escape (L19 at r3) and stop splitting her below 5.
