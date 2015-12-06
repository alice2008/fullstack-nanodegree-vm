from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Catalog, Item, User

engine = create_engine('sqlite:///catalogitemwithuser.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# session.delete(User)
# session.delete(Catalog)
# session.delete(Item)
# Create dummy user
User1 = User(name="John Smith", email="john_smith@abc.com", picture="http://www.digyourowngrave.com/content/worlds_fluffiest_kitten.jpg")
session.add(User1)
session.commit()

#
Catalog1 = Catalog(user=User1, name='Soccer')
session.add(Catalog1)

Item1 = Item(user=User1, name='Soccer Ball', description='A ball used in the sport of soccer.', catalog=Catalog1)
session.add(Item1)

Item1 = Item(user=User1, name='Soccer Cleats', description='An external attachment to the soccer shoe to provide additional tranction on a soft or slippery surface', catalog=Catalog1)
session.add(Item1)

Item1 = Item(user=User1, name='Jersey', description='A shirt worn by a member of a team.', catalog=Catalog1)
session.add(Item1)

Item1 = Item(user=User1, name='Shoes', description='Shoes worn by the soccer member', catalog=Catalog1)
session.add(Item1)

Item1 = Item(user=User1, name='Socks', description='Socks worn by the soccer member', catalog=Catalog1)
session.add(Item1)
session.commit()

#
Catalog2 = Catalog(user=User1, name='Hockey')
session.add(Catalog2)

Item1 = Item(user=User1, name='Helmet', description='A helmet with strap, and optionally a face cage or visor, is required of all ice hockey players. Hockey helmets come in various sizes, and many of the older designs can also be adjusted by loosening or fastening screws at the side or at the back. Ice hockey helmets are made of a rigid but flexible thermoplastic outer shell, usually nylon or ABS, with firm vinyl nitrile foam padding inside to reduce shocks. Even with the helmet and visor/face cage, concussions and facial injuries are common injuries in the sport.', catalog=Catalog2)
session.add(Item1)

Item1 = Item(user=User1, name='Neck Guard', description='A neck guard typically consists of a series of nylon or ABS plates for puncture resistance, with padding for comfort and fit and a tear-resistant nylon mesh outer covering.', catalog=Catalog2)
session.add(Item1)

Item1 = Item(user=User1, name='Ice Skates', description='Hockey skates incorporate a rigid shell, form-fit to the player\'s foot using memory foam and/or heat-moldable components, often reinforced with metal mesh to prevent a skate blade cutting through.', catalog=Catalog2)
session.add(Item1)
session.commit()

#
Catalog3 = Catalog(user=User1, name='Skiing')
session.add(Catalog3)

Item1 = Item(user=User1, name='Ski Helmet', description='A helmet specifically designed and constructed for winter sports. ', catalog=Catalog3)
session.add(Item1)

Item1 = Item(user=User1, name='Ski Poles', description='Ski poles, also referred to as Poles, are used by skiers for balance and propulsion. ', catalog=Catalog3)
session.add(Item1)

Item1 = Item(user=User1, name='Ski', description='A narrow strip of semi-rigid material worn underfoot to glide over snow. ', catalog=Catalog3)
session.add(Item1)

Item1 = Item(user=User1, name='Ski Boots', description='Ski boots are footwear used in skiing to provide a way to attach the skier to skis using ski bindings.', catalog=Catalog3)
session.add(Item1)
session.commit()

print "added items!"