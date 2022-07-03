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
    
class FileService():
    def is_Permission(self,userlogin_id,File_id):
        userlogin_id= int(userlogin_id)
        File_id=int(File_id)
        pic= FileModel.query.filter(FileModel.userlogin_id==userlogin_id,
                            FileModel.id==File_id).first()
        return not not pic

    def insert(self,userlogin_id,pic):
        File = FileModel(userlogin_id=userlogin_id,pic=pic)
        db.session.add(File)
        try:
            db.session.flush()
            db.session.refresh(File)
            File.pic= str(File.userlogin_id)+"/"+str(File.id)+"_"+File.pic
            db.session.merge(File)
            db.session.commit()
            return File
        except exc.SQLAlchemyError:
            db.session.rollback()
            return None;
    def getByUserID(self,userlogin_id):
        # lay toan bo anh cua user
        pics= FileModel.query.filter(FileModel.userlogin_id==userlogin_id)
        return pics
    def searchByPicID(self,userlogin_id,File_id):
        # lay thong tin cua anh duoc chia se toi user
        u = AuthService().getByID(userlogin_id)
        # tim trong list anh da su hu
        for pic in u.Files:
            if(pic.id==File_id):
                return pic
        # tim trong list share
        for sh in u.shares:
            if(sh.File_id==File_id):
                return sh.File
        # ko tim thay
        return None
    def getPicByID(self,File_id):
        return FileModel.query.get(int(File_id))

class ShareService():
    def getByUserID(self,userlogin_id):
        # lay File share cho user_id
        shares = ShareFileModel.query.filter(ShareFileModel.userlogin_id==userlogin_id)
        return shares
    
    
    def searchByPicID(self,File_id):
        shares =ShareFileModel.query.filter(ShareFileModel.File_id==File_id)
        return shares

    def searchAvailableUser(self,File_id):
        pic =FileModel.query.get(File_id)
        shares = pic.shares
        list = [sh.userlogin_id for sh in shares]
        list.append(pic.userlogin_id)# append them id chu? File
        users= UserLoginModel.query.filter(UserLoginModel.id.notin_(list)).all()
        return users
    
    
    def insertMore(self,File_id,list_user):
        for userlogin_id in list_user:
            self.insert(File_id,userlogin_id)
        try:
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False;
        
    def insert(self,File_id,userlogin_id):
        share = ShareFileModel(File_id=File_id,
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
    
    def remove(self,File_id,userlogin_id):
        share = ShareFileModel.query.filter(ShareFileModel.File_id==File_id,
                    ShareFileModel.userlogin_id==userlogin_id).first()
        if not share:
            return False
        db.session.delete(share)
        try:
            db.session.commit()
            return True
        except exc.SQLAlchemyError:
            db.session.rollback()
            return False;
        


    
