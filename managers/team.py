from models.location import Region, Commune
from models.staff import WorkArea, Employment, Person, PhonePerson, Employee

from datetime import datetime

class TeamManager:

    @staticmethod
    async def get_regions(db):
        return db.query(Region).all()

    @staticmethod
    async def get_communes_by_region(db, region):   
        return db.query(Commune).filter_by(region=region).all()
    
    @staticmethod
    async def get_work_areas(db):
        return db.query(WorkArea).all()
    
    @staticmethod
    async def get_employment_by_work_area(db, area):
        return db.query(Employment).filter_by(area=area).all()

    @staticmethod
    async def create_new_staff(db, results):
        person = Person(
            first_name = results['first_name'],
            last_name = results['last_name'],
            rut = results['rut'],
            email = results['email'],
            address_name = results['address_name'],
            address_number = results['address_number'],
            commune = results['commune'],
            region = results['region'],
            country = "Chile"
        )
        db.add(person)
        db.commit()
        db.refresh(person)

        phone_person = PhonePerson(
            phone = results['phone'],
            person = person.id
        )
        db.add(phone_person)
        db.commit()

        employee = Employee(
            start_date = datetime.strptime(results['start_date'], "%m/%d/%Y"),
            end_date = datetime.strptime(results['end_date'], "%m/%d/%Y"),
            person = person.rut,
            employment = results['employment'],
            area = results['work_area']
        )
        db.add(employee)
        db.commit()

    @staticmethod
    async def get_team(db):
        return db.query(Person, Employee, PhonePerson).join(Employee, Employee.person == Person.rut).join(PhonePerson, PhonePerson.person == Person.id).all()
    
    @staticmethod
    async def delete_team_member(db, id):
        member = db.query(Person).filter_by(id = id).first()
        db.delete(member)
        db.commit()