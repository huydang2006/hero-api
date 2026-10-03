from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import Hero, Mission, Team


def seed() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if session.exec(select(Team)).first() is not None:
            print("Database already seeded — nothing to do.")
            return

        avengers = Team(name="Avengers", headquarters="New York")
        xmen = Team(name="X-Men", headquarters="Westchester")

        sokovia = Mission(title="Battle of Sokovia")
        new_york = Mission(title="Battle of New York")

        heroes = [
            Hero(name="Tony", age=45, secret_name="Iron Man", team=avengers,
                 missions=[sokovia]),
            Hero(name="Natasha", age=35, secret_name="Black Widow", team=avengers,
                 missions=[sokovia, new_york]),
            Hero(name="Steve", age=110, secret_name="Captain America", team=avengers,
                 missions=[new_york]),
            Hero(name="Logan", age=150, secret_name="Wolverine", team=xmen),
            Hero(name="Ororo", age=32, secret_name="Storm", team=xmen),
            Hero(name="Peter", age=16, secret_name="Spider-Man"),
        ]

        session.add(avengers)
        session.add(xmen)
        session.add(sokovia)
        session.add(new_york)
        session.add_all(heroes)
        session.commit()

        print(f"Seeded {len(heroes)} heroes, 2 teams and 2 missions.")


if __name__ == "__main__":
    seed()
