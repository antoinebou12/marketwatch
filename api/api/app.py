"""Marketwatch API"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from marketwatch import MarketWatch


MARKETWATCH_USERNAME = os.environ.get("MARKETWATCH_USERNAME")
MARKETWATCH_PASSWORD = os.environ.get("MARKETWATCH_PASSWORD")
MARKETWATCH_GAME_ID = os.environ.get("MARKETWATCH_GAME_ID")

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game(request: Request, game_id: str = MARKETWATCH_GAME_ID):
    """
    Get the current marketwatch data

    :param request: The request object
    :return: The marketwatch data
    """
    mw = MarketWatch(MARKETWATCH_USERNAME, MARKETWATCH_PASSWORD)
    data = mw.get_game(game_id=game_id)
    return templates.TemplateResponse("game.html.j2", {"request": request, "data": data})

@app.get("/portfolio/{game_id}", response_class=HTMLResponse)
async def portfolio(request: Request, game_id: str = MARKETWATCH_GAME_ID):
    """
    Get the current marketwatch data

    :param request: The request object
    :return: The marketwatch data
    """
    mw = MarketWatch(MARKETWATCH_USERNAME, MARKETWATCH_PASSWORD)
    data = mw.get_portfolio(game_id=game_id)
    return templates.TemplateResponse("porfolio.html.j2", {"request": request, "data": data})

@app.get("/leaderboard/{game_id}", response_class=HTMLResponse)
async def leaderboard(request: Request, game_id: str = MARKETWATCH_GAME_ID):
    """
    Get the current marketwatch data

    :param request: The request object
    :return: The marketwatch data
    """
    mw = MarketWatch(MARKETWATCH_USERNAME, MARKETWATCH_PASSWORD)
    data = mw.get_leaderboard(game_id=game_id)
    return templates.TemplateResponse("leaderboard.html.j2", {"request": request, "data": data})


@app.get("/card/{game_id}", response_class=HTMLResponse)
async def card(request: Request, game_id: str = MARKETWATCH_GAME_ID):
    """
    Get the current marketwatch data

    :param request: The request object
    :return: The marketwatch data
    """
    mw = MarketWatch(MARKETWATCH_USERNAME, MARKETWATCH_PASSWORD)
    game = mw.get_game(game_id=game_id)

    return templates.TemplateResponse("card.html.j2", {"request": request, "data": game})



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
