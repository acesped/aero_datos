#!/usr/bin/env python3
"""DataViral: 500 propuestas, Reels/feed/Stories; edición de retención y fondo monocromático.

Las referencias son opcionales; la ausencia de fuentes no impide publicar.
Los datos generados por IA no están verificados independientemente.
Para contenido sensible, mantener revisión humana antes de publicar.
Python 3.11+. Dependencias en requirements.txt; ffmpeg instalado por workflow.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
import wave
import zlib
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

CATALOG_B85 = """c-pmnOONC@lIC9#`dpP2??>-p&|BTTvp~<FXR0xa#bOV1iSEH@N>osiS7t8u$K){&aTw&SE(47Ju{ASF9*^{g{4?&QJ2NZ7j2}fB?QQ?-
|NPEXzx(~~{`hY{o}Hcl?uXx%rnjpQKheMawR2_gVYPWS#iybSbsJ)DYG<21&`<WR_m+Pw#Nuh#d@X$Fir#j;ThSld!B(~@qAf$LOe`u#{~`Ti
S4P+N^qc(WFvQZPKYQDCp`kzj>0|3%NxxJEqCn(g(VoPFmdk$~8p9+yTMo7<ohd>wbb<e=jJ6LSe)oTWcn$vog8%d8TOEqd7RwN8Lp+P6@x&!E
*I1!|%Ohklh?lxA9Q@i<rly^5LcNH#<K?)`*QT&tIg}5k3Z3=?&*6cAzk<O33oq)yl$Mrf`8&|>#KM%lTifl|Kv6%<B96hm)_v<}y|po2v4R-
T0{8?PI+Lp*(kH64U-~!)4ET-W9-B`?WnKhI=bEB+k^W@bp&_}Wy3NOkV{mWrV@)hQ@fzaV6qWVq?gh<R-
c1n$cBebQd~sSEX}zYK?viQfjab@9zhkH6tm$VANtkbq_CTM`5!;x1#Q}HC(hr|(LEoku?B?G?K@TYN4&L!nv=Xg6jSI8^=Vw~cHr~L7*7Y>Fw
ehy#i`m9d4W&!#Sw*wRb1qKhhi!^dd!x0{*)83|@!Q)6{y3~`m8M=e`v0}-+`?P+`#zTswh0%wFbpKMB7GM>3S~OG_2%2!@!#p^qmebbhIJE-
h&+W4wh2ltkGVCWcS~A*I*+7N+Zczsl^fmKrhEBy)nPb+6}A;uc|>I#_!T1=#_W4Tx(ZA6&2#B|E;)IC1qNNI{}D~gCy=$%C{LR#s*_*!_L2T%
_^n^t&)QRP0xN7QG#cS@AO`fJ%W)j|AeN2@CGF-
>XWkv5je)(@eRmShm3$4+<LIXhi>mFlbg|LfcyoAQ;O|t*Fm1bC+LFG*FMSN5RcgZT$zhN*+8*m!wAtyES%#92R@c(<I{JewWZd*tqv(_fFK9C
^l$sx{tTgnb@U<%pe;W}j%uSx&Eb87YCK&v4?eXqxC-
Q|kEM2Tsh@Xzp#XxHOa4a}%vof217ol2)j&9$>&{R(8i919XgQ?ciik3ZNtVB5C=3ibD`eizJP3etZKbye>gMX!UTNpN@<&??wYBygaeGH@bUh
E-
^!Ms)+=H$*^4UQK|HiI8;6<;$mbjB;ZaOHds81Ngt5fa9if{$Z0zNA}?xuI)lOFoNwoAe}R*mm4zQcQ@~V5(@dsU{Oa43^SI=Sj7<U2m$*GabZ
|{>DyGV%FP_y>KOYQ(5(sJeLo)3HNG;v)H+j&slFeTHV5QHiN5q7g-
46C8l@%JZ!!+l~7&Nf3sxU#hPS|5pOpMnTp<)%0(3FO!63Hr9aJdfq1ZyV<y4DEBC{SY+JR&I!qk{tni(6Zq<krM|gIYv?R|T;9>J+;d)g>;Rt
CA>ZQu2N<Q0VbY(fJ2_t*@52WjFe(RNPp?NGY=vPX&&~(>GFKo?d?ePzj&93$X9iWYYz0TndX0x^FdCBae<}?Fao6bofdOU@h9Kv%rVH=Ul1ID
3QH#%frE@79=3$}+o23qL}bLj^-
PGfr)#}Jli3`v{F5e}Kf1cQI4Gd)<+CY~I>szsOJ=uJg7uxpIg?l?jogM6<`@nDt0utq^@QsgzI^_lX)XcIgRkcOaMo$2kX+S0*mY-
u~!ONvqJO|xZ~!>BsU0Rw)n2X5=|5^dshXMAs?So=h{$>If^%Lm(p3%$ufN@E;ztk}^JBn7FX-
*9!vk>_%l0S5b0>okgXZTv8LIm$q)W$)G*d`7$JVj!>7K5lw9BKzHw8X?v%n?hX{XUQ@880hO93W|J)u62`--
Lp28M>p9?8iRV1!DqsPMK+t(&u*&l%H>Xv=;m9jY=&=r3NLIk)P6D6mdwh9X`ROFU1Q(V#K5V&W3=6*I`pm@M2faCtOHrX{Fvl;qmDAbVBhEQd
DBl+Vg*De(WTl}oEenM;k}1E1o`?bhwr2heu|&g#<TJt^LS2n5XN9CbuY5(SA!V1ru1as7xm^#m(+qm)CF~7!7&CHY>l>6*`6c7iRZLFdO73DR
7xZ25M>OgTE7}|^iv9Z2EFPnJq*;9He0kC*sE;UY{T&VVP&4<zMVcXbT4TPsz!^FQ^Y~P$x7jWAbD91ojNz<2yG1PjY8(Kubgz7>DF|GSvYzJj
mnX?pDG6MR<9_w#+wDFl(MG28YH)rK7-icO9Ih{EIQ&0HrN(ud|0im(%q^OCl2|U-jwjGS{@;bLA+PVTxPa39Ji;tRTU4Rc8#r-
f_FDj2;R+^P8lpE6d;>yKbn=OF`SeUx_%%zVjivD6*-
3o241Nz+1HEihu8OvT`X!#{xEqA@<k>?zKxqNCCBRNK(>4mt9+LH4%!&lORYX^WEmt*VhkL(O~r6zeTjQquMQukkAYTaZb=?!X<j88k=;qASFL
+~j}ph=UhAu(?W3(*DRLQkbW_}?$x#n|fIJ3S6D{QbOdHN3G!%wZp_C#iuVjWA%H!lQ$hq>f=)A2g8Jf8gYj={xAS%64mR`fkNpQO94DER@v3k
FGu3ewOt$dg~23h5avP;*vch)rvPg!VCn(hZ_Ltt<9x$#SDtA#25&d;JPH_uC=kV(}zL>z;w)UDQ1fa3fxMlCkqTFDI5BHc$91F6xbMn`taa7>
Y!fh{s0bOz7?x){hy^}!9B=PHclVsw)TKo0lJUcwkmwcbQViY4~mWpJ#$(89o6>!a|lCR?j{R}|gG!7faW;QImc7~~su#X@D;etf|@(!oP?>S)
zIvKYi$mAhqI)h#AgSW0z_vO-}mRSe*rzJAO`yNF!+LSo&u+r);o%~3bDmpBIZK9@00U%|GMMdgb+tevU?ygY#g1pV$z-
#tX0G`eH#(e!rPZi+>x6e^G1rn($`L+0|rHbYT2ICd{#9%N;jo_{B4s*;~t7*(6ArxRFU(3M@im{T9Q2uLa$P4ii}Z`1Cz?Y)lC$3S1^$$Tvb(
tF5EA+cLqE+A>?DP_-5wzSv%95CQl%9s#8Gn2(Rw(`M~e4mbx#UN^8d=hAkg-KyY$x6&{jQ3K-0A|RKlF*`W=}%MgDR&9vnu0P<-po-
J7<7&PWk0s`fQ&rTnpjO5S?QeTM`&YU@05YB?YpqHQSw~y<e;a6L@{{Ez73%X{P5F?Ugrg9J2dR33IV*=)dZ$6YV!ZskG+kYFWn?h!Wc7FmIcn
>fB`?x;vQ$F=2fqRwTs4Q@{RALje)&Tw<#FI6Ksid%QM?a>a4gv!@`?P+4i&8U|VpRt?Nd|9a7eAEnG8p-
FQP61F7khC4D>xsh#H*C+5+nV0!A85tX&fN2z0gGkCC8aq~qIEK^vOjkFNi@2d~p9wCoGzR6<-Zc|@qQPPXK4vouZ0q&-
b0oLeKyo}VDF0ow>(!;Zjt~Sx>^r<7XF|c>J>bL8G3p|X77o+Q_a*!|vQ=?bC)YTTDb<J3<(-h5M*RPJA?iHTL0|9@2c9yxKVBxs8Nz(4=gH-
0l4UxUL-~cadGv4W8Kf7sT8^eiP-
U^6m6aHcfKYS*8+!H6VS1Ue~WSEEYAr!T12C29uW8K@;TlqcyCVM4+34V0Qc7=Hee3p%;Pn?=~e@E{_@fRc2Qr1f{bHDjgjBLx~+bn61QU|=+c
`rsY9h|>APiM*YF?7GD$6eTO%P4zCicVnH;Mhz$+US`Ve`ec-A6^=Z5);yhi01ZR$Y3>9_)z>$sYj&+NQOK&S!^V-
7Z#7S(?6ttW;gU|FjHnt3aBuA?g=GM`46v8#zWt?-S2<;sbg%V{m>Av538{L$(q<d{IoP>-
~IIZ`26CSE`v+o!?LDo9!>m#*3pqhLu*b8nwHqT4(4oshIVMg_3ngRoOD87E3Jl`7W2w#H$J^aAsO1^l(8#ti2)q@;mEP<=s@+(ORf+*s<=ega
?WyXn>^XU^EhD}aCOoKjBZ`CkRUyuWIBI;b2iddTG18Jd2{!Y#h_hd-`0MlBW0Uy&!apovUXF&fZdz~OcWGJCl}^R(<K>6Tl|-
yQE4apsbauxu`iZVMmiSjksGgdA{J}c)l$yG5;B8DF^>xd{O<HGn!Ihc^sW^P?sbFkZYX6Y1gi<P?etE)S!^)q_t-c8Cwda?7~U%)-
blFJOAvzdzP0|GFZs%NW51&9ZHOWDd>#L$YymZk0S5OR`+A*Z6<2hAnu2@U($&fk2i{E;19oxxcNBeuMS|h>1w%FNa7PkC_4y9b#lR`Fp3qd>{
crQ!)smGb`X=|+8YArdPoy)K9N)-
OKYtoWY(o$&XiB~qYu3Es#c@R`8LWy#$Z{5O3?`@%J(y3$I{4DC#zJ;Pke9yX(meX(BE$?|dJYc^G@vcHrjp_oU)a`3(`nTO-
a!t70_sP`uLc>Z6ZqtiK`LW)mYZ*#%g}-
AFm(**9b%P?v)<B`sksG(BGaNgL=yvbj~dfbOz5S%*H~P*iq1;*hw)_2+n6Qc^C%Mt_Qe@&t?(d=j<}JI{UZBxy#fzY#sHqH4=eki*qxP3DE9A
_CgZu?MIM6+`h(anR&Ktsi!4>8)H0tWM}GMZvKX{WjZr-^Uc0sF@)*>wDPn-G;BRHvXW1Fgb{+dZ*_Byw|FsMsY%gsL<TY^jN*Bw)r!fSEi!N-
+FdNU3vcB#JaSSG)!%WQ-KFc({dPsc~I6T(m>C&*1Fb3}yKB_h6%`LhR7wih&eEaB9Pa<0PBIrBn9_N4o#{4~WthyntMh2zbd|_KaUjVU#C<g0
Z{SpSBRbyjv5R}U^^-DLplFaA9XME^hQN@6P9-A>}_Ngent3^vpiMiqcRo}D2)G?qJio=-lG>3)FHGMi!!+>0>T#Aje3opqa3Or8-
iDIy>;Mig`pTacu*x1x~#QS0G%(hW1)2ees8)x&vHsKn62$*%s$?G>?W1Z(A_?{>R>qd9?3KPq)d5*5jHvN4|5d(CKdQ6Llp|+CiJ@tAm?Ap)?
%auuggaHN@jYrX?=#pGW%I^>trZE}1DeWSQK|^#D>50;Erap%NQ`3R4FbkLFJF$CSM1pdb={zP7>?>Vds;6sY#~uq0^y4LIiJ6{~U8FIH=dj9F
(rx)HQcv6n<zU!FTbgyAD8_LP7+@eq)ko8GsdS7*hpofPhlSJK(Y-`5SYULj8!EXulGkOMWppOTtkpeaF=)y-6S0kUDbbN!(WO@;F-
U+0)0&p9gxrL*f|cKVTMYas(kdIJi}yHn4CoCkUN~>@TWwZh3QrfCFC|`#)XpG{LA-
^YeRh(#lHMv8>ZBEOTsB7^@ttHbXm^mKkbWb&&#AuNS!H$6dukYvdpvgE4y}`TfM|-
++l`bB&Zo@M!*nlo2<Wv=V_Ca6NVsERO46%z)k25pV&K4-
QII$eXFrTVSF@Jn<W)31w=GfIOGg=CaKX5dB)Ja0<#1h+=L=G!I17*a>*p9Bb({kR_!9WO((u=EJpx%dBqzo}8G)Vbk^b`4lbqLm;dv}D$XB>v
G7I}CamspN=QFK&=uMX7q1}`*fY;caC3!e3{itg>=B6F^wvQ+V3y3XAvBu`NMmo@W5*m%`ImS%Nm3Ge89<mrT&}$>&E(H)4#(Uf7&*Bb}7$iiG
83!G3amXT0ndc(lS^9BVOpZAU2gqYkK~3kC{*ij>O-W>>T^ce4+K{2O-
7F>$>>EJuakZ>el0?OS6qliMT}l)+5}TzLPNf3PWPw3GSD3}Tq9y0~Zl2jha9y^JT5qUgz%KAN@gY2#tx`g!PpI>}h`Z=w;1C_B<8YDWfbgQo2
Kwl@wY2Uz+)Wb$bp^hLT(p!1EOQ;ADONUe(|`4IxQ8wV?pl#QO5$wuB`$(AS0iD^-PPnQWyv4iOC19W#-
A$Jad#=xOxvBNg0J<R`i>FDU;_Rc5pY{abkZLmLc>~r?Kn|z^IU3^Ea&pTK;PkMw9#yyKXXlesxTy#Y;Exdo9ztJ7{q%#7qM9SkfC|{4ssBb+c
WSc+9myDCFRoG_>J@}>F_YQCAjpp*SkArvcaI^@u&wWJEyJhbEI6pqJ{yvP<i4=zmVWwYr9-
kY_CaTkS=i{A_LW;nKH2|ZjO{{?^y@QAxjQ(zyNC^Pn<vDYCPmy?xuzTxrWn*I4CK%zO^e;n5m0*2Jyd_GzRfTrGpk`E#g|{U2tnFt~>AbPr^(
V7-T#HIJK1LltC#BoNR!#DL2nKB5VigV_-oI=7C$3abKL4pRBRip1Z;1NF+K)9D{kU6FEj^MB7|4XCwzfxjRGC^vG0;G6l{TOM1M7b72Oux;Nj
}&gU4{bdUiC7q99LA6;cer6b0Wp`!a8MGVjd8rW|Ck$!0Ecff_%`k?lABr!;ru*7^c3%=9Q)`MMJHdV4z_Us~yLA%llj%d04H?JmTL;ScfT}DB
&lRO6X8qO>2=*BPjLE<AdG-<{au~}K4Ew%J04-7P*--L3Ak?k^RwNhISUdF<F-
uzbThI}6+jKRCrdD+;#&TcRwpITX1Z_7Tq(q(W}%wmGUzSG{?1^sf|JezzMb)tv?x`!p~+BIesc>+VeOt0@~LZI%?K-
+@5KAT>W2C5L%cEnq97?g9BTjIgBn{O$!BaKpn;^;lip^bsWJMh_$t&Of0@A9_yArBsl!RKffeSka$^%7OGxm`6UKe{njUawWZr-
%UpGh(D8<@CUkjyQ#0#V4x{TpuEi!Ms*gREWVMe_b0tDHy5_s^xqR7~mVYTiZCEa%{XQ50%f*ooyFc4B9Ph`K8pdrZb-cXMb497i8(4qpjC|;u
uVzzUieCbF^!h+#<Y0_VaalT0HL{jKM=ZFH=T~Bm;)Zj`NWJKeTo}$^!v?aRz8Msjl<I8c%=U&VZO2$g9E@b9rE(-
|0Yqvt{$r&$?pg(7ri*FD=wr0h8)7Q=7_6GtQUBcd5gAmt!*DDeSPVxHxGm-ektfhp>%j&6GdRgX<n#v&xYbw}&(a@e=#mL~bo*XG1rhInMiu<
4f2_(`A`SHj@no{puv>a=Xp8B+U#QpP+SbXWH}2!Tq#@Qh3khfq}lpzPB{<3jHK&=vlGcvwc`htIN_Y><|MC?#=1ncq|Vty;<8d>agUPaBI5m@
AgxM!s9)ZF@U$H17vGCawGYa2DWs*k1t0o!}WbSjSB|+4m-%M>3YK_i*C^{7A#11@i_iaJw@>deGKe9@DRNoEoO>e?Sc*-Y4MfGHn8jsRS4Mo-
o|r|@7BBwHR-dxlXrm@SGhEJX_^wJj!vJ%2!nrqI{c|uRvE(IU24DA+0~$%{rhyBG6wMCbbzm%UM**)cFDfpe5sA}i{uK<&9^1qitFh#E*S7j{
GByzTeKX+TiLf&RXN_+y~Ht?fDXl?UvxSNz;=C_jm}B`>8)3cMtGV_9|L<0NMTRcM`k9Qah6TA+?=5c#Lg?LWRB3rKw=t`47OQDlN#CCk3DxvF
U<5OeTe%Ibqwe&enZR9reSC-AES74qm_oXVuq8ImhHaIWQA?P9jqNc3^G26o<cf-Ugj`0q}8spk(?RiF{qdZwRUWGjt@j9>*%fDd{w+Y<qXmg#
0x-|icZE=zDlYe^_#Bvmw%--
b)xLKN|(Gpp9=>39KXr`{STwT>6$g?8^$pkV^R)sT;XFpFwlr^YSLJz6?836|1&A+QfnC;BaXqmR4I_$7~eMI^u2<=fbzpW&1QhXy+V)j==|P>
8Eu+G+hqvL?xBnUM0BWknNnnr*`^w`R^wM33hx!&3d@t2V6ag?6iG+hF3sOFOi`aGVE}Gb9th8sFsWI*pZ<BWE0>1V)l5!_<BTx)pts43^q09-
9sS4Qlg&7{wmppt2K*j6xU?d9>KZdS`$$y}`Xq`SL?Kw0fUfisRJCj4hZK((Wg{;(Sz(gY-}NC={B{;AYzqM2(@SQfWo!$Vm{u-
MX2`F0ktcQX00Ru}1!~v+@t=Ruo3BI!TlS^qp#J0E{`S{j@*G4Vg+aK2Wv8d#5(bm=T&B@hHcXM;43hIG4-7P-
=Zs^>*g)F4bXxN?*k0)<Iz$+QccW6v|A+hW&#n-QsJF4PeI{-EJGvM+*fT`;rFY>a{lJTb-
|=ANo~<C}Xg}t04bA6;Z36Ba`uUIloWTV|RIr8LD=dsD0Mc?>I?D;g<-_J{#<6?vNkb5?&aj}b#IJbzd&-%a+-
q4fufHdYK|4oMZe(iXY9MWa2f(L6r0i^onmWdE4s8tNh2~Kg*|zyA9q7cx67sz8-
_ymwUBb`3YnD?QakS!TXi4WCvwi9|<}j3w^1wh}!P2rH8xL%^-
!5(0yLFBh_j_q$Affn|wJ~)o=L6M;evHMD$e<NfPT2(KIC%`}4R(ktCxRilL3!*Uhv@i21d@x%4X!=IGgx4dZ&4T3GBjgguD0XUC%w072T=^x9
dKw<#)mAec3p}XFHBP!bwAvLlrez!DpfqPM`bEWX+k}=!;V&`7tG@T0lq#%ADE6KrnT*i<hHB~DP_!UMIWT;IrpDy-
g)+1lcjm}OkUU~oNH8wBrR!Oflc0_(N;Jeri=l+&;$zTp$|)&((Po*OKqCUWNYKNgEj^d)RnkBVZ*I7Xhj`Q{$N>YyV7*lNU%abq2dSw3@)H0N
jC#}4>r#{@j4~Er)6ml?0%{kuxphJ=Gmo@Z23hTL|<uapDVX*7ikP47Qsp(LsB_K5O}i)QC*(4lO_fViE5c;YE7KlWb^EGx8@QuIz;98q^ktY4
Eh*Y)T2`@91DZZZws$1T-rengK`hsn5=-=(c_zZXWWe<Duqfrp92K=<_xwk?MHTnno<3-
E0f8#+({P$cdoE2)2_+~Q0Xz{VX7Fg3;39h8V09CrA0`)u#RV%M!PMG%5YleF~Z;jv8yRB&P=1_yI~9jcB&MJLv%54SCFG}dYI#A38WuygWo)J
p_kNn*>&(knZa{;8Z&Ggt~GWDy>t&#FuxmWo;a1V;(D9M967)MgL|Va#3@?SN8aqvl|u|12pF^SvsLBnXMsV!MJq%{Pscd1Np78O*4)=BQ?1nu
78v9^TyTxMJ^GTzylu7*$w~}4B-lX)7~FeJnRB#b6<-
&+mabdqOqZw1c^72};O%MJ)6c`^3){PCUg}^M(tEofxEl?fto301n(RfMkVp596IK*GB@tfOCY&om6w%62GrpJhE?j|}B|Nc%E(Q+Nw4z<Pu8&
f#IoQZr5M47)0*O&k$KB4QkAb}e?ki6^tXWjDW|y+a=&viQ(=ql^#eiLDl!-Pv>EM#Kf0%*>+owPqmpF|RwgJ~z^qa-xly*<{inNjZt#@7<`QA
qt1Bb@cLOIl_ZlaB(<5XilZ<hk{W;}fAxY|5681!4b%(=3jjO(;y!p8$5*(K{u)VV<C(8s_c5jWDylPWjz;uz=DEx;{#xQFgA&!CTi1wBzUoiF
JTFnTdLklT&_O7Ftpd!ujhIEx7c`wsU<5w$4#ocN1U-=a@8k3zARHU{!sSG>;gKklLSNw(ZHxoVESCyc=Zb*AZ&69+Z7zhgaSti)9-
Ob3Z$FjX1UGKh|op<?RbNG1tA5n31O9Qqj8E7X<BEu|jWPZAZ9r`$&m19PoQs^UXca-hBBfJ5zku8gYh2xIUNU(&l4lqLJA$MPmx6$gt3Wi8b#
4j5pqCrNq$baZ>Tm@Q?Ja6PzfR)!SSY~G~9Y%u6|Xc-
k*kkiDBaZ+ZbPOsWW7K5hDKS~*EX3+(oLe$(#mP4Mo(vS8sfZ*Pr>3RZkTU_~N{)Jky6_<`fOu0G(?qz_%J=fLi7OiPy;*E!U>X(OTVxW{=i9$
c+BXXg|DqoZD9h5PEh=<7d+K_lRFRZh5&_7HXgLs8EeOQEgk)lGZV2(lhjw8RMlR1Sqw>^yu1{~FjWJYKj&d_IQ((;xZ1_jc9YA$F_70&!;+Xd
2{FaM}hdiD^-
VBIQ=<Er2$FfunIm1KCg(#AuN631ZPDW3*1b!eNXaZ^6q^YD%?2JT*E92cqkfGfRul<dMZ3x(7z#UR}FBqj*#%d<1p%P2#_O#iB-
9RCZc(D|OoLo6`J?=+l$99zb*cV%d*uxpeoQ}5&OiFTur$c_lXu84tyu<8-
AN62F^FJ{9`eayKrRqtd8?2GB>=WU&`*`+q08=$M2n9pH=LA^Zji%!C0VQ7UzFJ+o_5*{QvIbVM@D1+MbSYU9kPW!UUL0Th@`&~3cz4;nB6SFp
-jBZBv0m2xx>)FuWlzEhHs0_D46z_!`u}7ITMvvg;IY*Y~aUK}po729f^a|g6laxi%(*LHu;Z;o*U)N_C+C7T_2KDxIxf|ljG$i`@7MWN+q{L{
sJbI~nkT?eM?zFFIV=|1=(fX0Qr&YSJ$S#5ylzUL7PU4-6AnvCn!9}y88&Z<_o=2u0W&y!{-
<SH>my;<ZbWKWWp`1qH4RNLO)a@mTK?3xg+Eu&&PHK0t9A0|ck>MUWXkoRN?l=bw>;)!AIU#zQc*KH@EF{uJHs4yjyWG=U`WVntb)7~yOD`?bE
Sqs1+*>L(Iw#LT${4sS)h(Qc<Z&zSu+Rozj}pfqUY~v|xnb(Ch~sASB_Z=*kYrF_`~hyhQqHB10X<Q(d2pXO;MBQ=w`0lzcgTIoGm{dHPCbEsJ
{t@+pylv0P0JaT%2a>C10<xU(Kw3Ds@0u&Trkil>OFPn*li(7=H_ct4QZs_pTkg^!K<1>9U+auy9XYZt(Nj?$fel2e>U74_mh5N&=Cd@)Qhtdk
FQyq=5yNbH@!D`Iv3Z(dsEW?aj;6<R7wr-WNz3doT@pIUDR~T5bGpC#i87!kxrFc4&5{a$5mFj0Vi?7z@O?jqSw%~`OiLdzjo>CM7yMAa~o(~<
l#7V4CLkMeg?LMeQ7vh)OpW#Rc#*w%bLkEkYU8#5e^vGs}qm&SRxjhwA<39eihA9mnF29DhBFWp<Xb1zDV*r*|do_R54IDCw{3(M@{mO+W_*7s
15h7cD(0)ayth7(9L;#FyOb4vwB?7%Y>$diBUJj>@Z~v+}(*^Rc`(EdG}UISjlGW6|to9IAsjnJtRq^_2H40Q*OR+@Jd|C+qX^eXtbyBfB;{f!
JdYtTaZzewmX-
1;SEg;(D`YAUd84(t*RfmR^EqZ#ed8c^!uJL2JPbX!})r?@Wa59S|0eyWM~z!pE3sS@<eCzIE<2M8+y5_7{<B5Il4paB8$PgI{lkHkhMeF5m~l
u0*z4_Uxae=6)(bV=TXN%0$w1IT4}C>?~T?Q@Rk||;s!W?1^rN+p{I<H!IpgsyjUMO#@Qt2U+G<~??k?XBnIaWa`RgW>-
k<Gw97r@Fc|mnD^#17-
oedtm%0m0?JjcV6YnDr!Mr*{0^DO+Q*yBX6RFuoW@5|lc9I3v4WzhAnqiKPMyIgDw&7F{3;jna)lA7U^xDLA${cCj+UhdN4wJ^<o#;b(HU6V34
add|y)`*r=fjjSaG39;A(hp>ZZ%}Pepu5>8lzj74C?-21{l;UFbFOIBl^K+HF%@%?6aRN2J0Hq9A8U?YzOohZ4BV4eiW%-
D?^BtZDa(<%5GQC>1*TmQO3Xl`pbX&>n}xPOHyL{ZC!f`bg8xD1Eeu{cZgOgk92SA&6hq)%fh$xFd(O9&`i^r<LhBwZ!ZI}S~`y6>CWT{j3DUO
XUI34@(AhaeKjld)qTlO!f=cQ2KOAdDAELHZi%xRq#j7|b=z6QF^DH>G}D-
nR~!B|w2@;5$zI|ZL^O+dOlM|cK~^>ArLnk|BGN9`B$>SoFsOi!h1BELo1{!Obe&ow%}v)fW{7+pB#uEmUB@vczhYD4`k|4z3+m>@d#GZdZca6
l(<~b@(ZhONLB&pR5q3%g`5<Ww9*{fpl9|lP@xpYRw=~3sY1A&V1Eeu{kY>}S=h^g*J9=vKgLjj};Gh}8+dye67Mmm>)uGB&5Vnsx1oGxgS&+c
KF*a$Y8{!M&qRm>5u$u)2_goh+ag_@he4{%^VsI`nL)Uo2Q8g|L?eQt;PX|b1aDd$3RN_j!?b;bd30Jw7AO__McJ~^;G>bIVpmVgV96`%fYq*0
n2JadRVvWZ{vNEHohLRIYx-<^AH+7Cm^_gri*f-F9^R{98M5^Vv|7(W(_MRjL2hc~PF>@;BY__s1SH;pn;uyp`=!;p-
`WefF+t3bpvyZ34R54IMP6|IY+_GYvv+a0H481_xn)x!r)b`^nAh@?@U@*BUn!$3gW0D71g38}f#XteoOPm4QR8#KO;HBpe>qE8KJbzYKNgSk(
fxLk1aC)z#acM&j)|mI5!2sVu6$5pN)z@>8l+?d(xlgkje6i#TTfQ+v$MFxJqu~A&e%MARs+njFV!6n_F$W*$54wi(bLeA0fozshzPmA-zgG@j
-boPya|1=_*`*`(@a!)j-YeW+-5w!}!Mas>H#xUg+>NX+x-
2D0a~NPy?~rmGNnlw;$C90`8rw)os`;$bM~@Q6Al?J7BTuK~EKwGErR8y)`l7O(L?K9bXOJd3HEb-W%9p^EAx#EtbPr_=+&P-x-k9~aTep-
)d!H-8eJ5!Q-
UaFkl)h<k^V=hd?p*z#UMON<E>%UyV;t2i*@_9JmE`lBg~+=ZU{J44y>tCgO^!KB%MDV3#UmQIH=|Wr?nj7Y5U=s{$TkL1`6st(t!!y|m^20t^
SE%yD8I6jZo}zso99f4JbNf(;BG<Zdx(<L$I&;Lt;ro;NUvDij_ypJW<ZBoU~o^=TcTZCzb)ojJM%bNFaOn=mDf(sJ470T2k0zYSvQ*9X-
NDe^n%(9JWL*fd4C3JpPbIX3ch!}wDx=5H6(-
nd5Am)Q&BZ!xi*~#hY$54+FT_=Z>eISF7QMi@yxnjDqMMlfpoOXS0=EBJO=ah$|1{br5COWX;x0BjY5A%4+8?^vApV~DXAIUzs)t`xlFfV98_#
FHtjsj2!nnN+w&#2OO>>+HY{?cC+{YW!Mi~-
=y@2Xt3$(Htz>QcOhdrFCyYS@qDn+Z@}hbk9w@qS=H@U*8DLPMj2C{HoJ?cRHi7&*k{BF7gCX%oKQHNuV~@e&fqrfCEoRVP4iZNoUY(sm#U0WV
;A5KUC_<0!hGf1^L)P?d8(WYawhiyJn_ui|h~rpr9<4<?zxh&*W!&E-zP_5-I$8-S;kYwzUzPv-k3S{LkCU;uy?~^e*~cV7*-
G^0llh0@pVN>Qu{KtwF_AQIE+$}Q^-
av4_a$YkZ8?7^{)q=ce;r*1zBWG;OCNaJs3YZmo4U{Y#54;YiQ=sfsqtr!j9U3e_C>px+D?1(q4>pd6jQp~i#}rLhkhtpHgL_Sp<*O!PA^N-
PK!k}pTmdZFVi$d-b`+$Iz?i(qXIs>J`@jq-
*&(M>8D?R{q@7I*7OfHeprR|Pvt}R6Yb(SAhmmac4)W!P(Gx?^L{)23s>^ewtkj+ueVrPcjR*++r#E~o5raznD^)70yrPv4~OQg!ltrmtgn3RY
(t^HCyiZ%O91FrGVpA9!%Vy2)rBT+h+$x^;IB4xvZ(m#vhl2>2Rc3^Y3XLH4O7s)!*iKn;IDNejl_lVtAPh#rDk%QFFYu7CHI?0CwbGzt<q-
ppTG*+h#Sq3X6KKQ*4^ASQF@S7GO?QUc~0YqigDQONlY;Cx9BOD#*t4!@+o|fW5oG;ni#Y@g-qrgxHyiE>Za$rbzSKitxP^d8UuQ-Il!bo1#ia
z5;4?mQc%*g8hS9eST;xZo#RX(@b4Qn&-=>b&~+Kb&6-
A<(Cy`tDF?alq=`XODxKB9>HP9$^tN7j8DW>~I2V+`nRy&A*cY1POmE|(JOy;H){?$t#!JTKVYOQ8I7T0Xd<lyx)A7#|$9k}mv}=5?Of20^5(9
RH9$~sPu`*lBsSae$dQo0&ZKEmy^Jy-94DvPnExB%^7w1w;WjSLj(`oj)Zo<_O;uu(!?zAQ`krtFDqVVQ(>u{9|vYkgAgL|u#$Yg8M-
()RYfw3HH>@#S|2Z&=}?@+MQxUtRGG-
1BmJa=`TaPoIFF=#4{i6<MkjuW>d_j7pUre9|BTeF?;NB0c3d)gD(KpSvzmcd_<8U=LQPtg^DTL7uu&$BpSu+P;tZ#URx?32cArGq%Y9)>z(F?
07)$KYNloi*Zs5dD>&N%|P6^(igZ>FbV;kjDVydK8zNTf-jXP8^$+83n1Kud^VPULO{l#{vU>r8VP6J;*g(Z>B)q%dE&8M*U$980>4E1CK@Q$D
ZsJTB~VeXdPZpT^=Ee0aWQ%C8rc8mM!Z6W_&u9k)%x2NUin+78r1)rX^-+V1v{YE0e+0eMb-jb*FxQcyfDa4f{b|L%M--7W^T)7(|t3<y}p8h2
DMV`zR)7YyH5!%`vd2cBCF-0D->L`JmV)5%IXTpJiM$&y6PCE<K5Achq6>7~t~^>LX`Tq{yZzOR-
L^R17R)SevdKv;*T$;)HF(g;GfQ*C9m`EHAEy91`mQbquaH_E!h8$w|IQjM+pt#<WD?B~YAMQsoE>&f<e@0jy_@@+FP7bGES~XPGsgbRo_gc56
|F|Mlm;Y7W53%&^V4RyhdRVZq(%otNJGq%qmZCN9r+&egW>C<_eu4eqWj`(X@l3Dc*+)`s2aoE@R-
;&+%d2J}|vCn3Ye)`2uco>@5^%AS3WPlF=?TukRt?<<+j3fqXgO!*zrnz5^?A=4*H`R0nt1TrRi?B#($zt5H@&^qql_I_Ab*8G6oEFj=lXPUz=
dA*WTMCVSp`Sc3$B6&I+tDk20=zNAr5+^akHsf3wWA<jvk1l<iG{Rou;3-
3mu56Ypz+)^h;INMOk}1q_Lg!x!N4Nb9^Tc9LVuWpiO7pYbYk|zcMN&#%&uZpS>dVAf^+`C59kwA?8Qz08$^Z4{E4P0ss-
X&9uC%`c95C1#jnB)_KB-=j-dc22^9<%aMjL~w^1Sf^xJEb4(Q0H)BX?3+yEv#t-9h3Q*xP(&4Jq0+=QmmINgp*W%ARI3z(C_V-
I!+|rH#WdmA7&|WE`B*gM5TG22~gDWS_PyOCnMoS6{zPOI54yM>#;SuQh%-
W;1wB<r2RE7icHfftN0F#^ZBx=5xSct8_K9h=H@^yQD>v<}gIDCAgKZUUnU%j={xq?^CI^OsuzFl4`4BoSoZ^GG~fqC~x&ioUm=URBGt;=G)qN
Sx_|GL7h2CvT6q1d_Qpv?3F?h;Zfj{{ZzU!<UFu*{9*H44n9L6>jB~zSUk#Uy<Lg++m(S`-YEf0d6xGP#lYQU2=sYBtl90uMNysjG-
=($%tn(b@^^p(23zG>tBuUujc=ugm^vz-N;{hY1{&A6Qa%hv?o97iQsB2HEdkd($|GbkfcN?A<SA{UvBT)A?($m3I~YKqZ}42QG7da-hKzHcO8
@BKePRW0BB2{neT+H=SD8ar4pO$n6Ok4vNHI;7=22yVptwH6Je1jtuuZ^qu9vi2>C5a*%~hs6Dq`Rg#kWzP|NM`?+4M785AV|;b(*$hc@($5^$
*3Le9>%vV_#=c2UasU`b}yz*PKetYD!EozDxW&`++NIIVxr%CkU6G+w~NUn>MQZfs0^e6PBB2&O_u%Lz}u~ZqupB9{o`KJXpWtrywo1-
~7h1WLnRdwJ2*}I@&7n%+k_H^gLQAGBxrk#n}5${M&Yqwv|w0bSHrrYfPlS63OS~?iyLKFNpt#WnW5>EWvaoot~c_!mmHFmuS_v&-
O<;CO?{WaMh3PgX<n#v-+_sP5q{b_7783Y5HKUv0Y2AUuAxH^+{RO@If<d#7wANQ`weNN~Hey-
9frkM;Giz?z1FambQv!mYBjW!q{!O(t8?8&LWeOunb&{u{5>wPSInnoJ${re4VYXa7-
9XD|mHHvKAWdV}gOdQ6@@^GRaLP>toM)zFjrzpO5+pOY^v3@NX4rUc<d(QVwP6aS)PWY=%m!>K!7D0oCX8O{3C#nY&l?p;pcpIZPRYd7mlx&2K
O9T1uX%R9dy(hK!N#-
3%bmw`a;bY!;DouTmS9t}vAhitk<?&XD5{&)|Z=Ki4@}>d<VyeRL@tOUqw`CWB{X7gY?Nsxo4FJ>G{~CCJ#PCZ*bMJBJ4b{Zem)r!k=`GmVnWV
}rk^iov_m$Lo{g97vqdPIqabr1e$`6%<zK(`j5V_}3~AM6xToupqf=;!5&{%ZFj9KhFn9V?Y%-
c)sSbE5tITgQvSxg?jU~)A(7+dDJnuaD<lgVeRMAr)C6G0z3&*ZlI#-
)^V6J1{3!XO24mhY7p7kNdXwUqv$7g?;(tVyw?>?%Yz_$o*D!>Qg`TBkttUVWro==$2mZ-
?=;a^Qx1~KF0CduUrTAn%T;q;<1H)aQODq_qOemriZp5CQSr%C**u3_ZAibTjKRE6D2kGr_cBvK9JcE5io1zo;BZ~3v)oKBzM3XP3#n4}S;+xl
_4K!+^fAa+>QoUPuu5yRT(>?hPcf6RokJUgdYz?ccKZqFuWQpOefLL5V?b{dk~i8V&pC;s@`ksx+eZ(BbgOIH#tkM@mhjdE$hW4^x4Jq+8-
uEensT?emG$FN^TgHmQpMoi>kT$>+WN`sLrh#utpt?g@SaX&18u;)*3(34*+Q0GyRly@Es9<Mm!cS5`amXww`nFPY#YuMVPrdn6FFTWT{wCeL{
-hvF{(U~4YmOnS$bu0B6Mqf@{zstKhD-GYY%-
4vZ7x{92KDSJyLV>j30XjeGIZnznYxg_9eFLLzxmr^~J;OiEOY9z_Zzw?(tpoGU7L+21!%AQa89@1_KOqjx4t_a4Rp8!Jb~<vC_#8pEG5+?V*m
rz0Kg9GvmPSOc(kPVGQJ5h8&orPUPyGb$~7gQRS&>qmlm>Q|F^@%xZU)S{2z(8G(6yhG(!zZ-ppLs4KS~JUc$$R9#6(Qg?7?v6v0~fB!%6wD2t"""
# VALORES HARDCODE PARA PRUEBAS LOCALES (ficticios, nunca credenciales reales).
# Los secretos de GitHub prevalecen sobre estos valores.
# Para pruebas locales se puede sustituir el valor de demostración.
# No introduzcas credenciales reales en un repositorio público.
TEST_OPENROUTER_API_KEY = "PON_AQUI_TU_CLAVE_DE_PRUEBA"
TEST_INSTAGRAM_TOKEN = "PON_AQUI_TU_TOKEN_DE_PRUEBA"
TEST_INSTAGRAM_USER_ID = "00000000000000000"

# Únicamente se acepta el router gratuito o un modelo con sufijo :free.
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openrouter/free').strip() or 'openrouter/free'
if OPENROUTER_MODEL != 'openrouter/free' and not OPENROUTER_MODEL.endswith(':free'):
    raise RuntimeError('Modelo no gratuito rechazado: configura openrouter/free o un modelo :free')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'

GRAPH_VERSION = os.getenv('IG_GRAPH_VERSION', 'v25.0')

def credential(name, demo):
    value = os.getenv(name, '').strip() or demo
    if not value or value.startswith('PON_AQUI_') or value == '00000000000000000':
        raise RuntimeError(f'Configura {name} como secreto de GitHub o valor de prueba local')
    return value

BRAND = 'DATAVIRAL'


def catalog():
    return json.loads(zlib.decompress(base64.b85decode(''.join(CATALOG_B85.split()))))


def _parse_ai_json(text):
    """Parsea un objeto JSON completo; admite fences y texto envolvente.

    No intenta cerrar comillas ni fabricar campos de un JSON truncado.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Respuesta sin texto JSON')
    cleaned = text.strip()
    fenced = re.fullmatch(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned, flags=re.I)
    if fenced:
        cleaned = fenced.group(1).strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find('{')
        if start < 0:
            raise
        value, end = json.JSONDecoder().raw_decode(cleaned[start:])
        rest = cleaned[start + end:].strip()
        if rest and not rest.startswith('```'):
            raise ValueError('Texto inesperado después del JSON')
    if not isinstance(value, dict):
        raise ValueError('OpenRouter debe devolver un objeto JSON')
    return value


def _validate_ai_data(data):
    for field in ('title', 'script', 'lesson', 'fact'):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f'Guion de IA sin campo requerido: {field}')
    words = len(data['script'].split())
    if not 30 <= words <= 60:
        raise ValueError(f'Duración incompatible: {words} palabras (30-60 aceptadas)')
    return data


def ajustar_texto_visual(texto, max_caracteres=40, max_palabras=6):
    """Obtiene una microfrase SIN cortar letras ni añadir puntos suspensivos.

    Si la entrada excede seis palabras, se utiliza una frase breve completa
    cuando sea posible. En caso contrario, se elige un grupo de palabras
    recortado en frontera léxica y se quita un conector final colgante.
    """
    texto = re.sub(r'\s+', ' ', str(texto or '')).strip(' \t\n.,;:')
    texto = re.sub(r'https?://\S+', '', texto).strip()
    # Si una pregunta original queda demasiado larga, presentar la afirmación central.
    if len(texto.split()) > max_palabras:
        texto = re.sub(r'^[¿¡]?\s*(?:sab[ií]as que|sab[ií]as|te imaginas que)\s+', '', texto, flags=re.I)
    texto = texto.lstrip('¿¡')
    if not texto:
        return 'DESCUBRE ALGO NUEVO'
    candidatos = re.split(r'(?<=[.!?;:])\s+|\s+[—–]\s+|,\s+', texto)
    candidatos = [x.strip(' .,:;!?') for x in candidatos if x.strip(' .,:;!?')]
    candidato = next((x for x in candidatos if len(x.split()) <= max_palabras
                      and len(x) <= max_caracteres), candidatos[0] if candidatos else texto)
    palabras = candidato.split()
    elegidas = []
    for palabra in palabras:
        if len(elegidas) >= max_palabras or len(' '.join(elegidas + [palabra])) > max_caracteres:
            break
        elegidas.append(palabra)
    conectores = {'de', 'del', 'la', 'el', 'los', 'las', 'un', 'una', 'y', 'o', 'que',
                  'para', 'por', 'con', 'sin', 'en', 'a', 'al', 'su', 'sus', 'es'}
    while len(elegidas) > 2 and elegidas[-1].lower().strip('.,:;') in conectores:
        elegidas.pop()
    return ' '.join(elegidas).strip(' .,:;!?¿¡') or 'DATO SORPRENDENTE'


# Los textos son ideas completas, nunca fragmentos cortados.
VISUAL_MIN_WORDS = 3
VISUAL_MAX_WORDS = 9
VISUAL_MAX_CHARS = 52
GENERIC_VISUALS = (
    'sabias esto', 'ahora ya lo sabes', 'dato sorprendente',
    'descubre algo nuevo', 'una idea util', 'increible pero cierto',
    'no te lo pierdas', 'esto te sorprendera', 'sigue aprendiendo',
    'te imaginas', 'mira esto', 'un dato real',
)
VISUAL_STOP_WORDS = {
    'a', 'al', 'ante', 'como', 'con', 'de', 'del', 'desde', 'donde',
    'el', 'ella', 'en', 'entre', 'es', 'esa', 'ese', 'esta', 'este',
    'hay', 'la', 'las', 'le', 'lo', 'los', 'más', 'menos', 'mi',
    'no', 'nos', 'o', 'para', 'pero', 'por', 'porque', 'que',
    'se', 'sin', 'su', 'sus', 'te', 'tu', 'tus', 'un', 'una', 'uno',
    'y', 'ya', 'si', 'son', 'puede', 'pueden', 'ser', 'tiene',
}


def _visual_normalizado(value):
    import unicodedata
    text = unicodedata.normalize('NFKD', str(value).lower())
    return ''.join(c for c in text if not unicodedata.combining(c))


def _palabras_relevantes(value):
    return {w for w in re.findall(r'[a-z0-9]+', _visual_normalizado(value))
            if len(w) >= 4 and w not in VISUAL_STOP_WORDS}


def validar_microfrases(visuals, script, title='', fact='', lesson=''):
    """Valida significado básico y legibilidad; nunca recorta una idea.

    Verifica relación léxica con el relato; no pretende garantizar exactitud
    factual ni reemplazar una revisión editorial humana.
    """
    if not isinstance(visuals, list) or len(visuals) != 5:
        raise ValueError('Se requieren cinco micromensajes relacionados con el guion')
    universo = _palabras_relevantes(' '.join([script, title, fact, lesson]))
    seen = set()
    result = []
    for index, item in enumerate(visuals, 1):
        if not isinstance(item, str):
            raise ValueError(f'Escena {index}: el texto no es una cadena')
        clean = re.sub(r'\s+', ' ', item).strip().strip('"“”')
        words = clean.split()
        if not (VISUAL_MIN_WORDS <= len(words) <= VISUAL_MAX_WORDS):
            raise ValueError(f'Escena {index}: requiere entre 3 y 9 palabras, tiene {len(words)}')
        if len(clean) > VISUAL_MAX_CHARS:
            raise ValueError(f'Escena {index}: supera 52 caracteres; reformular, no truncar')
        if clean.endswith(('...', '…', ':', ',', ';')):
            raise ValueError(f'Escena {index}: mensaje incompleto')
        norm = _visual_normalizado(clean).strip(' .!?¿¡')
        if any(generic in norm for generic in GENERIC_VISUALS):
            raise ValueError(f'Escena {index}: frase generica sin aprendizaje')
        if norm in seen:
            raise ValueError(f'Escena {index}: texto repetido')
        seen.add(norm)
        if not (_palabras_relevantes(clean) & universo):
            raise ValueError(f'Escena {index}: no se identifica relación con el contenido narrado')
        result.append(clean)
    return result


def microfrases(ep):
    """Cinco mensajes completos que expresan conocimiento, no títulos vacíos."""
    return validar_microfrases(
        ep.get('visuals'), ep.get('script', ''), ep.get('title', ''),
        ep.get('fact', ''), ep.get('lesson', ''),
    )


def texto_centrado_seguro(draw, texto, *, centro_y, ancho=560, max_lineas=3):
    """Adapta fuente y saltos sin acortar el mensaje ni cortarlo en pantalla."""
    for tam in range(66, 27, -2):
        fuente = font(tam, True)
        lineas = wrap_text(draw, texto.upper(), fuente, ancho)
        if not lineas or len(lineas) > max_lineas:
            continue
        cajas = [draw.textbbox((0, 0), lin, font=fuente, stroke_width=1) for lin in lineas]
        if any((b[2] - b[0]) > ancho for b in cajas):
            continue
        salto = tam + 17
        alto = len(lineas) * salto
        if alto > 320:
            continue
        y = centro_y - alto // 2
        for linea in lineas:
            caja = draw.textbbox((0, 0), linea, font=fuente, stroke_width=1)
            x = (720 - (caja[2] - caja[0])) / 2
            draw.text((x, y), linea, font=fuente, fill=(255,255,255),
                      stroke_width=1, stroke_fill=(4,7,22))
            y += salto
        return
    raise ValueError('El micromensaje no cabe en la zona segura sin recortes')


OPENROUTER_MODELS_URL = 'https://openrouter.ai/api/v1/models'


def _free_price(value):
    try:
        return float(value) == 0.0
    except (TypeError, ValueError, OverflowError):
        return False


def select_free_json_models(key, count=5):
    """Selecciona modelos de texto gratuitos; response_format es OPCIONAL.

    El listado de parámetros es informativo: el proveedor concreto puede no
    aceptar json_schema, por lo que se utiliza un segundo modo sin restricciones.
    """
    response = requests.get(OPENROUTER_MODELS_URL,
                            headers={'Authorization': f'Bearer {key}'}, timeout=30)
    response.raise_for_status()
    items = response.json().get('data', [])
    candidates = []
    forbidden = ('safety', 'moderation', 'guard', 'omni', 'embedding',
                 'audio', 'speech', 'image', 'reasoning', 'vision-only')
    for item in items:
        mid = item.get('id', '')
        if not isinstance(mid, str) or not mid.endswith(':free'):
            continue
        price = item.get('pricing') or {}
        if not (_free_price(price.get('prompt')) and _free_price(price.get('completion'))):
            continue
        description = (mid + ' ' + str(item.get('name', ''))).lower()
        if any(term in description for term in forbidden):
            continue
        context = item.get('context_length') or 0
        if not isinstance(context, int) or context < 4000:
            continue
        params = item.get('supported_parameters') or []
        can_format = 'response_format' in params
        # Preferir modelos de instrucciones conocidos, no modelos de razonamiento.
        familiar = any(term in description for term in ('instruct', 'chat', 'qwen', 'llama', 'mistral', 'gemma'))
        candidates.append((0 if familiar else 1, 0 if can_format else 1, mid, can_format))
    candidates.sort()
    # La clave de usuario nunca debe habilitar automáticamente un modelo pagado.
    if OPENROUTER_MODEL != 'openrouter/free':
        selected = [x for x in candidates if x[2] == OPENROUTER_MODEL]
        if not selected:
            raise RuntimeError('Modelo configurado sin cuota gratuita de texto: ' + OPENROUTER_MODEL)
        candidates = selected + [x for x in candidates if x[2] != OPENROUTER_MODEL]
    if not candidates:
        raise RuntimeError('No hay modelos gratuitos de texto en el catálogo de OpenRouter.')
    return [(item[2], item[3]) for item in candidates[:count]]


def _normalize_ai_fields(data):
    """Valida contenido, sin inventar ni reconstruir un JSON truncado."""
    if not isinstance(data, dict):
        raise ValueError('La IA no devolvió un objeto JSON')
    # No exigir metadatos que no afectan al relato; reducir tokens de salida.
    if not data.get('fact') and data.get('lesson'):
        data['fact'] = data['lesson']
    if not data.get('lesson') and data.get('fact'):
        data['lesson'] = data['fact']
    for field in ('title', 'script', 'lesson', 'fact'):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError('Falta ' + field)
    words = len(data['script'].split())
    if not 30 <= words <= 60:
        raise ValueError(f'Guion de {words} palabras; requiere entre 30 y 60')
    visuals = data.get('visuals')
    if not isinstance(visuals, list) or len(visuals) != 5 or not all(isinstance(v, str) and v.strip() for v in visuals):
        raise ValueError('Deben existir cinco frases visuales')
    # Rechazar frases genéricas o incompletas; no truncar conceptos.
    data['visuals'] = validar_microfrases(visuals, data['script'], data['title'],
                                          data['fact'], data['lesson'])
    if not isinstance(data.get('sources'), list):
        data['sources'] = []
    return data


def classify_openrouter_429(response):
    """Distingue saturación del proveedor y cuota global sin asumir que todo 429 es global.

    Devuelve 'provider', 'account' o 'unknown'. Nunca imprime credenciales.
    """
    try:
        body = response.json()
    except (ValueError, TypeError):
        body = {}
    error = body.get('error') if isinstance(body, dict) else None
    if not isinstance(error, dict):
        error = {}
    meta = error.get('metadata')
    if not isinstance(meta, dict):
        meta = {}
    details = ' '.join(str(x) for x in (
        error.get('message', ''), meta.get('raw', ''),
        meta.get('provider_name', ''), meta.get('reason', ''),
    )).lower()
    provider_clues = (
        'temporarily rate-limited upstream', 'rate-limited upstream',
        'upstream', 'provider returned error', 'provider rate limit',
        'provider rate-limit', 'provider is rate limited',
    )
    if any(phrase in details for phrase in provider_clues):
        return 'provider'
    account_clues = (
        'free-models-per-day', 'free model requests per day',
        'daily free requests', 'daily limit', 'daily quota',
        'insufficient credits', 'not enough credits',
        'account rate limit', 'your account', 'your quota',
    )
    if any(phrase in details for phrase in account_clues):
        return 'account'
    return 'unknown'


def _parse_compact_response(text):
    """Acepta JSON compacto o seis líneas delimitadas, sin inventar campos."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Respuesta vacía')
    try:
        return _parse_ai_json(text)
    except (ValueError, json.JSONDecodeError):
        pass
    # Formato alternativo; el guion y cada escena ocupan exactamente una línea.
    cleaned = re.sub(r'^```[^\n]*\n|\n```\s*$', '', text.strip())
    fields = {}
    scenes = {}
    for line in cleaned.splitlines():
        hit = re.match(r'^\s*(TITLE|TITULO|SCRIPT|GUION|LESSON|LECCION|FACT|DATO|MENSAJE_[1-5])\s*:\s*(.*?)\s*$', line, re.I)
        if not hit:
            if line.strip():
                raise ValueError('Línea no reconocida fuera del formato delimitado')
            continue
        key, value = hit.group(1).upper(), hit.group(2).strip()
        if not value:
            raise ValueError('Campo sin contenido: ' + key)
        if key.startswith('MENSAJE_'):
            scenes[int(key[-1])] = value
        elif key in ('TITLE', 'TITULO'):
            fields['title'] = value
        elif key in ('SCRIPT', 'GUION'):
            fields['script'] = value
        elif key in ('LESSON', 'LECCION'):
            fields['lesson'] = value
        elif key in ('FACT', 'DATO'):
            fields['fact'] = value
    if len(scenes) != 5:
        raise ValueError('Formato delimitado: faltan micromensajes')
    fields['visuals'] = [scenes[n] for n in range(1, 6)]
    fields['sources'] = []
    return fields


def _free_prompt(ep, mode):
    content = (
        'Tema: ' + str(ep.get('title', ''))[:180] + '. '
        'Categoría: ' + str(ep.get('category', ''))[:90] + '. '
        'Aprendizaje: ' + str(ep.get('lesson', ''))[:210] + '. '
    )
    instruction = (
        'Eres guionista educativo en español. Crea UN guion de 42 a 50 palabras '
        'que explique un hecho concreto sin inventar cifras. Escribe cinco '
        'microfrases de 3 a 9 palabras y máximo 52 caracteres cada una, '
        'específicas y relacionadas con las afirmaciones del guion, no títulos '
        'vacíos. Una idea completa por frase; nada de cortes o puntos suspensivos. '
        'Las cinco frases siguen el relato. Evita consejos médicos o de emergencia '
        'sin corroborar. Salida breve, sin explicaciones ni Markdown. '
    )
    if mode == 'lines':
        instruction += (
            'Emite exactamente estas nueve líneas con estas etiquetas: '
            'TITULO: ...\nGUION: ...\nDATO: ...\nLECCION: ...\n'
            'MENSAJE_1: ...\nMENSAJE_2: ...\nMENSAJE_3: ...\n'
            'MENSAJE_4: ...\nMENSAJE_5: ... . '
            'No agregues otras líneas.'
        )
    else:
        instruction += (
            'Devuelve SOLO JSON compacto con claves title, script, fact, lesson, '
            'visuals (array de cinco cadenas). Sin sources ni campos extra.'
        )
    return instruction + ' ' + content


def _openrouter_text(key, model, prompt, *, max_tokens=2600):
    """Obtiene texto visible sin perder una respuesta útil por finish_reason=length.

    Desactiva el razonamiento cuando lo admite el proveedor: algunos modelos
    gratuitos consumen su presupuesto en tokens internos. Ante 400 por un
    parámetro no soportado, reintenta la MISMA solicitud sin él.
    """
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com',
        'X-Title': 'Dato Wow - DataViral',
    }
    base = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'Español. Entrega únicamente las líneas solicitadas. No expliques ni razones.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.2,
        'max_tokens': max_tokens,
        'stream': False,
    }
    payload = dict(base)
    payload['reasoning'] = {'effort': 'none', 'exclude': True}
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=130)
    # Los modelos gratuitos no comparten todos los parámetros de razonamiento.
    if response.status_code in (400, 422) and any(
        word in response.text.lower() for word in ('reasoning', 'effort', 'unsupported parameter', 'unrecognized')
    ):
        response = requests.post(OPENROUTER_URL, headers=headers, json=base, timeout=130)
    if response.status_code == 429:
        kind = classify_openrouter_429(response)
        if kind == 'account':
            raise RuntimeError('Cuota gratuita de la cuenta OpenRouter agotada')
        raise ValueError(f'HTTP 429 ({kind}): modelo temporalmente saturado')
    if response.status_code in (401, 403):
        raise RuntimeError('OpenRouter rechazó la credencial o el acceso a la API')
    if not response.ok:
        raise ValueError(f'HTTP {response.status_code}: {response.text[:170]}')
    body = response.json()
    choice = (body.get('choices') or [{}])[0]
    finish = choice.get('finish_reason')
    message = choice.get('message') or {}
    content = message.get('content') or ''
    if isinstance(content, list):
        content = ''.join(part.get('text', '') for part in content if isinstance(part, dict))
    if not isinstance(content, str) or not content.strip():
        reason = 'respuesta truncada: el modelo consumió todos los tokens sin texto visible' if finish == 'length' else 'modelo sin texto visible'
        raise ValueError(reason)
    # finish_reason=length no implica automáticamente que el contenido esté
    # incompleto. El analizador de cada etapa es quien valida su integridad.
    return content.strip()


def _parse_narration(raw):
    """Acepta un objeto JSON corto o líneas TITLE/SCRIPT/FACT/LESSON."""
    try:
        obj = _parse_ai_json(raw)
    except (ValueError, json.JSONDecodeError):
        obj = {}
        for line in raw.strip().strip('`').splitlines():
            hit = re.match(r'^\s*(TITULO|TITLE|GUION|SCRIPT|DATO|FACT|LECCION|LESSON)\s*:\s*(.+?)\s*$', line, re.I)
            if hit:
                key = {'TITULO':'title','TITLE':'title','GUION':'script','SCRIPT':'script',
                       'DATO':'fact','FACT':'fact','LECCION':'lesson','LESSON':'lesson'}[hit.group(1).upper()]
                obj[key] = hit.group(2).strip()
    if not isinstance(obj, dict):
        raise ValueError('narración no estructurada')
    for field in ('title','script'):
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            raise ValueError(f'falta {field}')
    obj['fact'] = str(obj.get('fact') or obj.get('lesson') or obj['title']).strip()
    obj['lesson'] = str(obj.get('lesson') or obj.get('fact') or obj['title']).strip()
    words = len(obj['script'].split())
    if not 30 <= words <= 60:
        raise ValueError(f'guion de {words} palabras, se requieren 30-60')
    return obj


def _parse_five_visuals(raw):
    """Extrae cinco mensajes de un array JSON o cinco líneas numeradas."""
    try:
        obj = json.loads(raw.strip())
        if isinstance(obj, list):
            visuals = obj
        elif isinstance(obj, dict):
            visuals = obj.get('visuals') or obj.get('mensajes')
        else:
            visuals = None
        if isinstance(visuals, list):
            return visuals
    except json.JSONDecodeError:
        pass
    found = {}
    for line in raw.splitlines():
        hit = re.match(r'^\s*(?:MENSAJE[_ ]?|ESCENA[_ ]?|[\-]?)\s*([1-5])\s*[.):\-]\s*(.+?)\s*$', line, re.I)
        if hit:
            found[int(hit.group(1))] = hit.group(2).strip().strip('"')
    if len(found) != 5:
        raise ValueError('faltan cinco mensajes visuales')
    return [found[i] for i in range(1,6)]


def _validar_mensaje_individual(frase, narracion):
    """Aplicar límites de escena sin obligar a disponer de cinco mensajes."""
    if not isinstance(frase, str):
        return None
    frase = re.sub(r'\s+', ' ', frase).strip().strip('"“”').strip(' .,:;!?¿¡')
    if not 3 <= len(frase.split()) <= VISUAL_MAX_WORDS or len(frase) > VISUAL_MAX_CHARS:
        return None
    normal = _visual_normalizado(frase)
    if any(generic in normal for generic in GENERIC_VISUALS):
        return None
    universo = _palabras_relevantes(' '.join(str(narracion.get(k, '')) for k in
                                   ('script', 'title', 'fact', 'lesson')))
    if not (_palabras_relevantes(frase) & universo):
        return None
    if not re.search(r'[a-záéíóúñ]', frase, flags=re.I):
        return None
    return frase


def _fragmentos_completos(texto):
    """Conservar solo cláusulas que puedan funcionar solas, sin cortar por longitud."""
    text = re.sub(r'\s+', ' ', str(texto or '')).strip()
    if not text:
        return
    pieces = re.split(r'(?<=[.!?;])\s+|\s*[;:]\s*', text)
    for piece in pieces:
        piece = piece.strip(' \t\n.,;:¡!¿?')
        if piece:
            yield piece
        # Solo separar cláusulas con puntuación explícita, nunca a mitad de palabra.
        for part in re.split(r',\s+(?=(?:pero|aunque|además|sin embargo|por eso|mientras)\b)', piece, flags=re.I):
            part = re.sub(r'^(?:pero|aunque|además|sin embargo|por eso),?\s+', '', part.strip(' ,.;:!?¿¡'), flags=re.I)
            if part and part != piece:
                yield part


def _mensajes_recuperados(narration, respuestas=()):
    """Aprovechar escenas válidas incluso si otras exceden el límite.

    Complementar solo con proposiciones literales del relato, el dato y la
    lección; nunca repetir frases ni inventar información para llegar a cinco.
    """
    seen = set()
    valid = []

    def append_one(texto):
        frase = _validar_mensaje_individual(texto, narration)
        if frase is None:
            return
        norm = _visual_normalizado(frase)
        if norm in seen:
            return
        seen.add(norm)
        valid.append(frase)

    for response in respuestas:
        for frase in response:
            append_one(frase)
            # Recuperar también cláusulas completas de una frase demasiado larga.
            for piece in _fragmentos_completos(frase):
                append_one(piece)
    for field in ('script', 'fact', 'lesson'):
        for piece in _fragmentos_completos(narration.get(field, '')):
            append_one(piece)
    if len(valid) < 5:
        raise ValueError(f'solo se recuperaron {len(valid)} mensajes completos y distintos (requiere 5)')
    return validar_microfrases(valid[:5], narration['script'], narration['title'], narration['fact'], narration['lesson'])


def _completar_mensajes_con_ia(narration, respuestas, models, router_quota_exhausted=False):
    """Recuperación incremental: usa frases válidas y pide SOLO las faltantes.

    Las respuestas nuevas se validan; nunca se aceptan afirmaciones sin relación
    con el guion. El guardarraíl factual definitivo sigue siendo revisión humana.
    """
    pool = [list(x) for x in respuestas]
    attempts = 0
    for provider, model, api_key in models:
        if provider == 'openrouter' and router_quota_exhausted:
            continue
        if attempts >= 8:
            break
        try:
            return _mensajes_recuperados(narration, pool)
        except ValueError:
            pass
        # Selecciona cuántas frases completas existen, sin tomar fragmentos largos.
        acc = []
        for batch in pool:
            acc.extend(batch)
        existing = []
        seen = set()
        for text in acc:
            validated = _validar_mensaje_individual(text, narration)
            if validated and _visual_normalizado(validated) not in seen:
                existing.append(validated)
                seen.add(_visual_normalizado(validated))
        n = max(1, 5 - len(existing))
        prompt = (
            f'Genera EXACTAMENTE {n} frases educativas NUEVAS y DIFERENTES, '
            'cada una con entre 3 y 7 palabras y 45 caracteres como MÁXIMO. '
            'No incluyas introducciones, numeración, citas, ni explicaciones. '
            'Cada frase debe expresar una idea completa y comprobable SOLO en '
            'este guion, sin añadir cifras, causalidades ni hechos nuevos. '
            'Si una frase se pasa de largo, REFORMÚLALA en vez de cortarla. '
            'Una frase por línea. Evita repetir estos mensajes: '
            + json.dumps(existing, ensure_ascii=False) + '\n'
            + 'TÍTULO: ' + narration['title'] + '\n'
            + 'GUION: ' + narration['script'] + '\n'
            + 'DATO: ' + narration['fact'] + '\n'
            + 'ENSEÑANZA: ' + narration['lesson']
        )
        attempts += 1
        try:
            raw = _ai_request(provider, api_key, model, prompt, max_tokens=650)
        except (ValueError, RuntimeError, requests.RequestException) as exc:
            if provider == 'openrouter' and 'Cuota gratuita de la cuenta OpenRouter agotada' in str(exc):
                router_quota_exhausted = True
            print(f'IA complemento {attempts}: {model}: {str(exc)[:130]}', flush=True)
            continue
        lines = []
        for line in raw.splitlines():
            line = re.sub(r'^\s*(?:[-*•]|(?:MENSAJE[_ ]?)?\d{1,2}[.)\-:]?)\s*', '', line).strip(' "“”')
            if line:
                lines.append(line)
        pool.append(lines)
        print(f'IA complemento {attempts}: {model} devolvió {len(lines)} posibles frases', flush=True)
    return _mensajes_recuperados(narration, pool)


def _mensajes_locales_desde_guion(narration):
    return _mensajes_recuperados(narration)


def _mensajes_parciales_respuesta(raw):
    """Recuperar propuestas 1–5 aunque alguna esté mal formada o sea larga."""
    try:
        arr = _parse_five_visuals(raw)
        return [item for item in arr if isinstance(item, str)]
    except (ValueError, TypeError, KeyError):
        pass
    pieces = []
    for line in str(raw or '').splitlines():
        match = re.match(r'^\s*(?:MENSAJE[_ ]?|ESCENA[_ ]?|[-*]\s*)\s*([1-5])\s*[.):-]\s*(.+?)\s*$', line, re.I)
        if match:
            pieces.append(match.group(2).strip().strip('"“”'))
    return pieces


# Descubrir modelos desde la API de Gemini, en vez de asumir IDs disponibles.
GEMINI_API_ROOT = 'https://generativelanguage.googleapis.com/v1beta/models/'


def _discover_gemini_models(key):
    """Selecciona únicamente modelos que la clave actual puede usar para generateContent."""
    discovered = []
    token = None
    for _ in range(6):
        params = {'pageSize': 100}
        if token:
            params['pageToken'] = token
        response = requests.get(
            'https://generativelanguage.googleapis.com/v1beta/models',
            headers={'x-goog-api-key': key}, params=params, timeout=35,
        )
        if not response.ok:
            raise RuntimeError(f'Gemini models.list HTTP {response.status_code}; verificar clave y API habilitada')
        obj = response.json()
        for row in obj.get('models', []):
            mid = str(row.get('name', '')).removeprefix('models/')
            methods = row.get('supportedGenerationMethods') or []
            if ('generateContent' in methods and mid.startswith('gemini-')
                    and not any(x in mid.lower() for x in ('image','audio','tts','embedding','live','robotics'))):
                discovered.append(mid)
        token = obj.get('nextPageToken')
        if not token:
            break
    # Preferir variantes Flash-Lite y Flash; no activar modelos Pro por defecto.
    preferred = [m for m in discovered if 'flash-lite' in m.lower() and 'preview' not in m.lower()]
    preferred += [m for m in discovered if 'flash' in m.lower() and 'lite' not in m.lower() and 'preview' not in m.lower()]
    preferred += [m for m in discovered if 'flash' in m.lower() and m not in preferred]
    requested = [x.strip().removeprefix('models/') for x in os.getenv('GEMINI_MODEL', '').split(',') if x.strip()]
    chosen = [m for m in requested if m in discovered]
    chosen += [m for m in preferred if m not in chosen]
    models = list(dict.fromkeys(chosen))[:5]
    print('Gemini: modelos habilitados para generateContent: ' + (', '.join(models) or 'ninguno'), flush=True)
    if not models:
        raise RuntimeError('Gemini no muestra modelos Flash accesibles para esta clave')
    return models


def _gemini_text(key, model, prompt, *, max_tokens=1500):
    url = GEMINI_API_ROOT + urllib.parse.quote(model, safe='') + ':generateContent'
    response = requests.post(
        url,
        headers={'x-goog-api-key': key, 'Content-Type': 'application/json'},
        json={'contents': [{'parts': [{'text': prompt}]}],
              'generationConfig': {'maxOutputTokens': min(max_tokens, 2048), 'temperature': 0.2}},
        timeout=110,
    )
    if not response.ok:
        try:
            err = response.json().get('error') or {}
            detail = re.sub(r'\s+', ' ', str(err.get('message', '')))[:210]
        except (ValueError, TypeError, AttributeError):
            detail = ''
        raise ValueError(f'Gemini {model}: HTTP {response.status_code}; {detail}')
    data = response.json()
    choices = data.get('candidates') or []
    parts = ((choices[0].get('content') or {}).get('parts') or []) if choices else []
    result = ''.join(str(p.get('text', '')) for p in parts if isinstance(p, dict)).strip()
    if not result:
        raise ValueError('Gemini no devolvió texto visible')
    return result


def _ai_model_candidates():
    candidates = []
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    if gemini_key:
        try:
            candidates.extend(('gemini', model, gemini_key)
                              for model in _discover_gemini_models(gemini_key))
        except (requests.RequestException, RuntimeError, ValueError) as exc:
            print(f'Gemini: descubrimiento fallido: {str(exc)[:220]}', flush=True)
    router_key = os.getenv('OPENROUTER_API_KEY', '').strip()
    if router_key:
        try:
            candidates.extend(('openrouter', model, router_key)
                              for model, _ in select_free_json_models(router_key, 7))
        except (requests.RequestException, ValueError, RuntimeError) as exc:
            print(f'OpenRouter: catálogo gratuito no disponible: {type(exc).__name__}', flush=True)
    if not candidates:
        raise RuntimeError('Ningún modelo disponible: revisar acceso de Gemini o cuota de OpenRouter.')
    print('Modelos candidatos: ' + ', '.join(f'{p}:{m}' for p,m,_ in candidates), flush=True)
    return candidates


def _ai_request(provider, key, model, prompt, max_tokens):
    if provider == 'gemini':
        return _gemini_text(key, model, prompt, max_tokens=max_tokens)
    return _openrouter_text(key, model, prompt, max_tokens=max_tokens)


def create_ai_episode(ep):
    """Dos etapas cortas: narración, después cinco mensajes visuales.

    Evita pedir un gran JSON. Solo usa modelos con prompt/completion gratuitos;
    si alguno falla por saturación o salida truncada prueba el siguiente.
    """
    candidates = _ai_model_candidates()
    router_quota_exhausted = False
    intro = (
        f"Tema: {str(ep.get('title', ''))[:140]}. "
        f"Categoría: {str(ep.get('category', ''))[:70]}. "
        f"Enseñanza deseada: {str(ep.get('lesson', ''))[:160]}."
    )
    narration_prompt = (
        'Redacta un guion educativo sorprendente y preciso, IDEALMENTE 42 A 50 PALABRAS '
        'en español para narrar en 20 segundos. Abre con un gancho factual de 5 a 10 palabras, ' 
        'que despierte una pregunta o contradiga una intuición, sin sensacionalismo. Escribe de cuatro a seis oraciones completas con ideas concretas; deben avanzar de causa a conclusión y ser comprensibles ' 
        'por sí solas. Sin cifras inventadas, sin introducciones vacías, '
        'sin consejos médicos o de emergencia no verificados, ni promesas exageradas. Cierra con un aprendizaje claro y memorable. Responde SOLO cuatro líneas, '
        'sin Markdown: TITULO: ...\nGUION: ...\nDATO: ...\nLECCION: ...\n' + intro
    )
    narration = None
    narration_model = None
    last_problem = 'sin respuesta'
    for provider, model, api_key in candidates:
        if provider == 'openrouter' and router_quota_exhausted:
            continue
        try:
            raw = _ai_request(provider, api_key, model, narration_prompt, max_tokens=1800)
            narration = _parse_narration(raw)
            narration_model = f'{provider}:{model}'
            print(f'Narración validada con {provider}:{model}', flush=True)
            break
        except (RuntimeError, ValueError, requests.RequestException, KeyError, TypeError) as exc:
            if provider == 'openrouter' and 'Cuota gratuita de la cuenta OpenRouter agotada' in str(exc):
                router_quota_exhausted = True
                print('OpenRouter: cuota de cuenta agotada; se omiten sus modelos', flush=True)
            last_problem = f'{provider}/{model}: {str(exc)[:140]}'
            print(f'IA etapa 1: {last_problem}', flush=True)
    if narration is None:
        raise RuntimeError('Ningún modelo gratuito generó narración válida. '
                           f'Último diagnóstico: {last_problem}. No se publicó nada.')

    # No volver a generar el guion cuando fallan los mensajes visuales.
    visuals_prompt = (
        'Basándote ÚNICAMENTE en el guion siguiente, escribe cinco frases educativas '
        'completas para cinco escenas consecutivas. Cada una entre 3 y 9 palabras, '
        'máximo 52 caracteres, sin títulos vacíos, sin puntos suspensivos, sin introducir '
        'hechos ajenos al guion. MENSAJE_1 debe ser un gancho concreto y fiel al guion; MENSAJE_5 debe cerrar el aprendizaje sin inventar nada. Deben explicar cinco aspectos o consecuencias distintas. '
        'Responde SOLO estas cinco líneas, sin Markdown ni explicaciones: '
        'MENSAJE_1: ...\nMENSAJE_2: ...\nMENSAJE_3: ...\nMENSAJE_4: ...\nMENSAJE_5: ...\n'
        f"TITULO: {narration['title']}\nGUION: {narration['script']}\n"
        f"DATO: {narration['fact']}\nLECCION: {narration['lesson']}"
    )
    visuals = None
    visual_model = None
    respuestas_parciales = []
    # Antes de otra solicitud, no hay parámetro costoso de razonamiento forzado:
    # muchos proveedores gratuitos no lo admiten; los prompts cortos reducen consumo.
    # El modelo que completó bien la narración recibe la primera oportunidad.
    visual_candidates = sorted(candidates, key=lambda row: f'{row[0]}:{row[1]}' != narration_model)
    for provider, model, api_key in visual_candidates:
        if provider == 'openrouter' and router_quota_exhausted:
            continue
        try:
            raw = _ai_request(provider, api_key, model, visuals_prompt, max_tokens=1300)
            respuestas_parciales.append(_mensajes_parciales_respuesta(raw))
            proposed = _parse_five_visuals(raw)
            visuals = validar_microfrases(proposed, narration['script'],
                                           narration['title'], narration['fact'], narration['lesson'])
            visual_model = f'{provider}:{model}'
            print(f'Cinco mensajes validados con {provider}:{model}', flush=True)
            break
        except (RuntimeError, ValueError, requests.RequestException, KeyError, TypeError) as exc:
            if provider == 'openrouter' and 'Cuota gratuita de la cuenta OpenRouter agotada' in str(exc):
                router_quota_exhausted = True
                print('OpenRouter: cuota de cuenta agotada; se omiten sus modelos', flush=True)
            last_problem = f'{provider}/{model}: {str(exc)[:140]}'
            print(f'IA etapa 2: {last_problem}', flush=True)
    if visuals is None:
        # Evitar fallar por una segunda llamada cuando el propio guion
        # contiene cinco proposiciones breves. Nunca inventar información.
        try:
            visuals = _mensajes_recuperados(narration, respuestas_parciales)
            visual_model = 'recuperacion-mixta'
            print('Cinco mensajes recuperados de propuestas de IA y del guion (sin inventar datos)', flush=True)
        except ValueError as exc:
            print(f'Recuperación inicial insuficiente ({exc}); intentando completar solo mensajes faltantes', flush=True)
            try:
                visuals = _completar_mensajes_con_ia(
                    narration, respuestas_parciales, visual_candidates,
                    router_quota_exhausted=router_quota_exhausted
                )
                visual_model = 'recuperacion-incremental'
                print('Cinco mensajes recuperados y validados mediante complemento incremental', flush=True)
            except ValueError as final_exc:
                raise RuntimeError(
                    'Narración válida, pero no se obtuvieron cinco mensajes seguros. '
                    f'OpenRouter: {last_problem}. Recuperación: {final_exc}. '
                    'No se publicó nada.'
                ) from final_exc

    result = dict(ep)
    result.update(
        title=narration['title'], script=narration['script'],
        fact=narration['fact'], lesson=narration['lesson'],
        visuals=visuals, visual_title=visuals[0], visual_lesson=visuals[-1],
        source='', suggested_sources=[], ai_model=narration_model,
        visual_ai_model=visual_model, generated_at=now(), verified=False,
        verification_note='Contenido generado con IA, no verificado independientemente',
    )
    print(f"Guion IA creado: {ep['id']}; textos cortos: 5; fuentes propuestas: ninguna", flush=True)
    return result

def select_episode(episodes, gh=None, requested=None):
    """Selecciona un episodio pendiente con variedad de categorias y azar real.

    - Un ID explicito respeta la eleccion manual (publish() aplica antidualidad).
    - El historial remoto impide reutilizar publicaciones o envios inciertos.
    - Entre categorias con episodios disponibles, prioriza las menos publicadas;
      entre empates evita la ultima categoria usada, si existe alternativa.
    - Sortea tanto la categoria como el episodio usando SystemRandom.
    No altera el schema ni la ubicacion del estado previo.
    """
    if requested:
        return next((e for e in episodes if e['id'] == requested), None)

    states = {}
    if gh is not None:
        raw, _ = gh.read('dataviral/state.json')
        if raw is not None:
            document = json.loads(raw)
            if not isinstance(document, dict) or not isinstance(document.get('episodes'), dict):
                raise RuntimeError('Estado remoto de DataViral invalido; no se seleccionara episodio')
            states = document['episodes']

    blocked = {'publicado', 'enviando', 'incierto'}
    by_category = {}
    published_counts = {}
    recent = []
    for ep in episodes:
        category = ep['category']
        row = states.get(ep['id'], {})
        if not isinstance(row, dict):
            raise RuntimeError('Registro de estado invalido para ' + ep['id'])
        statuses = [row.get(field) for field in ('reel', 'foto', 'feed_video', 'story')]
        if any(status in blocked for status in statuses):
            if 'publicado' in statuses:
                published_counts[category] = published_counts.get(category, 0) + 1
                if row.get('updated_at'):
                    recent.append((str(row['updated_at']), category))
            continue
        by_category.setdefault(category, []).append(ep)
        published_counts.setdefault(category, 0)

    if not by_category:
        raise RuntimeError('Los 500 episodios ya estan publicados o bloqueados por incertidumbre')

    # Equilibrio entre categorias; no completar cien episodios de una sola.
    minimum = min(published_counts[category] for category in by_category)
    eligible_categories = [category for category in by_category
                           if published_counts[category] == minimum]
    if recent and len(eligible_categories) > 1:
        last_category = max(recent, key=lambda pair: pair[0])[1]
        others = [category for category in eligible_categories if category != last_category]
        if others:
            eligible_categories = others

    rng = random.SystemRandom()
    chosen_category = rng.choice(eligible_categories)
    selected = rng.choice(by_category[chosen_category])
    print(f'Episodio aleatorio equilibrado: {selected["id"]} | '
          f'categoria: {chosen_category} | '
          f'publicados de esa categoria: {published_counts[chosen_category]}', flush=True)
    return selected


def now():
    return datetime.now(timezone.utc).isoformat()


def font(size, bold=False):
    filenames = (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                  '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'] if bold else
                 ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                  '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'])
    for filename in filenames:
        if Path(filename).exists():
            return ImageFont.truetype(filename, size)
    return ImageFont.load_default()


def wrap_text(draw, text, text_font, width):
    words = text.split()
    result, current = [], ''
    for word in words:
        trial = f'{current} {word}'.strip()
        if draw.textbbox((0, 0), trial, font=text_font)[2] <= width:
            current = trial
        else:
            if current:
                result.append(current)
            current = word
    if current:
        result.append(current)
    return result


def palette(i):
    return [(12, 12, 32), (9, 23, 38), (27, 15, 28), (14, 26, 25), (20, 17, 45)][i % 5], [
        (186, 93, 253), (39, 217, 241), (255, 193, 92), (69, 231, 169), (252, 105, 174)
    ][i % 5]


# Fotografía única: solo CC0 o dominio público y sin texto visible.
# Para aceptar fotografías, el runner requiere Tesseract OCR:
# sudo apt-get install -y tesseract-ocr
# Si no está disponible, se detiene el video antes de publicar.
import shutil
import unicodedata
import ipaddress
import socket
from PIL import ImageOps, ImageEnhance, ImageFilter

PHOTO_HEADERS = {
    'User-Agent': 'DatoWowEducationalBot/1.5 (https://github.com/acesped/dataviral)',
    'Accept': 'application/json, image/jpeg, image/png, image/webp',
}
PHOTO_REJECT_METADATA = (
    'poster', 'infographic', 'infografia', 'diagram', 'diagrama',
    'chart', 'grafic', 'screenshot', 'captura', 'meme', 'banner',
    'advertisement', 'publicidad', 'logo', 'watermark', 'marca de agua',
    'typography', 'tipografia', 'text overlay', 'book cover',
    'portada', 'signage', 'letrero', 'labelled', 'labeled',
    'etiquetad', 'newspaper', 'periódico', 'periodico', 'mapa politico',
)
PHOTO_STOP = {
    'esto','esta','este','para','porque','como','cuando','desde','sobre','entre',
    'donde','tiene','puede','pueden','muchos','nuestra','nuestro','datos',
    'dato','sabias','sabías','están','estan','segun','según','algunas',
    'algunos','tambien','también','unos','unas','sino','pero','cada',
    'todo','todos','ellas','ellos','del','las','los','con','una','que',
}
PHOTO_MIN_SCORE = int(os.getenv('DV_IMAGE_MIN_SCORE', '7'))
PHOTO_MAX_QUERIES = int(os.getenv('DV_IMAGE_MAX_QUERIES', '10'))


def _photo_words(value):
    value = unicodedata.normalize('NFKD', str(value or '').lower())
    value = ''.join(x for x in value if not unicodedata.combining(x))
    return [x for x in re.findall(r'[a-z0-9]{4,}', value)
            if x not in PHOTO_STOP]


# Asociaciones de conceptos concretos con objetos fotografiables; no se usan
# pistas genéricas de categoría para elegir fondos irrelevantes.
PHOTO_CONCEPTS = {
    'huella digital': 'fingerprint closeup', 'firma invisible': 'laptop browser fingerprinting',
    'navegador': 'laptop web browser', 'internet': 'laptop internet router',
    'privacidad': 'laptop privacy cybersecurity', 'contraseña': 'computer keyboard password',
    'cerebro': 'human brain model', 'memoria': 'human brain model',
    'atención': 'person concentrating', 'emociones': 'human facial expression',
    'ansiedad': 'anxious human portrait', 'sueño': 'sleeping person',
    'abejas': 'honeybee on flower', 'volcán': 'volcano eruption',
    'océano': 'ocean water', 'pulpo': 'octopus underwater',
    'satélite': 'satellite orbit earth', 'luna': 'moon surface',
    'bacterias': 'bacteria microscope', 'corazón': 'human heart anatomy model',
}
PHOTO_QUERY_STOP = set('photo photograph photography images image picture stock high resolution realistic creative beautiful background vertical'.split())


# Consultas fotografiables, no etiquetas editoriales abstractas.
PHOTO_PHYSICAL_SCENES = {
    'expedicion': ['scientific expedition', 'explorers mountains', 'researchers fieldwork'],
    'exploracion': ['explorers landscape', 'research expedition'],
    'aventura': ['explorers mountains', 'hiking expedition'],
    'navegador': ['laptop computer', 'computer keyboard'],
    'huella digital': ['fingerprint', 'laptop computer'],
    'firma invisible': ['laptop computer', 'computer mouse'],
    'privacidad': ['laptop computer', 'closed laptop'],
    'dinero': ['coins money', 'banknotes'],
    'memoria': ['human brain model', 'person reading book'],
    'psicologia': ['human facial expression', 'person thinking'],
    'atencion': ['person reading book', 'person concentrating'],
    'cerebro': ['human brain model'],
    'volcan': ['volcano landscape'],
    'abejas': ['bee flower'],
    'oceano': ['ocean waves'],
    'satellite': ['satellite space'],
    'satelite': ['satellite space'],
    'historia': ['historical artifact'],
}


def _visual_query_ai(ep):
    """Gemini propone sujetos fotografiables, no conceptos abstractos.

    No depende de OpenRouter (que puede estar sin cuota). La salida se limita
    a consultas cortas y se valida antes de consultar buscadores de imágenes.
    """
    if os.getenv('DV_DISABLE_VISUAL_AI', '').lower() in ('1', 'true', 'yes'):
        return []
    key = os.getenv('GEMINI_API_KEY', '').strip()
    if not key:
        print('FOTO: Gemini no configurado; se usarán consultas locales', flush=True)
        return []
    prompt = (
        'Eres un documentalista que busca fotografías CC0. A partir del tema '
        'y guion en español, responde SOLO un JSON válido como '
        '{"queries":["english object or activity","second photo subject",'
        '"third photo subject"]}. Cada consulta EN INGLÉS con 2 a 4 '
        'palabras y sustantivos físicos fotografiables. Deben representar '
        'el fenómeno CONCRETO explicado, no su categoría ni una metáfora. '
        'Evita pantallas con letras, carteles, logos, diagramas e infografías. '
        'Ejemplo: si el tema es comparar ejercicios de fuerza y resistencia, '
        'usa "person lifting weights", "runner training outdoors", '
        '"athlete exercising gym"; nunca "training versus". '
        f"Tema: {str(ep.get('title',''))[:140]}\n"
        f"Guion: {str(ep.get('script',''))[:600]}\n"
        f"Dato: {str(ep.get('fact',''))[:150]}"
    )
    # El alias -latest se comprobó en ejecuciones previas, pero el modelo puede cambiar.
    preferred = ['gemini-flash-lite-latest', 'gemini-3.1-flash-lite', 'gemini-3.5-flash-lite']
    configured = [x.strip() for x in os.getenv('DV_IMAGE_GEMINI_MODELS','').split(',') if x.strip()]
    for model in list(dict.fromkeys(configured + preferred)):
        try:
            raw = _gemini_text(key, model, prompt, max_tokens=400)
            obj = _parse_ai_json(raw)
            lines = obj.get('queries') or []
            if not isinstance(lines, list):
                raise ValueError('queries no es lista')
            valid = []
            for q in lines:
                if not isinstance(q, str):
                    continue
                q = re.sub(r'\s+', ' ', q).strip(' .,!?:;')
                if (2 <= len(q.split()) <= 5 and len(q) <= 70
                        and re.fullmatch(r'[A-Za-z0-9 -]+', q)
                        and not any(w.lower() in PHOTO_QUERY_STOP for w in q.split())):
                    valid.append(q)
            if valid:
                print(f'FOTO: Gemini sugirió {valid!r}', flush=True)
                return valid[:4]
        except (ValueError, RuntimeError, requests.RequestException) as exc:
            print(f'FOTO: Gemini {model} no pudo proponer consultas: {str(exc)[:130]}', flush=True)
    return []


def _photo_queries(ep):
    """Varias consultas concretas, primero IA Gemini y después sujetos locales."""
    manual = str(ep.get('image_query') or '').strip()
    title = str(ep.get('title') or '')
    narrative = ' '.join(str(ep.get(k) or '') for k in ('title', 'script', 'fact', 'lesson'))
    normalized = unicodedata.normalize('NFKD', narrative.lower())
    normalized = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    queries = []
    if manual:
        queries.append(manual)
    queries.extend(_visual_query_ai(ep))
    for concept, examples in PHOTO_PHYSICAL_SCENES.items():
        if re.search(r'(?<![a-z])' + re.escape(concept) + r'(?![a-z])', normalized):
            queries.extend(examples)
    # Respaldo específico para temas que antes daban «entrenamiento versus».
    if any(word in normalized for word in ('entrenamiento', 'entrenar', 'ejercicio', 'fuerza', 'resistencia')):
        if any(word in normalized for word in ('dinero', 'finanzas', 'inversion', 'mercado', 'econom')):
            queries.extend(['financial analyst laptop', 'person using calculator'])
        else:
            queries.extend(['athlete exercising gym', 'person lifting weights', 'runner training outdoors'])
    if any(word in normalized for word in ('expedicion', 'exploracion', 'explorador')):
        queries.extend(['scientific expedition outdoors', 'explorers mountains'])
    # No usar por defecto fragmentos abstractos del título como «X versus».
    unique, seen = [], set()
    for q in queries:
        q = re.sub(r'\s+', ' ', str(q or '')).strip()[:80]
        if q and q.casefold() not in seen:
            unique.append(q)
            seen.add(q.casefold())
    if not unique:
        raise RuntimeError('FOTO: no se obtuvo un sujeto físico concreto para el tema; no se usará una foto genérica.')
    return unique[:max(3, min(12, PHOTO_MAX_QUERIES))]


def _photo_get(url, *, params=None, stream=False):
    for retry in range(2):
        response = requests.get(url, params=params, headers=PHOTO_HEADERS,
                                timeout=(10, 22), stream=stream)
        if response.status_code in (429, 502, 503, 504) and retry == 0:
            response.close()
            time.sleep(2)
            continue
        response.raise_for_status()
        return response
    raise RuntimeError('Proveedor de imágenes sin respuesta')


def _photo_html(value):
    import html as _html
    return _html.unescape(re.sub(r'<[^>]*>', ' ', str(value or '')))


def _commons_photos(query):
    params = dict(action='query', format='json', generator='search',
                  gsrsearch=query + ' filetype:bitmap', gsrnamespace=6,
                  gsrlimit=16, prop='imageinfo', iiprop='url|extmetadata',
                  iiurlwidth=1000)
    with _photo_get('https://commons.wikimedia.org/w/api.php', params=params) as response:
        pages = (response.json().get('query') or {}).get('pages') or {}
    for page in pages.values():
        info = (page.get('imageinfo') or [{}])[0]
        metadata = info.get('extmetadata') or {}
        license_name = _photo_html((metadata.get('LicenseShortName') or {}).get('value')).lower().replace(' ', '')
        # Evitar material CC-BY/SA: elegir exclusivamente CC0 o PD marcadas.
        permitted = ('cc0' in license_name or 'publicdomain' in license_name
                     or license_name in ('pd', 'pdm') or license_name.startswith('pd-'))
        if not permitted or any(x in license_name for x in ('cc-by', '-nc', '-nd')):
            continue
        url = info.get('thumburl') or info.get('url')
        if url:
            yield dict(url=url, title=page.get('title', ''),
                       description=_photo_html((metadata.get('ImageDescription') or {}).get('value'))[:400],
                       source=info.get('descriptionurl', ''), license=license_name,
                       provider='Wikimedia Commons')


def _openverse_photos(query):
    with _photo_get('https://api.openverse.org/v1/images/',
                    params=dict(q=query, license='cc0,pdm', page_size=16)) as response:
        results = response.json().get('results') or []
    for item in results:
        if str(item.get('license') or '').lower() not in ('cc0', 'pdm'):
            continue
        url = item.get('url') or item.get('thumbnail')
        if url:
            yield dict(url=url, title=item.get('title') or '',
                       description=item.get('description') or '',
                       source=item.get('foreign_landing_url') or '',
                       license=item.get('license'), provider='Openverse')


def _photo_score(item, ep, query_index):
    """No aceptar fotos sólo por pertenecer al resultado de una búsqueda.

    Wikimedia y Openverse pueden devolver imágenes irrelevantes; el título y la
    descripción deben coincidir con los términos concretos de la consulta.
    """
    meta = ' '.join(str(item.get(x) or '') for x in ('title', 'description'))
    normalized = unicodedata.normalize('NFKD', meta.lower())
    normalized = ''.join(x for x in normalized if not unicodedata.combining(x))
    if any(re.search(r'(?<![a-z])' + re.escape(term) + r'(?![a-z])', normalized)
           for term in PHOTO_REJECT_METADATA):
        return -1
    subject_query = item.get('_matched_query', '')
    qwords = set(_photo_words(subject_query)) - PHOTO_QUERY_STOP
    # Eliminar términos genéricos de búsqueda y pedir evidencia explícita.
    ignored = {'human', 'person', 'people', 'natural', 'nature', 'science',
               'technology', 'computer', 'close', 'closeup', 'background',
               'woman', 'man', 'young', 'digital', 'electronic'}
    focused = qwords - ignored
    matches = set(_photo_words(meta)) & (focused if focused else qwords)
    if not matches:
        return -1
    return 30 * len(matches) + 4 * len(set(_photo_words(meta)) & qwords) - query_index * 3


def _photo_has_text(path):
    """Descarta fotografías con palabras detectadas; nunca certifica ausencia total.

    La confianza de OCR aislado se verifica en dos modos para disminuir ruido.
    """
    exe = shutil.which('tesseract')
    if not exe:
        print('FOTO RECHAZADA: falta tesseract-ocr. Instalar con apt-get en Actions.', flush=True)
        return True
    try:
        import csv
        for psm in ('11', '6'):
            res = subprocess.run([exe, str(path), 'stdout', '--psm', psm, 'tsv'],
                                 capture_output=True, text=True, timeout=22, check=True)
            for row in csv.DictReader(io.StringIO(res.stdout), delimiter='\t'):
                token = (row.get('text') or '').strip()
                try:
                    confidence = float(row.get('conf', '-1'))
                except ValueError:
                    continue
                letters = re.sub(r'[^A-Za-zÀ-ÿ0-9]', '', token)
                if confidence >= 75 and len(letters) >= 3:
                    print(f'FOTO RECHAZADA: texto detectado (OCR, modo {psm})', flush=True)
                    return True
    except (OSError, subprocess.SubprocessError, ValueError):
        print('FOTO RECHAZADA: error al comprobar texto mediante OCR', flush=True)
        return True
    return False


def _public_photo_url(url):
    """Bloquea URLs no HTTPS, credenciales, puertos raros y direcciones internas.

    Openverse devuelve fotos alojadas en muchos dominios legítimos. La antigua
    lista cerrada descartaba casi todas las imágenes sin siquiera descargarlas.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        return False
    try:
        if parsed.port not in (None, 443):
            return False
    except ValueError:
        return False
    host = parsed.hostname.lower().rstrip('.')
    if host == 'localhost' or host.endswith(('.local', '.internal', '.localhost')):
        return False
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        if not addresses:
            return False
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return False
    except (OSError, ValueError):
        return False
    return True


def _download_photo(url, target):
    """Descarga fotos de dominios HTTPS públicos, incluidos los de Openverse.

    Valida cada redirección. Mantiene el límite de 10 MB y el filtro OCR.
    """
    try:
        if not _public_photo_url(url):
            print('FOTO DESCARTADA: URL no pública o dominio no resoluble', flush=True)
            return False
        current = url
        for _ in range(6):
            with requests.get(current, headers=PHOTO_HEADERS,
                              timeout=(10, 28), stream=True,
                              allow_redirects=False) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get('Location', '')
                    next_url = urllib.parse.urljoin(current, location)
                    if not location or not _public_photo_url(next_url):
                        print('FOTO DESCARTADA: redirección insegura', flush=True)
                        return False
                    current = next_url
                    continue
                response.raise_for_status()
                mime = response.headers.get('Content-Type', '').lower()
                if not any(kind in mime for kind in ('image/jpeg', 'image/png', 'image/webp')):
                    print(f'FOTO DESCARTADA: tipo MIME {mime[:55]}', flush=True)
                    return False
                payload = bytearray()
                for chunk in response.iter_content(65536):
                    if chunk:
                        payload.extend(chunk)
                    if len(payload) > 10_000_000:
                        print('FOTO DESCARTADA: tamaño superior a 10 MB', flush=True)
                        return False
                with Image.open(io.BytesIO(payload)) as image:
                    if image.width < 480 or image.height < 360:
                        print('FOTO DESCARTADA: resolución insuficiente', flush=True)
                        return False
                    image = ImageOps.exif_transpose(image).convert('RGB')
                    image.thumbnail((1600, 1600))
                    image.save(target, 'JPEG', quality=89)
                if _photo_has_text(target):
                    target.unlink(missing_ok=True)
                    return False
                return True
        print('FOTO DESCARTADA: demasiadas redirecciones', flush=True)
    except Exception as exc:
        print(f'FOTO DESCARTADA: {type(exc).__name__}: {str(exc)[:180]}', flush=True)
    target.unlink(missing_ok=True)
    return False


def prepare_photo(ep, folder):
    """Selecciona una sola foto aprobada para las cinco escenas."""
    queries = _photo_queries(ep)
    print(f'FOTO: búsquedas del episodio {ep["id"]}: {queries}', flush=True)
    if not shutil.which('tesseract'):
        raise RuntimeError('No está instalado tesseract-ocr. Instálalo en GitHub Actions para habilitar fotografías sin texto.')
    candidates, seen = [], set()
    stats = {'resultados': 0, 'metadatos_rechazados': 0,
             'descargas_fallidas_o_texto': 0, 'proveedores_fallidos': 0}
    for qindex, query in enumerate(queries):
        for provider in (_commons_photos, _openverse_photos):
            try:
                count = 0
                for item in provider(query):
                    count += 1
                    if item['url'] in seen:
                        continue
                    seen.add(item['url'])
                    item['_matched_query'] = query
                    score = _photo_score(item, ep, qindex)
                    if score >= 0:
                        candidates.append((score, item))
                    else:
                        stats['metadatos_rechazados'] += 1
                stats['resultados'] += count
                print(f'FOTO: {provider.__name__}: {count} resultados para {query!r}', flush=True)
            except (requests.RequestException, ValueError, KeyError) as exc:
                stats['proveedores_fallidos'] += 1
                print(f'FOTO: error {provider.__name__}: {type(exc).__name__}: {str(exc)[:130]}', flush=True)
    candidates.sort(key=lambda x: x[0], reverse=True)
    chosen = folder / 'foto_principal.jpg'
    chosen.unlink(missing_ok=True)
    credits = []
    print(f'FOTO: {len(candidates)} candidatas aptas por metadatos; OCR={bool(shutil.which("tesseract"))}', flush=True)
    for score, item in candidates[:20]:
        if _download_photo(item['url'], chosen):
            credits = [dict(item, relevance_score=score, text_check='tesseract_no_text_detected')]
            break
        stats['descargas_fallidas_o_texto'] += 1
    (folder / 'creditos_imagenes.json').write_text(
        json.dumps(credits, ensure_ascii=False, indent=2), encoding='utf-8')
    if credits:
        print(f'FOTO SELECCIONADA: {credits[0]["title"][:100]} ({credits[0]["provider"]}) | consulta={credits[0].get("_matched_query")!r}', flush=True)
        return chosen, credits
    raise RuntimeError(
        'No se encontró una fotografía apta para este episodio. '
        f'Diagnóstico: {stats}; candidatas={len(candidates)}. '
        'Se cancela el video para evitar publicar fondos de colores sin foto. '
        'Consulta los mensajes FOTO DESCARTADA y FOTO: error anteriores.'
    )


def scene(ep, number, dest, photo=None):
    W, H = 720, 1280
    bg, accent = palette(number + int(ep['id'][-3:]))
    if photo is None or not Path(photo).is_file():
        raise RuntimeError('No hay fotografía de fondo: se prohíbe crear escenas con fondos planos.')
    # Una misma fotografía real, sin texto detectado previamente por OCR,
    # permanece durante las cinco escenas. Se muestra siempre en blanco y negro.
    with Image.open(photo) as source:
        source = ImageOps.exif_transpose(source)
        img = ImageOps.fit(source.convert('RGB'), (W, H), method=Image.Resampling.LANCZOS)
    img = ImageOps.grayscale(img)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Brightness(img).enhance(0.55)
    img = img.convert('RGB')
    d = ImageDraw.Draw(img, 'RGBA')
    # Película negra sutil: aumenta el contraste sin ocultar el tema de la foto.
    d.rectangle((0, 0, W, H), fill=(0, 0, 0, 45))
    # Sin círculos decorativos: la imagen fotográfica permanece limpia.
    d.rounded_rectangle((52, 72, 668, 152), 24, fill=(255, 255, 255, 18), outline=(*accent, 200), width=3)
    d.text((77, 91), 'DATO_WOW', font=font(33, True), fill=(255, 255, 255))
    d.text((55, 187), ep['category'].upper(), font=font(19, True), fill=accent)
    # Franja oscura garantiza el contraste del texto educativo.
    d.rounded_rectangle((45, 420, 675, 835), 24, fill=(4, 7, 22, 160))
    titulares = microfrases(ep)
    texto_centrado_seguro(d, titulares[number], centro_y=610, ancho=560, max_lineas=3)
    d.line((58, 1128, 662, 1128), fill=accent, width=5)
    d.text((92, 1154), 'dato wow - conocimiento en 20 segundos', font=font(23, True), fill='white')
    img.save(dest, quality=92)

def ambient(path: Path, seconds=20):
    rate = 16000
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        import array
        buff = array.array('h')
        for i in range(rate*seconds):
            t = i/rate
            f = min(1., t/.8, (seconds-t)/1.3)
            v = (math.sin(2*math.pi*110*t)*.17 + math.sin(2*math.pi*164.81*t)*.07 +
                 math.sin(2*math.pi*220*t)*.05)
            buff.append(int(32767*max(0,f)*v))
        w.writeframes(buff.tobytes())


async def narrate(script: str, path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(script, voice=os.getenv('DV_VOICE', 'es-ES-AlvaroNeural'), rate='+12%')
    await communicate.save(str(path))
    if not path.exists() or path.stat().st_size < 500:
        raise RuntimeError('No se generó una narración válida')


def render(ep, out: Path, require_voice=False):
    out.mkdir(parents=True, exist_ok=True)
    if not ep.get('script'):
        raise ValueError(f"{ep['id']}: propuesta sin guion; no se puede producir")
    # Las fuentes son metadatos opcionales; no bloquean video ni publicacion.
    if not ep.get('source'):
        print(f"AVISO: {ep['id']} sin fuentes propuestas; contenido no verificado independientemente.", flush=True)
    folder = out / ep['id']
    folder.mkdir(parents=True, exist_ok=True)
    shared_photo, image_credits = prepare_photo(ep, folder)
    if shared_photo is None:
        raise RuntimeError('El video requiere una fotografía de fondo; cancelado.')
    ep['image_credits'] = image_credits
    frames = []
    for i in range(5):
        path = folder / f'escena_{i}.jpg'
        scene(ep, i, path, photo=shared_photo)
        frames.append(path)
    cover = out / f"{ep['id']}.jpg"
    cover.write_bytes(frames[0].read_bytes())
    ambient_path = folder / 'ambient.wav'
    ambient(ambient_path)
    narration = folder / 'voz.mp3'
    try:
        asyncio.run(narrate(ep['script'], narration))
    except Exception as exc:
        if require_voice:
            raise RuntimeError(f'Narración obligatoria falló: {exc}') from exc
        print(f'AVISO: preview sin voz por: {exc}', file=sys.stderr)
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    motion = os.getenv('DV_SUBTLE_ZOOM', 'true').strip().lower() in ('1','true','yes','on')
    for frame in frames:
        args += ['-loop', '1', '-framerate', '30', '-t', '4', '-i', str(frame)]
    args += ['-i', str(ambient_path)]
    voice_available = narration.exists() and narration.stat().st_size > 500
    if voice_available:
        args += ['-i', str(narration)]
    # Zoom muy leve (hasta ~6%) sobre la MISMA foto; los textos no cambian de tamaño perceptiblemente.
    # d=1 genera un fotograma por fotograma de entrada; 30 fps x 4 s por escena.
    if motion:
        video_filters = ''.join(
            f"[{i}:v]zoompan=z='min(zoom+0.0005,1.06)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d=1:s=720x1280:fps=30,setsar=1[v{i}];"
            for i in range(5)
        )
    else:
        video_filters = ''.join(f'[{i}:v]fps=30,scale=720:1280,setsar=1[v{i}];' for i in range(5))
    video_filters += ''.join(f'[v{i}]' for i in range(5)) + 'concat=n=5:v=1:a=0[v];'
    if voice_available:
        video_filters += '[5:a]volume=0.28[amb];[6:a]volume=1.4[voice];[amb][voice]amix=inputs=2:duration=first:dropout_transition=0[a]'
    else:
        video_filters += '[5:a]volume=0.5[a]'
    movie = out / f"{ep['id']}.mp4"
    args += ['-filter_complex', video_filters, '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast',
             '-crf', '24', '-r', '30', '-c:a', 'aac', '-b:a', '128k',
             '-t', '20', '-movflags', '+faststart', str(movie)]
    subprocess.run(args, check=True, timeout=240)
    print(f'Video: {movie} ({movie.stat().st_size:,} bytes)')
    print(f'Portada: {cover}')
    print(f'Edición DATO WOW: mismo fondo B/N, sin círculos, zoom suave={motion}, 5 escenas de 4 segundos', flush=True)
    return movie, cover


class Github:
    def __init__(self):
        self.repo = os.environ['GITHUB_REPOSITORY']
        self.token = os.environ['GH_TOKEN']
        self.base = f'https://api.github.com/repos/{self.repo}'
        self.branch = os.getenv('GITHUB_REF_NAME', 'main')
        self.s = requests.Session()
        self.s.headers.update({'Authorization': f'Bearer {self.token}',
                               'Accept': 'application/vnd.github+json',
                               'X-GitHub-Api-Version': '2022-11-28'})

    def request(self, method, route, **kwargs):
        r = self.s.request(method, self.base + route, timeout=40, **kwargs)
        if r.status_code >= 400:
            raise RuntimeError(f'GitHub API HTTP {r.status_code}: {r.text[:600]}')
        return r.json()

    def read(self, path):
        route = '/contents/' + urllib.parse.quote(path, safe='/')
        r = self.s.get(self.base + route, params={'ref': self.branch}, timeout=40)
        if r.status_code == 404:
            return None, None
        if r.status_code >= 400:
            raise RuntimeError(f'Lectura GitHub falló HTTP {r.status_code}')
        data = r.json()
        return base64.b64decode(data['content']), data['sha']

    def write(self, path, content: bytes, previous_sha=None):
        payload = {'message': f'DataViral: {path}', 'branch': self.branch,
                   'content': base64.b64encode(content).decode()}
        if previous_sha:
            payload['sha'] = previous_sha
        route = '/contents/' + urllib.parse.quote(path, safe='/')
        return self.request('PUT', route, json=payload)

    def assert_public(self):
        if self.request('GET', '').get('private') is not False:
            raise RuntimeError('Para Instagram, el repositorio que aloja el MP4 debe ser público')


def ig_api(method, path, *, token, **kwargs):
    url = f'https://graph.instagram.com/{GRAPH_VERSION}/{path}'
    data = dict(kwargs.pop('data', {}) or {})
    data['access_token'] = token
    if method == 'GET':
        r = requests.get(url, params=data, timeout=50)
    else:
        r = requests.post(url, data=data, timeout=60)
    try:
        obj = r.json()
    except ValueError:
        raise RuntimeError(f'Instagram HTTP {r.status_code} respuesta no JSON')
    if not r.ok or obj.get('error'):
        raise RuntimeError(f'Instagram HTTP {r.status_code}: {obj.get("error", obj)}')
    return obj


def publish_container(user_id, token, video_url, caption):
    """Publica una sola vez el MP4 como Reel visible también en el feed.

    La API expone el mismo video en la pestaña Reels y la cuadrícula/feed,
    sin crear una segunda publicación ni enviar ninguna imagen.
    """
    fields = {'caption': caption, 'media_type': 'REELS',
              'video_url': video_url, 'share_to_feed': 'true'}
    container = ig_api('POST', f'{user_id}/media', token=token, data=fields)['id']
    for _ in range(30):
        time.sleep(10)
        status = ig_api('GET', container, token=token, data={'fields': 'status_code,status'})
        if status.get('status_code') == 'FINISHED':
            break
        if status.get('status_code') in ('ERROR', 'EXPIRED'):
            raise RuntimeError(f'Contenedor Instagram {container}: {status}')
    else:
        raise RuntimeError(f'Timeout contenedor IG {container}; NO reintentar sin reconciliar')
    return ig_api('POST', f'{user_id}/media_publish', token=token,
                  data={'creation_id': container})['id']



def publish_story_container(user_id, token, video_url):
    """Publica el mismo MP4 como Story; requiere permisos/cuenta compatibles."""
    cid = ig_api('POST', f'{user_id}/media', token=token,
                 data={'media_type':'STORIES','video_url':video_url})['id']
    for _ in range(30):
        time.sleep(10)
        status = ig_api('GET', cid, token=token, data={'fields':'status_code,status'})
        if status.get('status_code') == 'FINISHED':
            break
        if status.get('status_code') in ('ERROR', 'EXPIRED'):
            raise RuntimeError(f'Story contenedor {cid}: {status}')
    else:
        raise RuntimeError(f'Story contenedor {cid} sin confirmación: no reenviar automáticamente')
    return ig_api('POST', f'{user_id}/media_publish', token=token,
                  data={'creation_id':cid})['id']


def upload_video_to_public_github(gh, movie: Path, episode_id: str):
    """Sube un MP4 con nombre inmutable, sin modificar el estado histórico.

    Evita el conflicto 409 si un nombre de carpeta ya existe como archivo.
    Solo cambia la carpeta de medios; el estado sigue en dataviral/state.json.
    """
    movie_bytes = movie.read_bytes()
    digest = hashlib.sha256(movie_bytes).hexdigest()[:16]
    filename = f'{episode_id}-{digest}.mp4'
    # Nombres independientes del antiguo dataviral/media. Si un antecesor
    # de cualquiera es un archivo, probamos el siguiente directorio.
    roots = ('datoviral_assets/media', 'datoviral_video_assets/media',
             'datoviral_public_videos/media')
    for root in roots:
        remote = f'{root}/{filename}'
        try:
            old, _ = gh.read(remote)
        except (KeyError, TypeError) as exc:
            # GitHub Contents responde distinto si la ruta ya es un directorio
            # u otro objeto; no convertir errores ambiguos en sobrescrituras.
            raise RuntimeError(f'No se pudo inspeccionar ruta GitHub {remote}: {exc}') from exc
        if old is not None:
            if old != movie_bytes:
                raise RuntimeError(f'Colisión: existe otro archivo en {remote}')
            commit = gh.request('GET', f'/commits/{gh.branch}')['sha']
            print(f'Video ya almacenado en GitHub: {remote}', flush=True)
            return remote, commit
        try:
            result = gh.write(remote, movie_bytes)
        except RuntimeError as exc:
            message = str(exc)
            if 'HTTP 409' in message and ('subdirectory' in message or 'file exists' in message):
                print(f'Aviso: conflicto de ruta de medios {remote}; probando alternativa.', flush=True)
                continue
            raise
        print(f'Video almacenado en GitHub: {remote}', flush=True)
        return remote, result['commit']['sha']
    raise RuntimeError('GitHub: todos los directorios alternativos de video chocan con archivos. '
                       'Revisar manualmente la estructura del repositorio; no se publicó en Instagram.')


def publish(ep, movie, cover, approval):
    if approval != ep['id']:
        raise ValueError('Se exige aprobación explícita del mismo ID de episodio')
    if not ep.get('script'):
        raise ValueError('Publicación bloqueada: falta el guion narrado')
    if not ep.get('source'):
        print('AVISO: publicación sin enlaces de referencia; la IA no ha verificado los hechos.', flush=True)
    token = credential('INSTAGRAM_TOKEN', TEST_INSTAGRAM_TOKEN)
    user_id = credential('INSTAGRAM_USER_ID', TEST_INSTAGRAM_USER_ID)
    if not user_id.isdigit():
        raise ValueError('INSTAGRAM_USER_ID debe ser numérico')
    # La cuenta autorizada se define exclusivamente con variables de entorno.
    # Nunca escribir un usuario fijo en este archivo: la configuración vive en
    # GitHub Actions -> Settings -> Secrets and variables -> Actions -> Variables.
    expected = os.environ.get('IG_EXPECTED_USERNAME', '').strip().lstrip('@').lower()
    if not expected:
        raise RuntimeError('Falta IG_EXPECTED_USERNAME: define la variable de GitHub para publicar')
    me = ig_api('GET', 'me', token=token, data={'fields': 'id,username'})
    actual_id = str(me.get('id', '')).strip()
    actual_username = str(me.get('username', '')).strip().lstrip('@').lower()
    if actual_id != user_id:
        raise RuntimeError('INSTAGRAM_USER_ID no coincide con la cuenta autorizada por INSTAGRAM_TOKEN')
    if actual_username != expected:
        raise RuntimeError(
            f'Cuenta Instagram diferente: esperado=@{expected}, recibido=@{actual_username}'
        )
    print(f'Cuenta Instagram verificada: @{actual_username}', flush=True)
    gh = Github()
    gh.assert_public()
    path = 'dataviral/state.json'
    raw, sha = gh.read(path)
    state = json.loads(raw) if raw is not None else {'schema':1,'episodes':{}}
    row = state['episodes'].get(ep['id'], {})
    if any(row.get(key) in ('enviando','incierto','publicado') for key in ('reel', 'foto', 'feed_video', 'story')):
        raise RuntimeError('Hay publicación previa o incierta: bloqueo anti-duplicados')
    def save():
        nonlocal sha
        result = gh.write(path, json.dumps(state,ensure_ascii=False,indent=2).encode(), sha)
        sha = result['content']['sha']
    # Subida de archivos a un repositorio público: URL estable de commit. El tamaño
    # máximo de GitHub Contents API es 100 MB; no es un CDN de producción.
    remote, commit = upload_video_to_public_github(gh, movie, ep['id'])
    video_url = f'https://raw.githubusercontent.com/{gh.repo}/{commit}/{remote}'
    response = requests.get(video_url, timeout=60)
    if not response.ok or len(response.content) != movie.stat().st_size:
        raise RuntimeError(f'MP4 no accesible públicamente: HTTP {response.status_code}')
    caption = f'{ep["title"]}\n\n{ep["lesson"]}'
    if ep.get('source'):
        caption += f'\n\nReferencias sugeridas (no verificadas): {ep["source"]}'
    caption += '\n\n¿Qué parte te sorprendió más? Cuéntanos en comentarios.\n\n#DatoWow #AprendeAlgoNuevo'
    state['episodes'][ep['id']] = row
    row['reel'] = 'enviando'
    row['updated_at'] = now()
    save()
    try:
        published = publish_container(user_id, token, video_url, caption)
    except BaseException:
        row['reel'] = 'incierto'
        row['updated_at'] = now()
        try:
            save()
        except Exception as ex:
            print(f'ALERTA: sin persistencia de estado incierto: {ex}', file=sys.stderr)
        raise
    row['reel'] = 'publicado'
    row['share_to_feed'] = True
    row['reel_id'] = published
    row['updated_at'] = now()
    save()
    print(f'Video publicado como Reel Y visible en el feed: {published}')
    row['story'] = 'enviando'
    row['updated_at'] = now()
    save()
    try:
        story_id = publish_story_container(user_id, token, video_url)
    except BaseException:
        row['story'] = 'incierto'
        row['updated_at'] = now()
        try:
            save()
        except Exception as exc:
            print(f'ALERTA persistencia Story: {type(exc).__name__}', file=sys.stderr)
        raise
    row['story'] = 'publicado'
    row['story_id'] = story_id
    row['updated_at'] = now()
    save()
    print(f'Story publicada: {story_id}', flush=True)



def main():
    ap = argparse.ArgumentParser(description='DataViral: 500 ideas, IA OpenRouter Free y video Instagram')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--episode', default='', help='ID concreto; vacío = siguiente disponible')
    ap.add_argument('--out', default='output')
    ap.add_argument('--publish', action='store_true', help='Publicar Reel en feed y Story')
    ap.add_argument('--approved-id', default='', help='ID revisado manualmente (modo seguro)')
    ap.add_argument('--auto-publish', action='store_true', help='Publicación autónoma (sin revisión humana)')
    args=ap.parse_args()
    episodes=catalog()
    if len(episodes)!=500 or len({e['id'] for e in episodes})!=500:
        raise RuntimeError('Catálogo de 500 propuestas dañado')
    if args.list:
        for ep in episodes:
            print(f"{ep['id']}: {ep['title']}")
        return 0
    gh=Github() if args.publish and not args.episode else None
    ep=select_episode(episodes,gh,args.episode or None)
    if ep is None:
        ap.error('ID de episodio desconocido')
    if args.publish and not args.auto_publish and args.approved_id!=ep['id']:
        ap.error('Sin --auto-publish, debe confirmar --approved-id con el ID')
    generated=create_ai_episode(ep)
    out=Path(args.out)
    out.mkdir(exist_ok=True,parents=True)
    (out/f"{ep['id']}-guion.json").write_text(
        json.dumps(generated,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"Guion generado: {ep['id']}; referencias propuestas: {generated['source'] or 'ninguna'}")
    (out/f"{ep['id']}-experimento.json").write_text(
        json.dumps({
            'episode_id': ep['id'], 'category': ep.get('category'),
            'creative_variant': 'hook_mono_subtle_zoom_v1',
            'hook_visual': generated['visuals'][0],
            'duration_seconds': 20, 'scene_count': 5,
            'metrics': None,
            'note': 'Etiquetas de creatividad; las métricas reales requieren consulta posterior a Insights.'
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.publish and not generated.get('source'):
        print('AVISO: el guion no tiene fuentes; se permite publicar, pero no existe verificación independiente.', flush=True)
    movie,cover=render(generated,out,require_voice=args.publish)
    if args.publish:
        # Los enlaces son opcionales y nunca equivalen a verificación independiente.
        # --auto-publish implica riesgo de errores factuales de la IA.
        publish(generated,movie,cover,generated['id'])
    else:
        print('VISTA PREVIA: no se publicó el video')
    return 0


if __name__=='__main__':
    sys.exit(main())
