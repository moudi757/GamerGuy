
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, VARCHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# SQLAlchemy is about three components which are Table, Mapper and a Class object
#Declarative is used to define all three instead of having to code everything from scratch
#Base jere os defined by a Declratibe method to help us with creating tables and mapping them
Base = declarative_base()

#The engine is used to enable us to establish a connection and interaction with the Database 
#The choice here is MySQL but SQLAlchemy is open to operating with a lot of options out there like SQLlite
engine = create_engine('mysql+mysqldb://root:@localhost/gamerguy')



#################################################################

#Class company will represent the table named Company in the Database
#It has an id and a name which names will mapp accordingly to the database implementation
#Company has a one to many relationship with table Creator  
class Company(Base):
	__tablename__ = 'Company' 
	id = Column(Integer, primary_key=True, unique=True)
	name = Column(VARCHAR(100))
  


#################################################################


#Creator is connected to Company through a one to many relationship with Creator being the many side
#Creator is also connected to Game through a many to many realtionship

class Creator(Base):
    __tablename__ = 'Creator'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100))
    # a ForeighKey is required here to establish a connection between table Creator and table Company in the databse
    company_id = Column(Integer, ForeignKey('Company.id'))
    #Creator is connected to table Company with the relationship method provided by SQLAlchemy library using the attribute backref to creat the relation'creators'
    #meaning: company has many creators
    company = relationship(Company, backref=backref('creators', uselist=True))
    #Creator is connected to table Game with the relationship method and arrtibute secondary refers to a final table which represents this relationship 
    #and is also built in the databse
    games = relationship('Game', secondary='creator_game')
		

#################################################################

#Class Game represents the games that are made by creators and is connected to the table Creator through a many to many relationship 
#Game will also have a declaration of the method relationship with attribute secondary to define the many to many relationship "creator_game" with table Creator
class Game(Base):
	__tablename__ = "Game"
	id= Column(Integer, primary_key=True)
	name= Column(VARCHAR(100))
	creators = relationship('Creator', secondary='creator_game')


#################################################################

#Class CreatorGame that represents the table which is the many to many relationship between Creator and Game is built with a composite primary key 
#that is made of two foreignkeys each referrs to the primary key in its corresponding table
class CreatorGame(Base):
	__tablename__= 'creator_game'
	creator_id = Column(Integer, ForeignKey('Creator.id'), primary_key=True)
	game_id = Column(Integer, ForeignKey('Game.id'), primary_key=True)


#################################################################

#session is also a part of the sqlalchemy library and as the name suggests, it creates the session that through, the script communicates with the database
Session = sessionmaker(bind=engine)
session = Session()
#The following method creates all the tables in the engine and it is equavilant to CREATE TABLE in raw SQL
Base.metadata.create_all(engine)
#bind engine means that it binds the engine to the metadata of Base so the declaraties (Table, Mappers, Classes) can be accessed
#through an instance of the session
Base.metadata.bind = engine


#################################################################
##This is a helper class that uses the concepts of OOP to make acheiving tasks less repetative
class callDB():
	# this function will make sure that entered value to the database is a nonexisting new value
	def callQ(self, x,y):
		r = 0
		while  r == 0:
			find_Comp_name = session.query(x).filter(x.name==y).first()
			if(find_Comp_name != None):
				print("Please enter another name:")
				y = input()
			else:
				r = 1
		return y

	#this function will add new values to each of the three tables Company, Creator and Game
	#and they will be mapped together using the logic provided by sqlalchemy library 
	def addNew(self, x, y, z):
		newcompany = Company(name=x)
		newcreator = Creator(name=y)
		newgame = Game(name=z)
		#add the new values to the corresponding tables
		session.add(newcompany)
		session.add(newcreator)
		session.add(newgame)
		#logically mapping tables together through the corresponding table relationships
		newgame.creators.append(newcreator)
		newcreator.company = newcompany
		#the final step which is required to admit all the changes to the database 
		#the changes can be undo with by calling: session.rollback()
		session.commit()


	#this function adds a new game while it has an existing creator mention in the databse
	def addToExistCreator(self, x, y):
		newgame = Game(name=x)
		#this query calls the existing creator and uses it as an object to append the new game on
		creator_Object = session.query(Creator).filter(Creator.name ==y).first()
		if(creator_Object != None):
			session.add(newgame)
			newgame.creators.append(creator_Object)
			session.commit()
			print('Game added')
		else:
			print('Creator Not found')

	# this function demonstrates some SQLAlchemy queries to show how quering differs from the raw SQL quering 
	def execQueries(self):

		print("This is a block of Queries################################")
		query1 = session.query(Creator).all()
		for x in query1:
			print("Creator id: " , x.id , "Creator name: ", x.name)

		print()
		# value in filter can be changed according to your inputs 
		query2 = session.query(Company).filter(Company.name == "Konami").first()
		print("Company id:" ,query2.id ,"Company's name:",query2.name, "Employee name: ",query2.creators[0].name)

		print()
		#value in filter can be changed according to your inputs 
		query3 = session.query(Game).filter(Game.name=='MetalGear').one()
		print("Game id:", query3.id, " Game name:", query3.name, "Game creator:", query3.creators[0].name)
		print()

		query4 = session.query(Game).all()
		for x in query4:
			print("Game id:", x.id, " Game name:", x.name, "Game creator:", x.creators[0].name)

		print()

		query5 = session.query(Creator).join(Creator.company).all()
		for x in query5:
			print("Creator id: ", x.id , "Creator name: ", x.name, "company's id: " ,x.company_id, "company's name:", x.company.name)

		quer6 = session.query(Creator).join(Creator.games).group_by(Game.id)
		for x in query5:
			print("Creator name: ",x.name, " Game name:", x.games[0].name)




#################################################################


# initiates class callDB()
calldb = callDB()

# This mechanisim is used to help the user choose either to input new values or add a game to an existing creator
#A lot more could have been done here like adding creator to Existing Company and so but 
#to avoid repetation the case of adding Game was most descriptive to show what is required
print("To add a new Company, Creator and Game press: N")
print("To add a new Game to an existing Creator press: E")
pressedVal = input()
if(pressedVal == 'N'):
	print("Please Enter Company's Name:")
	Compname= input()
	Comp_name = calldb.callQ(Company,Compname)

	print("Please Enter Creator's Name:")
	Creatorname= input()
	Creator_name = calldb.callQ(Creator, Creatorname)

	print("Please Enter Games's Name:")
	Gamename= input()
	Game_name = calldb.callQ(Game, Gamename)

	calldb.addNew(Comp_name,Creator_name,Game_name)

elif(pressedVal== 'E'):
	print("Please Enter Games's Name:")
	Game_name= input()
	print("Please Enter Creator's Name:")
	Creator_name= input()
	calldb.addToExistCreator(Game_name, Creator_name)
else:
	print("you pressed something wrong")
	quit()


# calls a bunch of queries to show interaction with the databse
calldb.execQueries()

