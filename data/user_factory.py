import uuid
from dataclasses import dataclass

from faker import Faker

fake = Faker()


@dataclass
class User:
    first_name: str
    last_name: str
    dob: str
    street: str
    house_number: str
    postal_code: str
    city: str
    state: str
    country: str
    phone: str
    email: str
    password: str


def create_user() -> User:
    
    unique = uuid.uuid4().hex[:12]
    return User(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        dob="1995-05-15",                          
        street=fake.street_name(),
        house_number=str(fake.random_int(1, 99)),
        postal_code=fake.numerify("#####"),
        city=fake.city(),
        state=fake.state(),
        country="KZ",
        phone=fake.numerify("##########"),         
        email=f"qa.{unique}@example.com",
        password=f"Qz9!{uuid.uuid4().hex[:12]}",   
    )


SEEDED_CUSTOMER = {
    "email": "customer@practicesoftwaretesting.com",
    "password": "welcome01",
    "display_name": "Jane Doe",     
}


BILLING_ADDRESS = {
    "country": "IT",
    "street": "Via Roma",
    "house_number": "9",
    "postal_code": "30100",
    "city": "Venezia",
    "state": "VE",
}