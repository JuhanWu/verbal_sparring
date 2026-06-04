"""Pydantic schemas for the matches API."""

from pydantic import BaseModel


class CreateMatchRequest(BaseModel):
    """Request body for creating a new match.

    Attributes:
        opponent: Either ``"npc"`` (case-insensitive) for an AI match, or
            the username of a registered human opponent.
    """

    opponent: str


class MatchResponse(BaseModel):
    """Response payload returned after a match is created.

    Attributes:
        match_id: UUID of the newly created match as a string.
        opponent: The opponent value echoed from the request.
        is_npc: True when the opponent is an NPC (AI), False otherwise.
    """

    match_id: str
    opponent: str
    is_npc: bool
