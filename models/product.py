from db import db


class ProductModel(db.Model):
    __tablename__='products'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80))
    price=db.Column(db.Float(precision=2))


    def __init__(self, name, price):
        self.name=name
        self.price=price
    
    def json(self):
        return {'name': self.name, 'price': self.price}



    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


    

    def upsert(self):
        db.session.add(self)
        db.session.commit()


    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    
