from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Hero,
    HeroCreate,
    HeroPublic,
    HeroStatus,
    HeroUpdate,
    Mission,
    MissionPublic,
    Team,
)

router = APIRouter(prefix="/heroes", tags=["heroes"])


def get_hero_or_404(session, hero_id: int) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


def check_team_exists(session, team_id: int | None) -> None:
    if team_id is not None and session.get(Team, team_id) is None:
        raise HTTPException(
            status_code=400,
            detail=f"Team {team_id} does not exist",
        )


@router.post(
    "",
    response_model=HeroPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a hero",
    responses={400: {"description": "Team does not exist"}},
)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    """Create a new hero (400 if the team does not exist)."""
    check_team_exists(session, hero_in.team_id)
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.get("", response_model=list[HeroPublic], summary="List heroes")
def list_heroes(
    session: SessionDep,
    team_id: int | None = None,
    min_age: int | None = Query(default=None, ge=0, le=1000),
    name: str | None = None,
    status_filter: HeroStatus | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    """List heroes with optional filters and pagination."""
    query = select(Hero).order_by(Hero.id)
    if team_id is not None:
        query = query.where(Hero.team_id == team_id)
    if min_age is not None:
        query = query.where(Hero.age >= min_age)
    if name is not None:
        query = query.where(Hero.name.ilike(f"%{name}%"))
    if status_filter is not None:
        query = query.where(Hero.status == status_filter)
    return session.exec(query.offset(offset).limit(limit)).all()


@router.get(
    "/{hero_id}",
    response_model=HeroPublic,
    summary="Get a hero",
    responses={404: {"description": "Hero not found"}},
)
def read_hero(hero_id: int, session: SessionDep):
    """Return a single hero by id, or 404 if it does not exist."""
    return get_hero_or_404(session, hero_id)


@router.patch(
    "/{hero_id}",
    response_model=HeroPublic,
    summary="Update a hero partially",
    responses={
        400: {"description": "Team does not exist"},
        404: {"description": "Hero not found"},
    },
)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    """Update the fields the client sent; the rest keep their values."""
    hero = get_hero_or_404(session, hero_id)
    changes = hero_in.model_dump(exclude_unset=True)
    check_team_exists(session, changes.get("team_id"))
    hero.sqlmodel_update(changes)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete(
    "/{hero_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hero",
    responses={404: {"description": "Hero not found"}},
)
def delete_hero(hero_id: int, session: SessionDep):
    """Delete a hero and return 204 No Content."""
    hero = get_hero_or_404(session, hero_id)
    session.delete(hero)
    session.commit()


@router.post(
    "/{hero_id}/missions/{mission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign a hero to a mission",
    responses={
        404: {"description": "Hero or mission not found"},
    },
)
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    """Link a hero to a mission (many-to-many), if not linked already."""
    hero = get_hero_or_404(session, hero_id)
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()


@router.get(
    "/{hero_id}/missions",
    response_model=list[MissionPublic],
    summary="List a hero's missions",
    responses={404: {"description": "Hero not found"}},
)
def list_hero_missions(hero_id: int, session: SessionDep):
    """List every mission assigned to a hero."""
    hero = get_hero_or_404(session, hero_id)
    return hero.missions
