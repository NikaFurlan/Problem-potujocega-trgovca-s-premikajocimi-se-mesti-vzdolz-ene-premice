# Program za vhodne podatke prejme seznam ciljev oziroma mest, ki jih mora trgovec obiskati. Za vsako mesto
# je podana lega ob času sprostitve (p), smer gibanja (d) in čas (r), ob katerem se mesto sprosti (šele tedaj 
# ga lahko trgovec obišče). Poleg tega imamo podano še hitrost, s katero se mesta premikajo, ki je enaka za vsa mesta.
# Kot rezultat nam program izračuna najkrajši čas, ki ga trgovec potrebuje, da obišče vse cilje ter vrstni red, po
# katerem jih obišče.

# Metoda generiraj_seznam_d_r_p generira naključne sezname smeri premikanja ciljev, njihovih časov sprostitve in pozicij ob sprostitvi
# kot vhodna podatka podamo:
# * a in b: časovni interval časov sprostitve ciljev
# * e in f: interval pozicij ciljev ob času sprostitve
# * n: število ciljev
import random
def generiraj_sezname_d_r_p(a,b,e,f,n):
    if a < 0 or b < 0:
        return "Vhodna podatka a in b prikazujeta interval, na katerem so razporejeni časi sprostitve ciljev. Le-ti pa morajo biti nenegativni. Popravi vhodne podatke, da bodo ustrezni."
    else:
        d = []
        r = []
        p = []
        for i in range(n): # imamo n ciljev, generiramo vse 3 parametre za vsakega od njih
            d1 = random.randrange(-1,2,2) # d vsebuje -1 in 1 (začetek, konec, korak)
            d.append(d1)
            r1 = random.uniform(a,b)
            r.append(r1)
            p1 = random.uniform(e,f)
            p.append(p1)
        return (d,r,p) # vrnemo nabor 3 seznamov

# v razredu Cilj so opisane lastnosti in metode vsakega od podanih ciljev (mest)
class Cilj:
    def __init__(self, d, r, p): # kaj imamo podano za vsak cilj: d = smer gibanja, r = čas sprostitve, p = pozicija ob r
        self.d = d
        self.r = r
        self.p = p
        
    def pozicija(self, t, v): # pozicija cilja ob času t, v = hitrost
        return self.p + (t - self.r) * v * self.d
    
    def __hash__(self):
        return hash((self.d, self.r, self.p))
    
    def __eq__(self, other): # preverimo enakost dveh ciljev
        return (self.d, self.r, self.p) == (other.d, other.r, other.p)
    
    def __repr__(self): # kako bodo cilji predstavljeni
        return f"Cilj({self.d}, {self.r}, {self.p})"
    
# v naslednjih dveh razredih določimo razporeditve mest v sezname
class Ureditev: # načini, kako razporedimo cilje (razporedimo jih na 2 načina, nato pa obe ureditvi še obrnemo - dobimo skupno 4 ureditve)
    def __init__(self, seznam, kljuc): # seznam = vsi cilji, ključ = funkcija, ki določa, kako se seznam posortira
        self.seznam = sorted(seznam, key=kljuc)
        self.indeksi = {c: i for i, c in enumerate(self.seznam)} # cilje oštevilčimo v urejenem seznamu
        
    def __len__(self): # število ciljev
        return len(self.seznam)
    
    def __getitem__(self, index): # vrne element seznama z indeksom index
        return self.seznam[index] # sigma^(-1)(index) - navezava na oznake v članku
    
    def indeks(self, cilj): # vrne indeks nekega cilja
        return self.indeksi[cilj] # sigma(cilj)
    
class ObratnaUreditev: # obratni vrstni red razporeditve ciljev iz razreda Ureditev
    def __init__(self, ureditev):
        self.ureditev = ureditev
        
    def __len__(self):
        return len(self.ureditev)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            index = slice(None if index.start is None else -index.start-1,
                          None if index.stop is None else -index.stop-1,
                          -1 if index.step is None else -index.step)
        else:
            index = -index-1
        return self.ureditev.seznam[index] 
    
    def indeks(self, cilj):
        return len(self) - self.ureditev.indeks(cilj) - 1

# nekaj primerov uporabe    
# "*" poskrbi, da je vsak cilj določen s 3 ločenimi argumenti
# podatki za cilje: smer gibanja, čas sprostitve, pozicija ob sprostitvi
cilji1 = [Cilj(*p) for p in zip([1, 1, -1, -1, -1, 1, -1], [0, 5, 13, 15, 6, 8, 18], [2, 5, -3, 4, 1, -2, -7])] #seznam ciljev
v1 = 0.3 # hitrost premikanja ciljev
# možne ureditve ciljev:
IPO = Ureditev(cilji1, lambda c: c.pozicija(0, v1)) # z "lambda" navedemo neko anonimno funkcijo (lambda argumenti: funkcija)
TO = Ureditev(cilji1, lambda c: (c.d, c.pozicija(0, v1)))
IPOc = ObratnaUreditev(IPO)
TOc = ObratnaUreditev(TO)

print([IPOc.indeks(c) for c in cilji1]) # vrstni red mest v ureditvi IPOc
print(cilji1) # izpis seznama ciljev      
print(IPOc[2]) # izpis cilja, ki je na drugem mestu v ureditvi IPOc

# v razredu SLMTTSP (single line moving target traveling salesman problem) določimo metode, ki rešijo začetni problem       
class SLMTTSP:
    def __init__(self, cilji, v): # na začetku imamo podane cilje in hitrost, s katero se ti premikajo
        IPO = Ureditev(cilji, lambda c: c.pozicija(0, v))
        TO = Ureditev(cilji, lambda c: (c.d, c.pozicija(0, v)))
        IPOc = ObratnaUreditev(IPO)
        TOc = ObratnaUreditev(TO)
        self.v = v
        self.cilji = cilji
        self.ureditve = [IPO, IPOc, TO, TOc] # seznam z vsemi možnimi ureditvami ciljev
        self.F = {} # tu so shranjena stanja (C, i) in najkrajši časi, ko do tega stanja lahko pridemo (elementi se dodajajo v metodi f)
        
    def g(self, t, j, i): # najhitrejši čas obiska cilja i, če smo nazadnje obiskali cilj j ob času t
        posi = i.pozicija(t, self.v) # določimo poziciji ciljev i in j ob času t
        posj = 0 if j is None else j.pozicija(t, self.v)
        razlika = posi - posj
        delta = 1 if razlika > 0 else -1 # hitrost gibanja agenta (pozitivna (negativna), če je razlika med zaporednima ciljema pozitivna (negativna))
        tt = t + razlika / (delta - self.v * i.d) # najmanjši potreben čas obiska i, dodan k trenutnemu času t
        if tt >= i.r: # primer, ko trgovec doseže i potem, ko je bil ta že sproščen
            return (tt, [(t, posj, j), (tt, posi, i)]) 
        # s trojicami znotraj [] si zapomnimo odseke trgovčeve poti (na katerih pozicijah je bil ob časih t in tt in kateri cilj je bil tedaj dosežen)
        else: # če cilj i v trenutku, ko trgovec doseže njegovo pozicijo, še ni bil sproščen, mora trgovec tam počakati na sprostitev
            return (i.r, [(t, posj, j), (t + abs(i.p - posj), i.p, None), (i.r, i.p, i)]) 
        # v zadnjem primeru (srednji element seznama) agent čaka na poziciji i.p do časa i.r (v tem primeru je delta = 0)
        
    def predhodno_stanje(self, C, i): # implementacija formule iz članka, vrne stanje, predhodno stanju (C, i)
        if i is None: # primer, ko ni predhodnega cilja
            return None
        return tuple(min(C[l], self.ureditve[l].indeks(i)) for l in range(4))
        
    def phi(self, C): # vrne vsa že obiskana mesta v naboru C
        return {j for l, m in enumerate(C) for j in self.ureditve[l][:m]} # vrne mesta, ki so bolj na začetku seznama l kot mesto m
    
    def predhodnik(self, l, C, i): # implementacija formule iz članka, vrne zadnje obiskano mesto pred mestom i (prišlo naj bi iz ureditve l)
        if i is None:
            return None
        CC = self.predhodno_stanje(C, i)
        obiskana = self.phi(CC)
        for j in reversed(self.ureditve[l][:CC[l]]): # obrnemo ureditev, da bodo indeksi razporedejni padajoče in bomo hitreje našli največjega
            # iščemo cilj j z največjim indeksom v ureditvi l (ki je manjši od indeksa cilja iz ureditve l v naboru, ki opisuje predhodno stanje), ki še ni obiskan
            if len(obiskana.difference(self.phi(self.predhodno_stanje(CC, j)))) == 1: # razlika med zaporednima množicama obiskanih mest mora biti dolžine 1
                return j
        return None
        
    def f(self, C, i): # minimalni čas, da dosežemo stanje (C, i) - glede na predhodno stanje in predhodnika
        if (C, i) not in self.F: # preverimo, da stanja še nismo poračunali
            kandidati = [] # shranimo vse izračune, potrebovali pa bomo le minimalnega
            CC = self.predhodno_stanje(C, i)
            for l in range(4): # za vsako ureditev predpostavimo, da je predhodnik prišel iz nje
                j = self.predhodnik(l, C, i)
                # če trenutni seznam ne da kandidata, ga preskočimo
                if j is None:
                    continue
                (t, _), _, _ = self.f(CC, j)
                kandidati.append((self.g(t, j, i), l, j)) 
                # vsak kandidat je določen s 3 argumenti: 
                # * rezultat funkcije g (najhitrejši čas obiska cilja i, če smo nazadnje obiskali cilj j ob času t), 
                # * indeks seznama, iz katerega je prišel naslednji obiskani cilj (l) 
                # * predhodnik (j) 
                # najmanjšega od kandidatov shranimo v F pod ključ (C, i) - pripadajoče stanje
            self.F[C, i] = min(kandidati) if kandidati else (self.g(0, None, i), None, None)
        return self.F[C, i]
    
    def resi(self): # izračun minimalnega časa, v katerem so obiskani vsi cilji
        n = len(self.cilji) # stevilo vseh ciljev
        # izvedemo f na vseh možnih naborih C za vsak cilj i
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    for d in range(n):
                        for i in cilji:
                            self.f((a, b, c, d), i) # shrani v F minimalni čas, da dosežemo stanje (C, i)
        (C, i) = min((self.f((n, n, n, n), i), i) for i in cilji) # od zaključnega stanja "nazaj" poteka rekurzija
        # z dodatnim i v zadnjem minimumu si zapomnimo še zadnje obiskano mesto
        (skupni_cas, odsek), l, predhodni_cilj = C
        resitev = [odsek] # seznam, kamor se shranjujejo obiskana mesta od zadaj naprej (na začetku je notri zadnje obiskano mesto)
        predhodno_stanje = self.predhodno_stanje((n, n, n, n), i)
        while predhodni_cilj is not None: # dokler ima cilj predhodnika
            i = predhodni_cilj
            (t, odsek), l, predhodni_cilj = self.F[predhodno_stanje, i] # predhodnika preberemo iz slovarja F
            predhodno_stanje = self.predhodno_stanje(predhodno_stanje, i) # izračun predhodnega stanja
            resitev.append(odsek[:-1]) # končno stanje je že začetno stanje naslednjega odseka
        return skupni_cas, sum(reversed(resitev), []) # potreben čas in vrstni red obiska ciljev 
        # (seznam "resitev" obrnemo okrog, da so odseki ustrezno razporejeni in te staknemo v en seznam)

# primer uporabe (v in cilji so enaki kot pri prejšnjem primeru)
primer1 = SLMTTSP(cilji1, v1)
resitev1 = primer1.resi()
print(resitev1)

# drugi primer uporabe (NAVODILA ZA UPORABNIKA)
# Najprej nastavi hitrost premikanja ciljev. Generiraj potrebne sezname, tako da namesto a, b, e, f in n vstaviš želene podatke. 
# a in b predstavljata časovni interval sprostitve ciljev, e in f interval začetnih pozicij, na katerih se nahajajo cilji ob sprostitvi, 
# n pa predstavlja število ciljev, ki jih želimo obravnavati. Nato poženi spodnje funkcije. 

# v = 
# d, r, p = generiraj_sezname_d_r_p(a,b,e,f,n)

# cilji = [Cilj(*p) for p in zip(d, r, p)]
# primer2 = SLMTTSP(cilji, v)
# resitev2 = primer2.resi()
# print(resitev2)
