class TableNode:
    def __init__(self):
        #definirati Korijen koji je globalni djelokrug
        #onda definirati Lokalne djelokruge
        #da li da radimo odvojeno za funkcije, pa za varijable
        #za varijablu moramo definirati tip i dodijeljena vrijednost
        #za funkciju isto moramo definirati tip (povratna/parametri)
        # ->i odabrati jel ju zapisujemo u declare ili defined
        self.declared = []
        self.defined = []
        #kazaljka na lokalne varijable
        self.scope = []
        #fora je u tom da ako nije u lokalnom djelokrugu onda tražimo u globalnom
        #kazaljka na ugnježđujući blok
        return
    