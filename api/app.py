from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os

# import sys
# sys.path.append('..')
# from marketwatch import MarketWatch
from marketwatch import MarketWatch

# Initialize FastAPI and Jinja2
app = FastAPI(docs_url="/docs", redoc_url=None)

current_directory = os.path.dirname(os.path.abspath(__file__))
templates=Jinja2Templates(directory=os.path.join(current_directory, "templates"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    try:
        mw = MarketWatch(credentials.username, credentials.password)
        # Optionally, you could check some property or call some method on mw to ensure it's valid
        return mw
    except Exception as e:
        # Log the error here if you want
        raise HTTPException(status_code=401, detail="MarketWatch validation failed")

@app.get("/")
def read_root(request: Request):
    return "Marketwatch API"

@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game(request: Request, game_id: str, mw: MarketWatch = Depends(get_current_user)):
    data = mw.get_game(game_id=game_id)
    return templates.TemplateResponse("game.html.j2", {"request": request, "data": data})

@app.get("/portfolio/{game_id}", response_class=HTMLResponse)
async def portfolio(request: Request, game_id: str, mw: MarketWatch = Depends(get_current_user)):
    data = mw.get_portfolio(game_id=game_id)
    return templates.TemplateResponse("portfolio.html.j2", {"request": request, "data": data})

@app.get("/leaderboard/{game_id}", response_class=HTMLResponse)
async def leaderboard(request: Request, game_id: str, mw: MarketWatch = Depends(get_current_user)):
    data = mw.get_leaderboard(game_id=game_id)
    return templates.TemplateResponse("leaderboard.html.j2", {"request": request, "data": data})

@app.get("/card/{game_id}", response_class=HTMLResponse)
async def card(request: Request, game_id: str, mw: MarketWatch = Depends(get_current_user)):
    data = mw.get_game(game_id=game_id)
    return templates.TemplateResponse("card.html.j2", {"request": request, "data": data})

@app.get("/watchlist/{watchlist_id}", response_class=HTMLResponse)
async def watchlists(request: Request, watchlist_id: str, mw: MarketWatch = Depends(get_current_user)):
    data = mw.get_watchlist(watchlist_id=watchlist_id)
    return templates.TemplateResponse("watchlists.html.j2", {"request": request, "data": data})
