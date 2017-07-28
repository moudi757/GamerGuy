
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, VARCHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import MySQLdb


#############################################################################################################################################################
##SECTION 1: DEFINING THE CLASSES THAT REPRESENT THE DATABASE
#############################################################################################################################################################

#Declarative base is used to create and mapp the classes which are tables in the database
Base = declarative_base()
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
# a ForeighKey is required here to establish a connection between table Creator and table Company in the databse
#Creator is connected to table Company with the relationship method provided by SQLAlchemy library using the attribute backref to creat the relation'creators'
#meaning: company has many creators
#Creator is connected to table Game with the relationship method and arrtibute secondary refers to a final table which represents this relationship 
#and is also built in the databse
class Creator(Base):
    __tablename__ = 'Creator'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100))
    company_id = Column(Integer, ForeignKey('Company.id'))
    company = relationship(Company, backref=backref('creators', uselist=True))
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




##########################################################################################################################################################
##SECTION 2: DEFINING THE CLASS USED TO INTERACT WITH THE DATABASE - (CREATE DB, INSERT INTO DB, QUERY DB)
##########################################################################################################################################################

##This is a helper class that uses the concepts of OOP to make acheiving tasks less repetative
class callDB():

	def creatDB(self):
		db1 = MySQLdb.connect(host="localhost",user="root",passwd="")
		cursor = db1.cursor()
		sql = 'CREATE DATABASE GamerGuy'
		cursor.execute(sql)

	# this function will make sure that entered value to the database is a nonexisting new value
	def callQ(self, x,y, session):
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
	def addNew(self, x, y, z, session):
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
	def addToExistCreator(self, x, y, session):
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
	def execQueries(self, session):

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
		query3 = session.query(Game).filter(Game.name=='Metal Gear Solid').one()
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


#############################################################################################################################################################
##SECTION 3: DEFINING THE CLASS WHICH HAS THE MAIN METHOD THAT DRIVES THE EXECTION OF THE SCRIPT
#############################################################################################################################################################

class runningProgram():

		
		def runProgram(self):
			calldb = callDB()
			calldb.creatDB()
			engine = create_engine('mysql+mysqldb://root:@localhost/gamerguy')
			Session = sessionmaker(bind=engine)
			sessionN = Session()
			#The following method creates all the tables in the engine and it is equavilant to CREATE TABLE in raw SQL
			Base.metadata.create_all(engine)
			#bind engine means that it binds the engine to the metadata of Base so the declaraties (Table, Mappers, Classes) can be accessed
			#through an instance of the session
			Base.metadata.bind = engine
			#inserting NEW data into empty database
			Compname= "Konami"
			Comp_name = calldb.callQ(Company,Compname, sessionN)
			Creatorname= "Kojima"
			Creator_name = calldb.callQ(Creator, Creatorname, sessionN)
			Gamename= "Metal Gear Solid"
			Game_name = calldb.callQ(Game, Gamename,sessionN)
			calldb.addNew(Comp_name,Creator_name,Game_name, sessionN)
			#inserting a game to an existing creator
			Game_name2="Death Stranding"
			Creator_name2="Kojima"
			calldb.addToExistCreator(Game_name2, Creator_name2,sessionN)
			#Calling Queries from Database
			calldb.execQueries(sessionN)


################################################################################################################################################################
## SECTION 4: RUNNING THE SCRIPT
################################################################################################################################################################

executeProgram = runningProgram()
executeProgram.runProgram()

