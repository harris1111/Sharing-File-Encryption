from venv import create
from models import *
from sqlalchemy import exc
import pandas as pd
import hashSHAsalt
class AuthService():
    def login(self,username,password):
        username = username.strip()
        password = password.strip()
        engine = create_engine("mysql+pymysql://root@localhost/crypto_project?charset=utf8mb4")
        print(password)
        sql = "select password from userlogin where username = '" + username+"'"
        df = pd.read_sql(sql, con=engine)
        password_hashed = df.password[0]
        print(password_hashed)
        print(hashSHAsalt.matchHashedText(password_hashed,password))
        u = UserLoginModel.query.filter(UserLoginModel.username==username,
            UserLoginModel.password==password_hashed).first()
        return u
    def getByID(self,userlogin_id):
        return UserLoginModel.query.get(int(userlogin_id))
    def getAll(self):
        return UserLoginModel.query.all()
    def getByUsername(self,username):
        return  UserLoginModel.query.filter(UserLoginModel.username==username).first()
    def register(self,username,password,fullname):
        u = UserLoginModel(username=username,password=password,fullname=fullname)
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
        return u
    
class PictureService():
    def is_Permission(self,userlogin_id,picture_id):
        userlogin_id= int(userlogin_id)
        picture_id=int(picture_id)
        pic= PictureModel.query.filter(PictureModel.userlogin_id==userlogin_id,
                            PictureModel.id==picture_id).first()
        return not not pic

    def insert(self,userlogin_id,pic):
        picture = PictureModel(userlogin_id=userlogin_id,pic=pic)
        db.session.add(picture)
        try:
            db.session.flush()
            db.session.refresh(picture)
            picture.pic= str(picture.userlogin_id)+"/"+str(picture.id)+"_"+picture.pic
            db.session.merge(picture)
            db.session.commit()
            return picture
        except exc.SQLAlchemyError:
            db.session.rollback()
            return None;
    def getByUserID(self,userlogin_id):
        # lay toan bo anh cua user
        pics= PictureModel.query.filter(PictureModel.userlogin_id==userlogin_id)
        return pics
    def searchByPicID(self,userlogin_id,picture_id):
        # lay thong tin cua anh duoc chia se toi user
        u = AuthService().getByID(userlogin_id)
        # tim trong list anh da su hu
        for pic in u.pictures:
            if(pic.id==picture_id):
                return pic
        # tim trong list share
        for sh in u.shares:
            if(sh.picture_id==picture_id):
                return sh.picture
        # ko tim thay
        return None
    def getPicByID(self,picture_id):
        return PictureModel.query.get(int(picture_id))

class ShareService():
    def getByUserID(self,userlogin_id):
        # lay picture share cho user_id
        shares = SharePictureModel.query.filter(SharePictureModel.userlogin_id==userlogin_id)
        return shares
    
    
    def searchByPicID(self,picture_id):
        shares =SharePictureModel.query.filter(SharePictureModel.picture_id==picture_id)
        return shares

    def searchAvailableUser(self,picture_id):
        pic =PictureModel.query.get(picture_id)
        shares = pic.shares
        list = [sh.userlogin_id for sh in shares]
        list.append(pic.userlogin_id)# append them id chu? picture
        users= UserLoginModel.query.filter(UserLoginModel.id.notin_(list)).all()
        return users
    
    
    def insertMore(self,picture_id,list_user):
        for userlogin_id in list_user:
            self.insert(picture_id,userlogin_id)
        try:
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False;
        
    def insert(self,picture_id,userlogin_id):
        share = SharePictureModel(picture_id=picture_id,
                      userlogin_id=userlogin_id)
        try:  
            db.session.add(share)
            db.session.flush()
            db.session.refresh(share)
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False;
        return share
    
    def remove(self,picture_id,userlogin_id):
        share = SharePictureModel.query.filter(SharePictureModel.picture_id==picture_id,
                    SharePictureModel.userlogin_id==userlogin_id).first()
        if not share:
            return False
        db.session.delete(share)
        try:
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False;
        


    
