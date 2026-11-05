import uuid
from dataclasses import dataclass, asdict, replace


@dataclass
class User:
    first_name: str = "Ivan"
    last_name: str = "Petrov"
    address: str = "Svetlanskaya 1"
    city: str = "Vladivostok"
    state: str = "Primorsky"
    zip_code: str = "690000"
    phone: str = "+79001234567"
    ssn: str = "123-45-6789"
    username: str = ""
    password: str = "Passw0rd!123"
    confirm: str = ""

    def __post_init__(self):
        if not self.username:
            self.username = f"qa_{uuid.uuid4().hex[:10]}"
        if not self.confirm:
            self.confirm = self.password

    def with_(self, **changes) -> "User":
        """Копия пользователя с изменёнными полями."""
        return replace(self, **changes)

    def as_dict(self):
        return asdict(self)


def make_user(**overrides) -> User:
    return User(**overrides)
