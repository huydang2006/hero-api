# Mai Huy Đăng - 11247269

**Question 1.** For each of the four statements, which constraint blocked it (`PRIMARY KEY` ,`UNIQUE` ,`NOT NULL` ,`FOREIGN KEY`) and why?

- 1 was blocked by `UNIQUE`, a team called `Avengers` already exists.
- 2 was blocked by `FOREIGN KEY`, no team `99` exists.
- 3 was blocked by `NOT NULL`, the name column is `NOT NULL`.
- 4 was blocked by `FOREIGN KEY`, `Tony` and `Natasha` still reference team `1`, so deleting it would leave orphan rows.

**Question 2.** The relationship team → hero is **one-to-many**. Why is the foreign key on `hero` and not on `team`?

- One team has many heroes, but each hero belongs to only one team.

**Question 3.** Heroes can go on many missions and a mission has many heroes (**many-to-many**). Sketch the tables you need (names, columns, PK, FK). Hint: you need a **link table**.

```python
hero(id PK, name, age, ...)
mission(id PK, title)
hero_mission(
  hero_id    FK -> hero.id,
  mission_id FK -> mission.id,
  PRIMARY KEY (hero_id, mission_id)
)
```

**Question 4.** Why read the URL from an environment variable instead of writing it in `database.py`? Give two reasons.

1. *Security:* Credentials hardcoded in code end up in Git history, where anyone with repo access can read them. An environment variable keeps the password out of the repo.
2. *Configurability:* The same code runs against different databases (local dev, a separate test database, production) by changing only the variable, with no code edits or redeploys.

**Question 5.** Why is `id` typed `int | None` with `default=None`, when every row in the database has an id?

- Before the insert, the Python object has no id yet. The database generates it (`SERIAL`) at INSERT.
- `id` is `None` when create `Hero(...)` and gets filled in after `commit()` and `refresh()`. Typing it as `int` with no default would force user to supply an id up front.

**Question 6.** Which attributes of `Hero` become **columns**, and which one does not? What is `back_populates` for?

- `id`, `name`,`age`, `team_id` and `secret_name` become columns.
- `team` does not, because `Relationship()` is only a Python-side link. Only `team_id` is stored.
- `back_populates` names the matching attribute on the other class (`Hero.team` <-> `Team.heroes`), so both sides stay in sync: setting `hero.team = avengers` also adds the hero to `avengers.heroes`.

**Question 7.** Compare the `CREATE TABLE hero` printed by SQLAlchemy with the one you wrote by hand in Part 1. List the differences (types, `NOT NULL` , indexes, constraints).

- **Extra column:** SQLModel adds `secret_name VARCHAR NOT NULL`, which the hand-written table didn't have.
- **Index:** SQLModel runs `CREATE INDEX ix_hero_name ON hero (name)` because of `Field(index=True)`. The manual table had no index on `name`.
- **Constraint style**: SQLModel writes `PRIMARY KEY (id)` and `FOREIGN KEY(team_id) REFERENCES team (id)` as table-level clauses, while the hand-written SQL used inline (`id SERIAL PRIMARY KEY`, `team_id INTEGER REFERENCES team(id)`). They mean the same thing, but the constraint names differ.
- **Types and nullability:** these match. `id` is `SERIAL NOT NULL`, `name` is `VARCHAR NOT NULL`, and `age` and `team_id` are nullable.
- **Unique on team:** for `team.name`, `unique=True` together with `index=True` gives a unique index (`ix_team_name`) instead of the `UNIQUE` constraint written by hand.

**Question 8.** Stop and restart the server. Is `CREATE TABLE` printed again? Why? What does `create_all` do when a table already exists?

- No. `create_all` first checks the database for each table (`SELECT ... pg_catalog` queries in the echo output). Tables that already exist are skipped, and only missing tables are created. It never alters or drops existing tables, which is why a new column on an existing model isn't added.

**Question 9.** `create_all` only knows about models that have been **imported**. Which line in `main.py` makes sure `Hero` and `Team` are registered?

- `from app import models`. Importing the module runs the class definitions, and each `table=True` class registers itself in `SQLModel.metadata`. `create_all` only creates the tables in that metadata. Without the import, it would create nothing.

**Question 10.** Comment out `session.commit()` in `create_hero` and create a hero. What does the response look like, and is the row in the database (`SELECT * FROM hero;`)? Put the line back. What does `add()` do on its own, and why do we need `refresh()`?

- Response: looks normal (`201` with the hero's data), or a 500 error if `refresh()` fails on an unsaved object
- Database: `SELECT * FROM hero;` shows no new row
- Terminal log: `INSERT` followed by `ROLLBACK`, since the session closes without a commit
- `add()` only stages the object in the session; nothing is permanent until `commit()`
- `refresh()` reloads the object after the commit so it holds database-generated values (the `id`)

**Question 11.** Which SQL statement does `echo=True` print for `PATCH` with body `{"age": 17}`? Does it update every column or only `age`? Why?

- SQL printed: `UPDATE hero SET age=... WHERE hero.id = ...`
- Only the `age` column is updated
- `model_dump(exclude_unset=True)` keeps only the fields the client sent
- SQLAlchemy also tracks changed attributes and writes only those

**Question 12.** Look at the JSON returned by `GET /heroes/{id}`. Is `secret_name` there? Which line of code is responsible?

- Not present in the JSON
- Responsible line: `response_model=HeroPublic` in the route decorator
- `HeroPublic` has no `secret_name` field, so FastAPI filters it out of the response

**Question 13.** Call `GET /heroes?min_age=18&team_id=1` and copy the `SELECT` printed by `echo=True`. Where do the values `18` and `1` appear? Why is this safe against **SQL injection**?

```sql
SELECT hero.name, hero.age, hero.team_id, hero.power, hero.id, hero.secret_name
FROM hero
WHERE hero.age >= %(age_1)s::INTEGER AND hero.team_id = %(team_id_1)s::INTEGER
```

- `18` and `1` are not in the SQL. They are sent on the next line as bind parameters: `{'age_1': 18, 'team_id_1': 1}`. The SQL only holds placeholders (`%(age_1)s`).
- The SQL and the data are sent separately, so a value is never parsed as SQL. Something like `18; DROP TABLE hero--` is only data for the placeholder, never executed.

**Question 14.** Why filter in the database instead of `[h for h in session.exec(select(Hero)).all() if h.age >= 18]`?

- The list comprehension downloads **every** row first, then throws most away. A `WHERE` clause filters on the server and returns only matching rows.
- The database can use an index instead of a full scan, and memory usage stays small no matter how big the table gets.

**Question 15.** On restart, `create_all` did create `mission` and `heromissionlink`. In Part 4 it did nothing for `hero`. What is the rule?

- `create_all` only creates tables that are **missing** (like `CREATE TABLE IF NOT EXISTS`). It never alters or drops existing tables.
- So `hero` and `team` were skipped, while `mission` and `heromissionlink` were created. The same rule explains why a new model field needs a migration.

**Question 16.** You never set `team_id` in the seed script. Read the echo=True output: in which order were the `INSERT`s executed, and how did `hero.team_id` get its value?

- Order: `team` (2×) → `mission` (2×) → `hero` (6×) → `heromissionlink` (4×).
- SQLAlchemy sorts inserts by foreign key: referenced tables go first, so no FK error happens.
- `team_id` comes from `Hero(team=avengers)`. The team is inserted first, its generated `id` returns, and SQLAlchemy writes that id into `hero.team_id` before inserting the hero.

**Question 17.** Is there a `power` column? Now call `GET /heroes`. What happens and why? Why is "drop all tables and run `create_all` again" not an acceptable fix in production?

- No. `create_all` does not alter existing tables, so `power` is missing.
- `GET /heroes` returns `500`: the query selects `hero.power` and PostgreSQL raises `UndefinedColumn`.
- Dropping all tables deletes every row — irreversible data loss. A migration adds only the new column and keeps the data.
- After `alembic upgrade head` the column exists and the endpoint works again.

**Question 18.** Copy the bodies of `upgrade()` and `downgrade()`. What does each one do?

```python
def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('hero', sa.Column('power', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('hero', 'power')
```

- `upgrade()` runs `ALTER TABLE hero ADD COLUMN power VARCHAR` — nullable, so existing rows are untouched.
- `downgrade()` runs `ALTER TABLE hero DROP COLUMN power` — the schema goes back, but anything stored in `power` is lost.

**Question 19.** Where does Alembic store "which revision this database is at"? (Hint: `\dt`.) Why should the `migrations/` folder be committed to Git?

- In the table `alembic_version` (one row, one column `version_num`). `\dt` lists it next to the other tables. It currently holds `69b38f0f83a1`.
- With `migrations/` in Git, anyone can clone the repo and run `alembic upgrade head` to get the exact schema. Schema changes are also reviewable in the commit history.

**Question 20.** Rename `secret_name` to `alias` in the model and run `revision --autogenerate` (do not apply it). What did Alembic generate? Why is that dangerous for existing data, and how would you fix the script?

- Alembic does not detect a rename. It saw one column removed and one added:

  ```python
  def upgrade() -> None:
      op.add_column('hero', sa.Column('alias', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
      op.drop_column('hero', 'secret_name')

  def downgrade() -> None:
      op.add_column('hero', sa.Column('secret_name', sa.VARCHAR(), autoincrement=False, nullable=False))
      op.drop_column('hero', 'alias')
  ```

- Dangerous: `DROP COLUMN` deletes all stored values. Running it loses every `secret_name`, and the downgrade only recreates an empty column.
- Fix: replace both commands with a rename that keeps the data:

  ```python
  op.alter_column('hero', 'secret_name', new_column_name='alias')
  ```
  
  (emits `ALTER TABLE hero RENAME COLUMN secret_name TO alias`).
- The test revision was then deleted and the field renamed back: history is again `<base> -> 69b38f0f83a1 (head)`.
