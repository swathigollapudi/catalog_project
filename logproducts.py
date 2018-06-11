from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from myproject import Onlineshopping, Base, Products, User


engine = create_engine('sqlite:///shopping.db')


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



User1 = User(name="swathi", email="15pa1a0548@vishnu.edu.in",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()



shoppingwebsite1 = Onlineshopping(user_id=1, name="flipkart")

session.add(shoppingwebsite1)
session.commit()


product1 = Products(user_id=1, name="costumes",price="$3",
                          course="textiles", shoppingwebsite=shoppingwebsite1)

session.add(product1)
session.commit()

product2 = Products(user_id=1, name="Washing Machine",price="$10.50",
                          course="homeappiliances", shoppingwebsite=shoppingwebsite1)

session.add(product2)
session.commit()

product3 = Products(user_id=1, name="Mobilephone",price="$5",
                          course="electronic gadgets", shoppingwebsite=shoppingwebsite1)

session.add(product3)
session.commit()


product4 = Products(user_id=1, name="Perfume",price="$1.50",
                          course="cosmetics", shoppingwebsite=shoppingwebsite1)

session.add(product4)
session.commit()



shoppingwebsite2 = Onlineshopping(user_id=1, name="Amazon")

session.add(shoppingwebsite2)
session.commit()


product1 = Products(user_id=1, name="Blankets",price="$5",
                          course="textiles", shoppingwebsite=shoppingwebsite2)

session.add(product1)
session.commit()

product2 = Products(user_id=1, name="Mixy",price="$7.50",
                          course="homeappiliances", shoppingwebsite=shoppingwebsite2)

session.add(product2)
session.commit()

product3 = Products(user_id=1, name="laptop",price="$25",
                          course="electronic gadgets", shoppingwebsite=shoppingwebsite2)

session.add(product3)
session.commit()


product4 = Products(user_id=1, name="Makupkit",price="$2.50",
                          course="cosmetics", shoppingwebsite=shoppingwebsite2)

session.add(product4)
session.commit()


shoppingwebsite3 = Onlineshopping(user_id=1, name="Ebay")

session.add(shoppingwebsite3)
session.commit()


product1 = Products(user_id=1, name="LalchiPaijama",price="$1",
                          course="textiles", shoppingwebsite=shoppingwebsite3)

session.add(product1)
session.commit()

product2 = Products(user_id=1, name="Refrigerator",price="$17.50",
                          course="homeappiliances", shoppingwebsite=shoppingwebsite3)

session.add(product2)
session.commit()

product3 = Products(user_id=1, name="Ipad",price="$35",
                          course="electronic gadgets", shoppingwebsite=shoppingwebsite3)

session.add(product3)
session.commit()


product4 = Products(user_id=1, name="Nailpolish",price="$1",
                          course="cosmetics", shoppingwebsite=shoppingwebsite3)

session.add(product4)
session.commit()
                          

                          

                          
