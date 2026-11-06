// Сборка моделей Xcos для ЛР2, вариант 4
loadXcosLibs(); loadScicos();
function [o]=place(b,x,y,w,h,lbl,flp)
    b.graphics.orig=[x,y]; b.graphics.sz=[w,h];
    if lbl<>"" then b.graphics.id=lbl; end
    if flp then b.graphics.style=b.gui+";flip=true"; b.graphics.flip=%f; end
    o=b;
endfunction
function p=outp(b,i)
    g=b.graphics;
    if or(b.gui==["SPLIT_f","CLKSPLIT_f"]) then p=g.orig+g.sz/2; return; end; n=size(b.model.out,"*"); x=g.orig(1); y=g.orig(2); w=g.sz(1); h=g.sz(2);
    if g.style<>"" & strindex(g.style,"flip=true")<>[] then p=[x, y+h*i/(n+1)]; else p=[x+w, y+h*i/(n+1)]; end
endfunction
function p=inp(b,i)
    g=b.graphics;
    if or(b.gui==["SPLIT_f","CLKSPLIT_f"]) then p=g.orig+g.sz/2; return; end; n=size(b.model.in,"*"); x=g.orig(1); y=g.orig(2); w=g.sz(1); h=g.sz(2);
    if g.style<>"" & strindex(g.style,"flip=true")<>[] then p=[x+w, y+h*i/(n+1)]; else p=[x, y+h*i/(n+1)]; end
endfunction
function p=eout(b)
    g=b.graphics;
    if b.gui=="CLKSPLIT_f" then p=g.orig+g.sz/2; return; end; p=[g.orig(1)+g.sz(1)/2, g.orig(2)+g.sz(2)];
endfunction
function p=ein(b)
    g=b.graphics;
    if b.gui=="CLKSPLIT_f" then p=g.orig+g.sz/2; return; end; p=[g.orig(1)+g.sz(1)/2, g.orig(2)];
endfunction
function l=lk(ia,pa,ib,pb,pts,ev)
    // pts: rows [x y] of all points incl. ends
    if ev then ct=[5,-1]; else ct=[1,1]; end
    if size(pts,1)==2 & pts(1,2)<>pts(2,2) & ~ev then
        xm=pts(2,1)-12; pts=[pts(1,:); xm pts(1,2); xm pts(2,2); pts(2,:)];
    end
    l=scicos_link(xx=pts(:,1),yy=pts(:,2),ct=ct,from=[ia,pa,0],to=[ib,pb,1]);
endfunction
function b=tf(num,den)
    b=CLR("define"); b.graphics.exprs=[num;den];
endfunction
function b=stepb(v)
    b=STEP_FUNCTION("define");
    for i=1:length(b.model.rpar.objs)
        o=b.model.rpar.objs(i);
        if typeof(o)=="Block" then
            if o.gui=="STEP" then
                o.graphics.exprs=["0";"0";string(v)];
                o.model.rpar=[v;v]; o.model.firing=0;
                b.model.rpar.objs(i)=o;
            end
        end
    end
endfunction
function b=sumb(sg)
    b=SUMMATION("define"); b.graphics.exprs=["1";sci2exp(sg);"0"];
    b.model.ipar=sg; b.model.in=-ones(sg); b.model.in2=-2*ones(sg); b.model.intyp=ones(sg);
    b.graphics.pin=zeros(sg);
endfunction
function b=clockb()
    b=CLOCK_c("define");
    for i=1:length(b.model.rpar.objs)
        o=b.model.rpar.objs(i);
        if typeof(o)=="Block" then
            if o.gui=="EVTDLY_c" then
                o.graphics.exprs=["0.1";"0"]; o.model.rpar=[0.1;0]; o.model.firing=0;
                b.model.rpar.objs(i)=o;
            end
        end
    end
    b.model.firing=0;
endfunction
function b=scopeb(ymin,ymax)
    b=CSCOPE("define"); e=b.graphics.exprs;
    e(5)=string(ymin); e(6)=string(ymax); e(7)="100";
    b.graphics.exprs=e; b.model.rpar=[0;ymin;ymax;100];
endfunction
function b=towsb(nm,nz)
    b=TOWS_c("define"); b.graphics.exprs=[string(nz);nm;"0"];
    b.model.ipar=[nz; length(ascii(nm)); ascii(nm)'];
endfunction
function b=textb(s,x,y)
    b=TEXT_f("define"); b.graphics.exprs=[s;"2";"1"]; b.graphics.orig=[x,y]; b.graphics.sz=[60,20];
endfunction

// mode: 1 - ПД + осциллографы; 2 - ПД + возмущение + TOWS; 3 - ПИД + возмущение + TOWS
function scs_m=build(mode)
    scs_m=scicos_diagram(); scs_m.props.tf=100;
    dist=(mode==2|mode==3); if dist then scs_m.props.tf=500; end
    o=list();
    Y=100; // главная линия
    // 1 Заданный курс
    o(1)=place(stepb(10), 10, Y-30, 40, 40, "Заданный курс", %f);
    // 2 сумматор
    s1=sumb([1;-1]); o(2)=place(s1, 90, Y-30, 30, 60, "", %f);
    // сдвиг: вход 1 сумматора на Y-10, вход 2 на Y+10
    if mode<>3 then
        o(3)=place(tf("13.53*s+0.7","s+1"), 160, Y-20, 100, 40, "Регулятор", %f);
        xR=300;
    else
        o(3)=place(tf("13.53*s+0.7","s+1"), 190, Y-20, 100, 40, "Регулятор", %f);
        xR=380;
    end
    o(4)=place(tf("1","2*s+1"), xR, Y-20, 60, 40, "Привод", %f);
    xP=xR+130; if dist then xP=xR+240; end
    o(5)=place(tf("0.07","16.6*s^2+s"), xP, Y-20, 90, 40, "Судно", %f);
    o(6)=place(tf("1","4*s+1"), xP-40, Y+70, 60, 40, "Гирокомпас", %t);
    o(7)=place(SPLIT_f("define"), xR+87, Y-3, 7, 7, "", %f);   // после привода
    o(8)=place(SPLIT_f("define"), xP+127, Y-3, 7, 7, "", %f);  // после судна
    if mode==1 then
        o(9)=place(scopeb(-5,40), xP+60, Y-140, 40, 40, "Руль", %f);
        o(10)=place(scopeb(0,15), xP+180, Y-20, 40, 40, "Курс", %f);
    else
        nz=5000; if ~dist then nz=1000; end
        o(9)=place(towsb("delta",nz), xP+50, Y-140, 60, 40, "Руль", %f);
        o(10)=place(towsb("phi",nz), xP+180, Y-20, 60, 40, "Курс", %f);
    end
    o(11)=place(clockb(), xP-40, Y-240, 40, 40, "", %f);
    o(12)=place(CLKSPLIT_f("define"), xP+17, Y-183, 7, 7, "", %f);
    n=12;
    L=list();
    // 1 -> 2.1
    p=outp(o(1),1); q=inp(o(2),1); L($+1)=lk(1,1,2,1,[p; q(1)-15 p(2); q(1)-15 q(2); q],%f);
    // 2 -> 3 (ПД)
    if mode<>3 then
        p=outp(o(2),1); q=inp(o(3),1); L($+1)=lk(2,1,3,1,[p; q],%f);
    end
    // 3 -> 4
    if mode<>3 then
        p=outp(o(3),1); q=inp(o(4),1); L($+1)=lk(3,1,4,1,[p; q],%f);
    end
    // 4 -> split7
    p=outp(o(4),1); q=inp(o(7),1); L($+1)=lk(4,1,7,1,[p; q],%f);
    // split7 -> scope Руль (вверх)
    p=outp(o(7),2); q=inp(o(9),1); L($+1)=lk(7,2,9,1,[p; p(1) q(2); q],%f);
    // 5 -> split8
    p=outp(o(5),1); q=inp(o(8),1); L($+1)=lk(5,1,8,1,[p; q],%f);
    // split8 -> Курс
    p=outp(o(8),1); q=inp(o(10),1); L($+1)=lk(8,1,10,1,[p; q],%f);
    // split8 -> H (вниз и влево)
    p=outp(o(8),2); q=inp(o(6),1); L($+1)=lk(8,2,6,1,[p; p(1) q(2); q],%f);
    // H -> 2.2
    p=outp(o(6),1); q=inp(o(2),2); L($+1)=lk(6,1,2,2,[p; q(1)-15 p(2); q(1)-15 q(2); q],%f);
    // события: clock -> clksplit -> scopes
    p=eout(o(11)); q=ein(o(12)); L($+1)=lk(11,1,12,1,[p; p(1) q(2); q],%t);
    p=eout(o(12)); q=ein(o(9)); L($+1)=lk(12,1,9,1,[p; q(1) p(2); q],%t);
    p=eout(o(12)); q=ein(o(10)); L($+1)=lk(12,2,10,1,[p; q(1) p(2); q],%t);
    if ~dist then
        // 7 -> 5 напрямую
        p=outp(o(7),1); q=inp(o(5),1); L($+1)=lk(7,1,5,1,[p; q],%f);
    else
        // возмущение: блок 13 STEP 2, сумматор 14
        n=n+1; o(n)=place(stepb(2), xR+110, Y-90, 40, 40, "Возмущение", %f); iw=n;
        n=n+1; o(n)=place(sumb([1;1]), xR+180, Y-30, 30, 60, "", %f); is2=n;
        p=outp(o(7),1); q=inp(o(is2),1); L($+1)=lk(7,1,is2,1,[p; q],%f);
        p=outp(o(iw),1); q=inp(o(is2),2); L($+1)=lk(iw,1,is2,2,[p; q(1)-15 p(2); q(1)-15 q(2); q],%f);
        p=outp(o(is2),1); q=inp(o(5),1); L($+1)=lk(is2,1,5,1,[p; p(1)+15 p(2); p(1)+15 q(2); q],%f);
    end
    if mode==3 then
        n=n+1; o(n)=place(SPLIT_f("define"), 147, Y-3, 7, 7, "", %f); isp=n;
        n=n+1; o(n)=place(tf("1","200*s"), 200, Y+30, 80, 40, "И-канал", %f); ii=n;
        n=n+1; o(n)=place(sumb([1;1]), 320, Y-30, 30, 60, "", %f); is3=n;
        p=outp(o(2),1); q=inp(o(isp),1); L($+1)=lk(2,1,isp,1,[p; q],%f);
        p=outp(o(isp),1); q=inp(o(3),1); L($+1)=lk(isp,1,3,1,[p; p(1) q(2); q],%f);
        p=outp(o(isp),2); q=inp(o(ii),1); L($+1)=lk(isp,2,ii,1,[p; p(1) q(2); q],%f);
        p=outp(o(3),1); q=inp(o(is3),1); L($+1)=lk(3,1,is3,1,[p; q],%f);
        p=outp(o(ii),1); q=inp(o(is3),2); L($+1)=lk(ii,1,is3,2,[p; p(1)+10 p(2); p(1)+10 q(2); q],%f);
        p=outp(o(is3),1); q=inp(o(4),1); L($+1)=lk(is3,1,4,1,[p; p(1)+10 p(2); p(1)+10 q(2); q],%f);
    end
    // надписи
    lab=list();
    for k=[1 3 4 5 6 9 10]
        g=o(k).graphics; lab($+1)=list(g.id, g.orig(1)+g.sz(1)/2-30, g.orig(2)-22);
    end
    if dist then g=o(iw).graphics; lab($+1)=list(g.id, g.orig(1)-10, g.orig(2)-22); end
    if mode==3 then g=o(ii).graphics; lab($+1)=list(g.id, g.orig(1)-65, g.orig(2)+10); end
    // записать связи в pin/pout
    for k=1:length(L)
        l=L(k); idx=n+k;
        if l.ct(2)==-1 then
            g=o(l.from(1)).graphics; g.peout(l.from(2))=idx; o(l.from(1)).graphics=g;
            g=o(l.to(1)).graphics; g.pein(l.to(2))=idx; o(l.to(1)).graphics=g;
        else
            g=o(l.from(1)).graphics; g.pout(l.from(2))=idx; o(l.from(1)).graphics=g;
            g=o(l.to(1)).graphics; g.pin(l.to(2))=idx; o(l.to(1)).graphics=g;
        end
    end
    for k=1:n, scs_m.objs(k)=o(k); end
    for k=1:length(L), scs_m.objs(n+k)=L(k); end
    m=n+length(L);
    for k=1:length(lab), t=lab(k); scs_m.objs(m+k)=textb(t(1),t(2),t(3)); end
endfunction
