from django.core.paginator import Paginator

class PaginatorVil(Paginator):
    # Constructeur qui rappelle le constructeur parent
    def __init__(self, objectList, pageSize):
        super().__init__(objectList,pageSize)


    # Methode qui renvoie un range de 5 numero de page au plus en fonction de la page courante (liste glissante)
    def getPageListby5(self,pageNumber):
        pageNumber=int(pageNumber)
        if pageNumber <= 3 or self.num_pages <=5 :
            pageDeb=1
            pageFin=min(5,self.num_pages)
        elif self.num_pages - pageNumber < 2 :
            pageFin=self.num_pages
            pageDeb=max(1,pageFin-4)
        else :
            pageDeb=max(1,pageNumber -2)
            pageFin=min(pageDeb+4,self.num_pages)
        return range(pageDeb,pageFin+1)


