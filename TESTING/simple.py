from teachablerobots.src.GridSpace import *



G = GridSpace("")

while(not G._finished):
    G.Update(G.FrameOverlay)
    G.ShowFrame(False)
