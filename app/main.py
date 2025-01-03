import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.fetcher import fetch_profile, fetch_scores
from app.models import predict_scores, train_model
from app.utils import df_to_json, dict_to_json, is_valid_id

app = FastAPI()

# schemas
class Recommendation(BaseModel):
  leaderboardId: str
  songId: str
  cover: str
  fullCover: str
  name: str
  subName: Optional[str]
  author: str
  mapper: str
  bpm: float
  duration: int
  difficultyName: str
  type: str
  stars: float
  passRating: float
  accRating: float
  techRating: float
  starsMod: float
  passRatingMod: float
  accRatingMod: float
  techRatingMod: float
  status: str
  rank: Optional[int]
  timeAgo: Optional[str]
  currentMods: Optional[List[str]]
  predictedMods: Optional[List[str]]
  currentAccuracy: float
  predictedAccuracy: float
  accuracyGained: float
  currentPP: float
  predictedPP: float
  maxPP: float
  unweightedPPGain: float
  weightedPPGain: float
  weight: float

class Profile(BaseModel):
  id: str
  name: str
  alias: str
  avatar: str
  country: str
  pp: float
  rank: int
  countryRank: int

class ProfileAndRecommendations(BaseModel):
  profile: Profile
  recs: List[Recommendation]

@app.get("/recommendations/{player_id}", response_model=ProfileAndRecommendations)
async def get_recommendations(player_id: str):
  if not is_valid_id(player_id):
    raise HTTPException(status_code=404, detail="Player does not exist.")
  
  try:
    print(f"[{player_id}] Fetching profile...")
    player_dict = fetch_profile(player_id)

    print(f"[{player_id}] Fetching scores...")
    maps_df = pd.read_csv("./app/ranked_maps.csv")
    scores_df = fetch_scores(player_id)
  except:
    raise HTTPException(status_code=500, detail="Failed to fetch player data.")

  print(f"[{player_id}] Predicting scores...")
  model = train_model(scores_df)
  pred_df = predict_scores(model, scores_df, maps_df)
  
  player_json = dict_to_json(player_dict)
  pred_json = df_to_json(pred_df)

  return { 
    "profile": player_json, 
    "recs": pred_json 
  }
