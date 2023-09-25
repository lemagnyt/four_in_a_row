import tkinter as tk
from tkinter import font as tkfont
import random
import numpy as np
import pygame

###############################################################################
# création de la fenetre principale  - ne pas toucher

LARG = 900
HAUT = 610

#Fenetre principale
Window = tk.Tk()
Window.geometry(str(LARG)+"x"+str(HAUT))
Window.title("ESIEE - Puissance 4")
Window.resizable(width=False,height=False)

# création de la frame principale stockant toutes les pages

F = tk.Frame(Window,bd=5,relief=tk.SUNKEN)
F.pack(side="top", fill="both", expand=True)
F.grid_rowconfigure(0, weight=1)
F.grid_columnconfigure(0, weight=1)
F.pack(side=tk.LEFT)

# gestion des différentes pages

ListePages  = {}
PageActive = 0

def CreerUnePage(id):
    Frame = tk.Frame(F)
    ListePages[id] = Frame
    Frame.grid(row=0, column=0, sticky="nsew")
    return Frame

def AfficherPage(id):
    global PageActive
    PageActive = id
    ListePages[id].tkraise()

Frame0 = CreerUnePage(0)

canvas = tk.Canvas(Frame0,width = LARG, height = HAUT, bg ="black" )
canvas.place(x=0,y=0)

#Permet d'afficher le score de la partie
def AfficheScore():
    global score_H,score_IA
    sH=str(score_H)
    sIA=str(score_IA)
    if score_H<10 : sH=str(0)+str(sH)
    if score_IA<10 : sIA=str(0)+str(sIA)
    sP1="HU"
    sP2="IA"
    if mode ==4  :
        sP1="P1"
        sP2="P2"
    canvas.create_rectangle(715,90,875,150,fill="white")
    canvas.create_text(795,120,text=sH+"  -  "+ sIA,font = PoliceTexte)
    canvas.create_rectangle(715,25,785,75,fill="red")
    if mode>2 or mode==0 : canvas.create_rectangle(805,25,875,75,fill="yellow")
    else :
        canvas.create_rectangle(805,25,842.5,75,fill="yellow")
        canvas.create_rectangle(842.5,25,875,75,fill="green")
    canvas.create_text(750,50,text=sP1,font=PoliceTexte)
    canvas.create_text(840,50,text=sP2,font=PoliceTexte)

#Permet d'afficher le résultat
def AfficheResult():
    canvas.create_text(795,310,text = " Appuyer sur\n    \"Restart\"\n pour rejouer !",fill="black",font= PoliceTexte2)
    if mode <= 3 :
        sHU="HU"
        sIA="IA"
    else :
        sHU="P1"
        sIA="P2"
    for x in range(7):
        for y in range (6):
            if Win(Grille,4,1,x,y):
                canvas.create_text(795,225,text = sHU+" WIN",fill="red",font= PoliceTexte1)
                return
            if Win(Grille,4,2,x,y):
                canvas.create_text(795,225,text = sIA+" WIN",fill="yellow",font= PoliceTexte1)
                return
            if AlignementCarre(Grille,4,3,x,y):
                canvas.create_text(795,225,text = sIA+" WIN",fill="green",font= PoliceTexte1)
                return
    if MatchNul(Grille):
        canvas.create_text(795,225,text = "NUL",fill="blue",font= PoliceTexte1)

def AfficheMode() :
    global mode
    if mode == 0 : smode = "Mode 1 v 1 sans Mode Simulation"
    if mode == 1 : smode = "Mode 1 v 1 v 1 sans Mode Simulation"
    if mode == 2 : smode = "Mode 1 v 1 v 1 avec Mode Simulation"
    if mode == 3 : smode = "Mode 1 v 1 avec Mode Simulation"
    if mode == 4 : smode = "Mode 1 v 1 Joueur vs Joueur"
    canvas.create_text(800,565,text=smode,font=PoliceTexte3, fill="white")

#################################################################################
'''Parametres du jeu'''

Grille = [ [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0] ]
#Les lignes representent les colonnes de la grille
Grille = np.array(Grille)
Grille = Grille.transpose()

#Pour le son a chaque jeton
pygame.mixer.init()

debutPartie=True
finPartie=False
game_justStart=True
Player = 1
PionsGagnants = []
score_IA=0
score_H=0
'''Modes  : 1 = PlacJud(R,J,V) - 2 = PlacJud(V),Simu(R,J) - 3 = Simu(R,J) - 4 = 1v1 manuel'''
mode = 0
PHU = (8,8)
PIA = (8,8)
PIAV = (8,8)
###############################################################################
''' gestion des victoires'''

#Permet de detecter lorsqu'il y a un alignement de N pions en vertical
def AlignementVertical(G,N,P,x,y):
    for i in range (len(G[x])-3):
        compteurP=0
        compteurV=0
        List=[]
        for j in range (0,len(G[x])-i) :
            if G[x][i+j]==P:
                compteurP+=1
                List.append((x,(i+j)))
            elif G[x][i+j]==0:
                compteurV+=1
            else:
                List = []
                compteurV=0
                compteurP=0
            if (compteurP==N and compteurV==4-N):
                if (x,y) in List : return True

    return False

#Permet de detecter lorsque il y a un alignement de N pions en horizontal
def AlignementHorizontal(G,N,P,x,y):
    Grille2=G.transpose()
    return AlignementVertical(Grille2,N,P,y,x)

#Permet de recuperer les diagonales
def AlignementDiagonal(G,NPions,P,x,y):

    #Test pour la diagonale de haut gauche a bas droit
    G2=G.copy()
    diagonale=np.diagonal(G2,offset=y-x)

    #Test pour la diagonale bas gauche a haut droit
    G3=G.copy()
    G3=np.flipud(G3)
    diagonale2=np.diagonal(G3,offset=x-(6-y))
    return CheckDiagonale(diagonale,NPions,P) or CheckDiagonale(diagonale2,NPions,P)

#Permet de verifier si il y a un alignement de Npions en diagonale
def CheckDiagonale(diagonale,N,P):
    for i in range (len(diagonale)-3):
        compteurP=0
        compteurV=0
        for j in range (0,len(diagonale)-i) :
            if diagonale[i+j]==P:
                compteurP+=1
            elif diagonale[i+j]==0:
                compteurV+=1
            else:
                compteurV=0
                compteurP=0
            if (compteurP==N and compteurV==4-N):
                    return True

    return False

#Permet de verifier si un joueur a gagner
def Win(G,N,P,x,y):
    return AlignementVertical(G,N,P,x,y) or AlignementDiagonal(G,N,P,x,y) or AlignementHorizontal(Grille,N,P,x,y)

#Permet de detecter si l'IA verte a gagne
def AlignementCarre(G,N,P,x,y):
    for i in range(6):
        for j in range(5):
            compteur=0
            compteurV=0
            if G[i][j]==P:compteur+=1
            elif G[i][j]==0:compteurV+=1
            if G[i][j+1]==P:compteur+=1
            elif G[i][j+1]==0:compteurV+=1
            if G[i+1][j]==P:compteur+=1
            elif G[i+1][j]==0:compteurV+=1
            if G[i+1][j+1]==P:compteur+=1
            elif G[i+1][j+1]==0:compteurV+=1
            if (compteur==N and compteurV==4-N and G[x][y]==P):
                if (x,y)==(i,j) or (x,y)==(i,j+1) or (x,y)==(i+1,j) or (x,y)==(i+1,j+1): return True
    return False

################################################################################
'''Gestion de l'ia et du joueur'''

#Permet de placer les jetons des joueurs
def PlacementJetons(x,G):
    if x not in PossibleMove(G):
        return
    else:
        for y in range(5,-1,-1):
            if G[x][y]==0:
                return (x,y)

#Permet de savoir si il y a des coups possibles
def PossibleMove(G):
    liste=[]
    for x in range(7):
        if G[x][0]==0:
            liste.append(x)
    return liste

#Permet de faire bouger aleatoirement parmis les coups possibles l'ia
def MoveIA(G):
    moves=PossibleMove(G)
    choix=random.randrange(len(moves))
    return moves[choix]

#Permet de savoir quel coup sera le meilleur en fonction du score
def PlacementJudicieux(G,P):
    if P==1 : P2=2
    if P==2 : P2=1
    L=PossibleMove(G)
    score=[(0,(0,0))]
    liste_score=[0]
    scoreS=0
    for x in L:
        center = 0
        coup=PlacementJetons(x,G)
        if x>=2 and x<=4: center = 2

        G[coup[0]][coup[1]]=P
        if Win(G,4,P,coup[0],coup[1]):
            score.append((100,coup))
            scoreS+=100
            liste_score.append(100)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=P2
        if Win(G,4,P2,coup[0],coup[1]):
            score.append((50+center,coup))
            scoreS+=50
            liste_score.append(50+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=3
        if AlignementCarre(G,4,3,coup[0],coup[1]):
            score.append((50+center,coup))
            scoreS+=50
            liste_score.append(50+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=P
        if Win(G,3,P,coup[0],coup[1]):
            score.append((30+center,coup))
            scoreS+=30
            liste_score.append(30+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=P2
        if Win(G,3,P2,coup[0],coup[1]):
            score.append((15+center,coup))
            scoreS+=15
            liste_score.append(15+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=3
        if AlignementCarre(G,3,3,coup[0],coup[1]):
            score.append((15+center,coup))
            scoreS+=50
            liste_score.append(15+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=P
        if Win(G,2,P,coup[0],coup[1]):
            score.append((10+center,coup))
            scoreS+=10
            liste_score.append(10+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        score.append((5+center,coup))
        scoreS+=5
        liste_score.append(5+center)
    indice=liste_score.index(max(liste_score))
    return score[indice],scoreS

#Permet de savoir quel coup sera le meilleur en fonction du score pour le joueur vert
def PlacementJudicieux2(G):
    ListP = [1,2]
    L=PossibleMove(G)
    score=[(0,(0,0))]
    liste_score=[0]
    scoreS=0
    for x in L:
        center = 0
        coup=PlacementJetons(x,G)
        if x>=2 and x<=4: center = 2

        G[coup[0]][coup[1]]=3
        if AlignementCarre(G,4,3,coup[0],coup[1]):
            score.append((100,coup))
            scoreS+=100
            liste_score.append(100)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        for P in ListP:
            G[coup[0]][coup[1]]=P
            if Win(G,4,P,coup[0],coup[1]):
                score.append((50+center,coup))
                scoreS+=50
                liste_score.append(50+center)
                G[coup[0]][coup[1]]=0
                continue
            G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=3
        if AlignementCarre(G,3,3,coup[0],coup[1]):
            score.append((30+center,coup))
            scoreS+=30
            liste_score.append(30+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        for P in ListP :
            G[coup[0]][coup[1]]=P
            if Win(G,3,P,coup[0],coup[1]):
                score.append((15+center,coup))
                scoreS+=15
                liste_score.append(15+center)
                G[coup[0]][coup[1]]=0
                continue
            G[coup[0]][coup[1]]=0

        G[coup[0]][coup[1]]=3
        if AlignementCarre(G,2,3,coup[0],coup[1]):
            score.append((10+center,coup))
            scoreS+=10
            liste_score.append(10+center)
            G[coup[0]][coup[1]]=0
            continue
        G[coup[0]][coup[1]]=0

        score.append((5+center,coup))
        scoreS+=5
        liste_score.append(5+center)
    indice=liste_score.index(max(liste_score))
    return score[indice],scoreS

#Affichage du coup gagnant
def pions_gagnants(G,P,x,y) :
    list = []
    if Win(G,4,P,x,y):
        if AlignementVertical(G,4,P,x,y):
            compteur = 0
            for i in range(6):
                if G[x][i] == P :
                    compteur +=1
                    list.append((x,i))
                    if compteur== 4 : return list
                else :
                    list = []
                    compteur = 0
        if AlignementHorizontal(G,4,P,x,y):
            G2 = G.copy()
            G2 = G2.transpose()
            compteur = 0
            for i in range(7):
                if G2[y][i] == P :
                    compteur +=1
                    list.append((i,y))
                    if compteur== 4 : return list
                else :
                    list = []
                    compteur = 0
        if AlignementDiagonal(G,4,P,x,y):
            ixG = x
            iyG = y
            iyD = y
            ixD = x
            compteur = 0
            while(ixG>0 and iyG>0):
                ixG-=1
                iyG-=1
            while(ixD>0 and iyD<5):
                ixD-=1
                iyD+=1
            while(ixG<=6 and iyG<=5):
                if(G[ixG][iyG]==P):
                    compteur +=1
                    list.append((ixG,iyG))
                    if compteur == 4 : return list
                else :
                    list =[]
                    compteur = 0
                ixG+=1
                iyG+=1
            compteur = 0
            list=[]
            while(ixD<=6 and iyD>=0):
                if(G[ixD][iyD]==P):
                    compteur +=1
                    list.append((ixD,iyD))
                    if compteur== 4 : return list
                else :
                    list =[]
                    compteur = 0
                ixD+=1
                iyD-=1
    return list

#Permet de detecter quel carre est le gagnant
def carregagnant(G,P,x,y):
    List=[]
    if AlignementCarre(G,4,P,x,y):
        for i in range(6):
            for j in range(5):
                compteur=0
                if G[i][j]==P:compteur+=1
                if G[i][j+1]==P:compteur+=1
                if G[i+1][j]==P:compteur+=1
                if G[i+1][j+1]==P:compteur+=1
                if compteur==4:return [(i,j),(i,j+1),(i+1,j),(i+1,j+1)]

    return List

#Permet d'evaluer la grille
def Note(G):
    for x in range (7):
        for y in range (6):
            if Win(G,4,2,x,y):return 500
            if Win(G,4,1,x,y):return -500
    LIA = PlacementJudicieux(G,2)[1]
    LH  = PlacementJudicieux(G,1)[1]
    return LIA-LH

#Permet de savoir quand la partie est finie
def PartieFinie(G):
    for x in range(7):
        for y in range (6):
            if Win(G,4,2,x,y) or Win(G,4,1,x,y) or AlignementCarre(G,4,3,x,y): return True
    return MatchNul(G)

#Permet de savoir si la partie est un match nul
def MatchNul(G):
    compteur=0
    for x in range(7):
        for y in range(6):
            if G[x][y]!=0:
                compteur+=1
    if compteur==42:
        return True
    else:
        return False

#Permet de determiner le meilleur coup en simulant des parties
def MinMax(G,N,i):
    if PartieFinie(G) or N==0:
        return (Note(G),0)
    L = PossibleMove(G)
    Résultats = []
    ListR = []
    for x in L:
        K = PlacementJetons(x,G)
        if i>0: G[K[0]][K[1]]=2
        else : G[K[0]][K[1]]=1
        R=MinMax(G,N-1,-i)
        Résultats.append((R[0],K))
        ListR.append(R[0])
        G[K[0]][K[1]]=0
    if i>0 : v = max(ListR)
    else : v = min(ListR)
    for i in range (len(ListR)):
        if Résultats[i][0]==v:return Résultats[i]

################################################################################
'''Dessine la grille de jeu, et le cote graphique et affiche le score des participants'''

def Dessine():
    global finPartie, mode,game_justStart
    if game_justStart==True:
        canvas.create_image (0,0,image = img_accueil , anchor = "nw", state="normal" )
        PlaceButtons()
    if game_justStart==False:
        canvas.delete("all")
        for i in range (7):
            canvas.create_rectangle(i*100,0,i*100+100,600,activefill="darkblue",fill="blue",outline="blue")

        if PIA!=(8,8):
            canvas.create_oval(PIA[0]*100+5,PIA[1]*100+5,PIA[0]*100+95,PIA[1]*100+95,fill="white")
        if PHU!=(8,8):
            canvas.create_oval(PHU[0]*100+5,PHU[1]*100+5,PHU[0]*100+95,PHU[1]*100+95,fill="white")
        if PIAV!=(8,8):
            canvas.create_oval(PIAV[0]*100+5,PIAV[1]*100+5,PIAV[0]*100+95,PIAV[1]*100+95,fill="white")
        for pions in PionsGagnants :
            canvas.create_rectangle(pions[0]*100,pions[1]*100,pions[0]*100+100,pions[1]*100+100,fill="cyan")
        for x in range(7):
            for y in range(6):
                xc = x * 100
                yc = y * 100
                canvas.create_oval(xc+10,yc+10,xc+90,yc+90,fill="white",state="disabled")
                if(Grille[x][y]==1):
                    canvas.create_oval(xc+10,yc+10,xc+90,yc+90,fill="red",dash=True)
                if(Grille[x][y]==2):
                    canvas.create_oval(xc+10,yc+10,xc+90,yc+90,fill="yellow",dash=True)
                if(Grille[x][y]==3):
                    canvas.create_oval(xc+10,yc+10,xc+90,yc+90,fill='#34C924',dash=True)

        canvas.create_image ( 700 , 0 , image = img_bois , anchor = "nw", state="normal" )
        AfficheScore()
        AfficheMode()
        if finPartie :
            AfficheResult()

####################################################################################

'''Permet de placer des pions a l'endroit clique et de faire jouer l'IA'''
def MouseClick(event):
    global Grille,debutPartie,PionsGagnants,score_IA,score_H,mode,PHU,PIA,PIAV,finPartie,game_justStart, Player
    Window.focus_set()
    #Convertit une coordonée pixel écran en coord grille de jeu
    x = event.x // 100
    y = event.y // 100
    if game_justStart:
        return
    #Si c'est le debut de partie on remet la grille a 0
    if debutPartie:
        recommence()
        debutPartie=False
        if mode == 4 : Player = 2
        else : Player = 1
    if not finPartie:
        if Grille[x][y]!=0:
            return
        if mode <= 3 :
            coup=PlacementJetons(x,Grille)
            Grille[coup[0]][coup[1]]=1
            PHU=coup
            #Si le joeuur gagne
            if Win(Grille,4,1,coup[0],coup[1]):
                print("win")
                score_H+=1
                PionsGagnants = pions_gagnants(Grille,1,coup[0],coup[1])
                finPartie = True
            else:

                if mode==1:
                    #Placement du jetons du joueur jaune
                    print("Mode : Placement Judicieux (Rouge,Jaune,Vert)")
                    xA,yA=PlacementJudicieux(Grille,2)[0][1]
                    Grille[xA][yA]=2
                    PIA = xA,yA
                    if Win(Grille,4,2,xA,yA):
                        score_IA+=1
                        print("IA Win")
                        PionsGagnants = pions_gagnants(Grille,2,xA,yA)
                        finPartie=True
                    else:
                        #Placement du jetons du joueur vert
                        xAV,yAV=PlacementJudicieux2(Grille)[0][1]
                        Grille[xAV][yAV]=3
                        PIAV=xAV,yAV
                        if AlignementCarre(Grille,4,3,xAV,yAV):
                            print("IA Win mais IA verte")
                            score_IA+=1
                            PionsGagnants = carregagnant(Grille,3,xAV,yAV)
                            finPartie=True

                elif mode==2:
                    print("Mode : Simulation (Rouge,Jaune) - Placement Judicieux (Vert)")
                    xA,yA= MinMax(Grille,2,1)[1]
                    Grille[xA][yA]=2
                    PIA = xA,yA
                    if Win(Grille,4,2,xA,yA):
                        print("IA Win")
                        score_IA+=1
                        PionsGagnants = pions_gagnants(Grille,2,xA,yA)
                        finPartie=True
                    else:
                        xAV,yAV=PlacementJudicieux2(Grille)[0][1]
                        Grille[xAV][yAV]=3
                        PIAV=xAV,yAV
                        if AlignementCarre(Grille,4,3,xAV,yAV):
                            print("IA Win mais IA verte")
                            score_IA+=1
                            PionsGagnants = carregagnant(Grille,3,xAV,yAV)
                            finPartie=True

                elif mode == 3 :
                    print("Mode : Simulation (Rouge,Jaune)")
                    xA,yA= MinMax(Grille,2,1)[1]
                    Grille[xA][yA]=2
                    PIA = xA,yA
                    if Win(Grille,4,2,xA,yA):
                        print("IA Win")
                        score_IA+=1
                        PionsGagnants = pions_gagnants(Grille,2,xA,yA)
                        finPartie=True

                elif mode == 0 :
                    print("Mode : Placement Judicieux (Rouge,Jaune)")
                    xA,yA=PlacementJudicieux(Grille,2)[0][1]
                    Grille[xA][yA]=2
                    PIA = xA,yA
                    if Win(Grille,4,2,xA,yA):
                        score_IA+=1
                        print("IA Win")
                        PionsGagnants = pions_gagnants(Grille,2,xA,yA)
                        finPartie=True

        elif mode == 4 :
            if Player == 1 : Player =2
            elif Player == 2 : Player = 1
            coup=PlacementJetons(x,Grille)
            Grille[coup[0]][coup[1]]=Player
            if Player== 1 : PHU=coup
            elif Player == 2 : PIA = coup
            #Si le joeuur gagne
            if Win(Grille,4,Player,coup[0],coup[1]):
                print("win")
                if Player == 1 : score_H+=1
                elif Player == 2 : score_IA+=1
                PionsGagnants = pions_gagnants(Grille,Player,coup[0],coup[1])
                finPartie = True

        if MatchNul(Grille):
            finPartie=True

        pygame.mixer.music.load("assets/jeton.mp3")
        pygame.mixer.music.play()
    Dessine()
    print("clicked at", x,y)
canvas.bind('<ButtonPress-1>',    MouseClick)

#####################################################################################
'''Bouton et interface a droite'''

#Permet de recommencer une partie et de remettre la grille a 0
def recommence():
    global debutPartie,Grille,PionsGagnants,PHU,PIA,PIAV,finPartie
    debutPartie = True
    PionsGagnants=[]
    PHU = (8,8)
    PIA = (8,8)
    PIAV = (8,8)
    Grille=Grille=np.zeros((7,6),dtype='int')
    finPartie=False
    Dessine()

#Permet de revenir au menu
def Menu():
    global game_justStart,score_H,score_IA
    score_IA,score_H=0,0
    game_justStart=True
    recommence()

#Permet de passer de l'ecran d'accueil a l'ecran du jeu
def start():
    global game_justStart
    game_justStart=False
    Dessine()
    PlaceButtons()

#Permet de choisir le mode de jeu
def GameMode(x):
    global mode,score_H,score_IA
    score_IA=0
    score_H=0
    mode=x
    start()

#Liste des boutons
btn_restart = tk.Button(Window, text = 'Restart', width = 20, height = 2, command = recommence)
btn_menu = tk.Button(Window, text = 'Menu', width = 20, height = 2, command=Menu)
btn_quitter = tk.Button(Window, text = 'Quitter', width = 20, height = 2, command = Window.destroy)

btn_leave=tk.Button(Window, text = 'Quitter', width = 20, height = 2, command = Window.destroy)
btn_modeRJ=tk.Button(Window,text='Mode 1v1v1 \n  Sans Mode Simulation',width=20,height=2, command=lambda:GameMode(1))
btn_modeSimu=tk.Button(Window,text='Mode 1v1v1 \n  Avec Mode Simulation',width=20,height=2, command=lambda:GameMode(2))
btn_mode1v1=tk.Button(Window,text='Mode 1v1 \n  Avec Mode Simulation',width=20,height=2, command=lambda:GameMode(3))
btn_mode1v1SansSimu=tk.Button(Window,text='Mode 1v1 \n  Sans Simulation',width=20,height=2, command=lambda:GameMode(0))
btn_1v1Manuel=tk.Button(Window,text='Mode 1v1 \n  Joueur vs Joueur',width=20,height=2, command=lambda:GameMode(4))

#Permet de placer les boutons
def PlaceButtons():
    global game_justStart
    if game_justStart:
        #Placement des boutons
        btn_modeRJ.place(x=500,y=200)
        btn_modeSimu.place(x=700,y=200)
        btn_mode1v1.place(x=700,y=280)
        btn_mode1v1SansSimu.place(x=500,y=280)
        btn_1v1Manuel.place(x=500,y=360)
        btn_leave.place(x=700,y=360)

        #Efface les boutons existants
        btn_menu.place_forget()
        btn_quitter.place_forget()
        btn_restart.place_forget()
    else:
        #Efface les boutons de la page d'accueil
        btn_mode1v1.place_forget()
        btn_modeRJ.place_forget()
        btn_modeSimu.place_forget()
        btn_mode1v1SansSimu.place_forget()
        btn_leave.place_forget()
        btn_1v1Manuel.place_forget()

        #Placement des boutons
        btn_restart.place(x=725, y=400)
        btn_menu.place(x=725, y=450)
        btn_quitter.place(x=725, y=500)

img_bois = tk.PhotoImage ( file = 'assets/bois.png' )
img_accueil=tk.PhotoImage(file='assets/Ecran_accueil.png')

PoliceTexte = tkfont.Font(family='Arial', size=30, weight="bold", slant="italic")
PoliceTexte1 = tkfont.Font(family='Arial', size=40, weight="bold", slant="italic")
PoliceTexte2 = tkfont.Font(family='Arial', size=20, weight="bold", slant="italic")
PoliceTexte3 = tkfont.Font(family='Arial', size=7, weight="bold", slant="italic")

#####################################################################################
'''Mise en place de l'interface - ne pas toucher'''

AfficherPage(0)
Dessine()
Window.mainloop()