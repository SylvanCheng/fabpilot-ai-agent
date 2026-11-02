from fabpilot.core.settings import EnvSettings


class FabDataSettings(EnvSettings):
    # The role behind this URL must only have SELECT (see db/init).
    business_db_url: str = "postgresql+psycopg://fab_reader:fab_reader@localhost:5432/fab_business"
