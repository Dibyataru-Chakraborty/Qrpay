#------------------
# See Requirements


import csv
import json
import random
import re
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pyrebase
import qrcode
import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from resizeimage import resizeimage

from welcome import Ui_Form

#Enter Your Firebase details
firebaseConfig = {
                                'apiKey': "#",
                                'authDomain': "#",
                                'database_url' : "#",
                                'projectId': "#",
                                'storageBucket': "#",
                                'messagingSenderId': "#",
                                'appId': "#",
                                'measurementId': "#"
                            }
fire = pyrebase.initialize_app(firebaseConfig)
auth = fire.auth()
db = fire.database()

#---otp
lcase="abcdefghijklmnopqrstuvwxyz"
ucase="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
number="0123456789"
symbol="@#"
otp_lenght = 6
transaction = 16

#pincode
api = "https://api.postalpincode.in/pincode/"

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

date_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class MainWindow(QtWidgets.QWidget,Ui_Form):

    #----------login
    def login(self):
        if self.w_login.isChecked():
            self.widget_login.hide()
            self.widget_welcome.show()
            self.widget_register_details.hide()
            self.widget_register.hide()
            self.widget_qrpay.hide()
            self.frame.show()
            self.widget_forget.hide()
        else:
            self.widget_welcome.hide()
            self.widget_qrpay.hide()
            self.widget_register.hide()
            self.widget_login.show()
            self.frame.show()
            self.widget_register_details.hide()
            self.widget_forget.hide()

    #----------login_frame
    def login_function(self):
        if self.l_email.text()=='' or self.l_password.text()=='':
            QMessageBox.warning(self.widget_login,'Warning','All Fields Are Rquired')
        else:
            try:
                #fire = pyrebase.initialize_app(firebaseConfig)
                email = self.l_email.text()
                password =  self.l_password.text()
                auth.sign_in_with_email_and_password(email, password)
                self.qrpay()
                find = db.child('Employ')
                upi = find.order_by_child("email").equal_to(email).get()
                s = smtplib.SMTP('smtp.gmail.com', 587)           
                s.starttls()#security           
                s.login("email", "password")#login smtp #See requirements           
                msg=MIMEMultipart()#message
                msg['From'] = "email"  #See requirements 
                msg['To'] = email
                msg['Subject'] = "LOGIN SUCCESSFULL"
                day = self.dateTimeEdit.dateTime().toString('MM/dd/yyyy  h:mm:ss')
                for employe in upi.each():
                    up_i = employe.val()['upi']
                    self.q_upi.setText(up_i)
                    name=employe.val()['f_name']
                message = 'Hello, '+'\n\n\t\tWe Noticed a New Login,'+name+'\n\n'+'\t\t\t\t'+day+'\n\nYou Have successfully logged in'+'\n\n\nThanks,\n\nYour QrPay team'
                msg.attach(MIMEText(message, 'plain'))               
                s.sendmail("email", email, msg.as_string()) #See requirements 
                QMessageBox.information(self.widget_login,'Welcome','Login Successfull')
            except Exception  as es:
                exc = es.args[1]
                ex = json.loads(exc)["error"]["message"]
                QMessageBox.warning(self.widget_login,'Error',ex)
    
    def forget_function(self):
        email = self.l_email.text()
        if email =='':
            QMessageBox.warning(self.widget_login,'Warning','All Fields Are Rquired')
        else:
            if email.endswith('@gmail.com'): 
                find = db.child('Employ')
                emai = email.removesuffix('@gmail.com')
                if find.order_by_key().equal_to(emai).get().val():
                    self.widget_welcome.hide()
                    self.widget_register.hide()
                    self.widget_login.hide()
                    self.widget_forget.show()
                    self.frame.show()
                    self.widget_qrpay.hide()
                    self.widget_register_details.hide()
                    self.f_resend.setEnabled(False)
                    s = smtplib.SMTP('smtp.gmail.com', 587)
                    s.starttls()# start TLS for security
                    s.login("email", "password")# Authentication  #See requirements
                    #-- otp
                    ad_ans = lcase+ucase+number+symbol
                    self.otp = "".join(random.sample(ad_ans,otp_lenght))
                    msg=MIMEMultipart()
                    msg['From'] = "email" #See requirements
                    msg['To'] = email
                    msg['Subject'] = "Password Reset For QrPay"
                    message = 'Hello '+',\n\nYour otp is '+str(self.otp)+'\nThanks,\n\nYour QrPay team'# add in the message body
                    msg.attach(MIMEText(message, 'plain'))
                    s.sendmail("email", email, msg.as_string())# sending the mail''' #See requirements
                    QMessageBox.information(self.widget_forget,"OTP","OTP has been sent to your Email")  
                    self.f_otp.setText('')         
                else:
                    QMessageBox.warning(self.widget_login,'Warning','Please Enter the Valid email to reset password')
            else:
                QMessageBox.warning(self.widget_login,'Warning','Invalid Email')

    def resend_otp(self):
        ad_ans = lcase+ucase+number+symbol
        self.re_otp = "".join(random.sample(ad_ans,otp_lenght))
        print(self.re_otp)
        email = self.l_email.text()
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()# start TLS for security    
        s.login("email", "password")# Authentication      #See requirements       
        msg=MIMEMultipart()
        msg['From'] = "email" #See requirements
        msg['To'] = email
        msg['Subject'] = "Password Reset Otp For QrPay"        
        message = 'Hello '+',\n\nYour otp is '+str(self.re_otp)+'\nThanks,\n\nYour QrPay team'# add in the message body
        msg.attach(MIMEText(message, 'plain'))
        s.sendmail("email", email, msg.as_string())# sending the mail #See requirements
        QMessageBox.information(self.widget_forget,"OTP","OTP has been sent to your Email")
        self.f_otp.setText('')

    def send_otp(self):
        if self.f_otp.text()=='':
            QMessageBox.warning(self.widget_forget,'Warning','All Fields Are Rquired')
        else:
            try:
                if self.f_otp.text()==self.otp:
                    QMessageBox.information(self.widget_forget,'OTP',"OTP is Verified")
                    auth = fire.auth()
                    email = self.l_email.text()
                    auth.send_password_reset_email(email)
                    self.login()
                    QMessageBox.information(self.widget_login,'Password Reset',"A link has been sent to your email for reset password")
                    self.f_otp.setText('')
                elif self.f_otp.text()==self.re_otp:
                    QMessageBox.information(self.widget_forget,'OTP',"OTP is Verified")
                    auth = fire.auth()
                    email = self.l_email.text()
                    auth.send_password_reset_email(email)
                    self.login()
                    QMessageBox.information(self.widget_login,'Password Reset',"A link has been sent to your email for reset password")
                    self.f_otp.setText('')
            except:
                self.f_resend.setEnabled(True)
                QMessageBox.warning(self.widget_forget,"OTP","Wrong otp\nPlease enter correct otp")
                self.f_otp.setText('')

    #----------QrPay
    def qrpay(self):
        self.widget_welcome.hide()
        self.widget_register_details.hide()
        self.widget_register.hide()
        self.widget_login.hide()
        self.widget_forget.hide()
        self.frame.hide()
        self.widget_qrpay.show()        
        self.q_c_widget.hide()           
        self.q_p_widget.show()
        self.q_qr_widget.hide()
        self.q_widget_profile.hide()
        self.widget_history.hide()
        self.widget_search.hide()

    #------Qr Generate
    def Gene_rate(self):
        if self.q_customer_name.text()=='' or self.q_customer_Phone.text()=='' or self.q_amount.text()=='':
            QMessageBox.warning(self.widget_qrpay,"Error","All Fields Are Rquired")
        elif self.q_amount.text().startswith('-'or'/'or'+'or'*'):
            QMessageBox.warning(self.widget_qrpay,"Error","Amount Cannot be start with '-'")
        else:
            self.q_c_widget.hide()           
            self.q_p_widget.show()
            self.q_widget_profile.hide()
            self.q_qr_widget.show()
            qr_data=('upi://pay?pa=')+str(self.q_upi.text())+('&mode=02&am=')+str(self.q_amount.text())
            qr_code=qrcode.make(qr_data)
            qr_code=resizeimage.resize_cover(qr_code,[171,151])
            qr_code.save("Customer/Code/Customer "+str(self.q_customer_name.text())+'.png')
            self.im=QPixmap("Customer/Code/Customer "+str(self.q_customer_name.text())+'.png')
            self.q_qr_code.setPixmap(self.im)            

    def screen_clear(self):
        self.q_p_widget.show()
        self.q_qr_widget.hide()
        self.q_payment.setCurrentText('Select')
        self.q_customer_name.setText('')
        self.q_customer_Phone.setText('')
        self.q_amount.setText('')
        self.q_p_1p.setText('0')
        self.q_p_1pn.setText('')
        self.q_p_1n.setText('0')
        self.q_p_2p.setText('0')
        self.q_p_2pn.setText('')
        self.q_p_2n.setText('0')
        self.q_p_3p.setText('0')
        self.q_p_3pn.setText('')
        self.q_p_3n.setText('0')
        self.q_p_4p.setText('0')
        self.q_p_4pn.setText('')
        self.q_p_4n.setText('0')
        self.q_p_5p.setText('0')
        self.q_p_5pn.setText('')
        self.q_p_5n.setText('0')
        self.q_p_6p.setText('0')
        self.q_p_6pn.setText('')
        self.q_p_6n.setText('0')
        self.q_p_7p.setText('0')
        self.q_p_7pn.setText('')
        self.q_p_7n.setText('0')
        self.q_p_8p.setText('0')
        self.q_p_8pn.setText('')
        self.q_p_8n.setText('0')
        self.q_p_9p.setText('0')
        self.q_p_9pn.setText('')
        self.q_p_9n.setText('0')
        self.q_p_10p.setText('0')
        self.q_p_10pn.setText('')
        self.q_p_10n.setText('0')
        self.q_p_11p.setText('0')
        self.q_p_11pn.setText('')
        self.q_p_11n.setText('0')
        self.q_p_12p.setText('0')
        self.q_p_12pn.setText('')
        self.q_p_12n.setText('0')
        QMessageBox.information(self.widget_qrpay,"Successful","All Fields Are Cleared")
        
    def save_data(self):
        if self.q_upi.text()=='' or self.q_customer_name.text()=='' or self.q_customer_Phone.text()=='' or self.q_amount.text()=='' or self.q_payment.currentText()=='Select' or self.q_reference.text()=='':
            QMessageBox.warning(self.widget_qrpay,"Error","All Fields Are Rquired")
        else:
            p=self.q_payment.currentText()
            email =  self.l_email.text()
            c_upi = self.q_upi.text()
            c_name = self.q_customer_name.text()
            c_phone = self.q_customer_Phone.text()
            c_amount = self.q_amount.text()
            c_reference = self.q_reference.text()
            day = self.dateTimeEdit.dateTime().toString('MM/dd/yyyy  h:mm:ss')
            product = (self.q_p_1pn.text()+'    '+self.q_p_2pn.text()+'     '+self.q_p_3pn.text()+'     '+self.q_p_4pn.text()+'     '+self.q_p_5pn.text()+'     '+self.q_p_6pn.text()+'     '+self.q_p_7pn.text()+'     '+self.q_p_8pn.text()+'        '+self.q_p_9pn.text()+'      '+self.q_p_10pn.text()+'        '+self.q_p_11pn.text()+'        '+self.q_p_12pn.text())
            payment_firebase = db.child('Payment details')

            data = ({"email":email,'date' : day, 'customer' : c_name, 'customer_phone' : c_phone, 'upi' : c_upi,'amount' : c_amount, 'reference' : c_reference,'payment' : p,'product':product})
            payment_firebase.push(data)

            s='\n'+day+'\t'+'||'+'\t'+str(self.q_upi.text())+'\t'+'||'+'\t'+str(self.q_customer_name.text())+'\t'+'||'+'\t'+str(self.q_customer_Phone.text())+'\t'+'||'+'\t '+str(self.q_amount.text()+'\t'+'||'+'\t '+c_reference+'\t'+'||'+'\t '+p+'\t'+'||'+'\t '+product)
            f = open(('Customer/Payment-Details/Text/PaymentDeatails.txt'), 'a')
            f.write(s)
            f.close()
            
            with open('Customer/Payment-Details/Excel/PaymentDeatails.csv', 'a') as fs:
                data = [day,c_upi,c_name,c_phone,c_amount,c_reference,p,product]
                w = csv.writer(fs)
                w.writerow(data)
                fs.close()
            QMessageBox.information(self.widget_qrpay,"Successfull","Successfully Save")

    #------calculator
    def calculator(self):
        self.q_qr_widget.hide()
        self.q_c_widget.show()
        self.q_widget_profile.hide()
    def calculator_close(self):
        self.q_c_widget.hide()
    def cal(self,num):       
        xnum=self.q_c_display.text()+str(num)
        self.q_c_display.setText(xnum)            
    def equal(self):       
        equal=""
        try:
            equal = self.q_c_display.text()
            self.q_c_display.setText(str(eval(equal)))
        except:
            QMessageBox.warning(self.widget_qrpay,'Error',"Wrong Input in Calculator")
    def c(self):
        self.q_c_display.setText('')
    def backscpace(self):
        self.q_c_display.setText(self.q_c_display.text()[0:-1])

    def pr_total(self):
        try:
            total = float(
                        (float(self.q_p_1p.text())*float(self.q_p_1n.text()))+
                        (float(self.q_p_2p.text())*float(self.q_p_2n.text()))+
                        (float(self.q_p_3p.text())*float(self.q_p_3n.text()))+
                        (float(self.q_p_4p.text())*float(self.q_p_4n.text()))+
                        (float(self.q_p_5p.text())*float(self.q_p_5n.text()))+
                        (float(self.q_p_6p.text())*float(self.q_p_6n.text()))+
                        (float(self.q_p_7p.text())*float(self.q_p_7n.text()))+
                        (float(self.q_p_8p.text())*float(self.q_p_8n.text()))+
                        (float(self.q_p_9p.text())*float(self.q_p_9n.text()))+
                        (float(self.q_p_10p.text())*float(self.q_p_10n.text()))+
                        (float(self.q_p_11p.text())*float(self.q_p_11n.text()))+
                        (float(self.q_p_12p.text())*float(self.q_p_12n.text()))
                    ) 
            self.q_amount.setText(str(total))
        except:
            None

    #----------register
    def register(self):
        if self.w_register.isChecked():
            self.widget_login.hide()
            self.widget_welcome.show()
            self.widget_qrpay.hide()
            self.frame.show()
            self.widget_register.hide()
            self.widget_register_details.hide()
            self.widget_forget.hide()
        else:
            self.widget_welcome.hide()
            self.widget_register.show()
            self.widget_qrpay.hide()
            self.widget_login.hide()
            self.frame.show()
            self.widget_register_details.hide()
            self.widget_forget.hide()

    #---------register_details
    def register_function(self):
        self.email = self.s_email.text()
        self.password = self.s_password.text()
        self.confirm_password = self.s_confirm_password.text()
        if self.email=='' or self.password=='':
            QMessageBox.warning(self.widget_register,"Error","All Fields Are Rquired")
        elif self.password!=self.confirm_password:
            QMessageBox.warning(self.widget_register,"Warning","Password mismatch")
        elif len (self.password)<8:
            QMessageBox.warning(self.widget_register,"Error","Password should be minimum 8 Letter")
        else:
            try:
                if self.email.endswith('@gmail.com'): 
                    find = db.child('Employ')
                    emai = self.email.removesuffix('@gmail.com')
                    if find.order_by_key().equal_to(emai).get().val():
                        self.widget_welcome.hide()
                        self.widget_register.show()
                        self.frame.show()
                        self.widget_register_details.hide()
                        self.widget_login.hide()
                        self.widget_forget.hide()
                        self.widget_qrpay.hide()
                        QMessageBox.warning(self.widget_register,'Warning','Email Already Exist')
                    else:
                        self.widget_welcome.hide()
                        self.widget_register.hide()
                        self.widget_qrpay.hide()
                        self.widget_register_details.show()
                        self.frame.hide()
                        self.widget_login.hide()
                        self.widget_forget.hide()
                        self.r_email.setText(self.email)
                        self.r_password.setText(self.password)
                        QMessageBox.information(self.widget_register_details,'Welcome','Please Register your details to continue')
                else:
                    QMessageBox.warning(self.widget_register,'Warning','Invalid Email')                    
            except:
                self.widget_welcome.hide()
                self.widget_register.hide()
                self.widget_qrpay.hide()
                self.widget_register_details.show()
                self.frame.hide()
                self.widget_login.hide()
                self.widget_forget.hide()
                self.r_email.setText(self.email)
                self.r_password.setText(self.password)
                QMessageBox.information(self.widget_register_details,'Welcome','Please Register your details to continue')

    def register_details(self):
        if self.r_first_name.text()=='' or self.r_last_name.text()=='' or self.r_phone_number.text()=='' or self.r_upi.text()=='' or self.r_comboBox.currentText()=='Select' or self.r_answer.text()=='':
            QMessageBox.warning(self.widget_register_details,"Error","All Fields Are Rquired")
        elif "@" not in self.r_upi.text():
            QMessageBox.warning(self.widget_register_details,"Error","Enter valid upi")
        else:
            s = smtplib.SMTP('smtp.gmail.com', 587)           
            s.starttls()#security           
            s.login("email", "password")#login smtp    #See requirements         
            msg=MIMEMultipart()#message
            msg['From'] = "email" #See requirements       
            msg['To'] = self.email
            msg['Subject'] = "REGISTRATION SUCCESSFULL"
            message = 'Hello '+',\n\nYour Email id is : '+self.email+' and your password is : '+self.password+'\nThanks,\n\nYour QrPay team'
            msg.attach(MIMEText(message, 'plain'))
            create = auth.create_user_with_email_and_password(self.email,self.password)
            data = ({'email' : self.email, 'f_name' : self.r_first_name.text(), 'shop' : self.r_last_name.text(), 'contact' : self.r_phone_number.text(),'upi' : self.r_upi.text(), 'securityqu' : self.r_comboBox.currentText(), 'securityans' : self.r_answer.text()})
            emai = self.email.removesuffix('@gmail.com')
            db.child('Employ').child(emai).set(data)
            auth.send_email_verification(create['idToken'])
            s.sendmail("email", self.email, msg.as_string()) #See requirements       
            self.login()
            QMessageBox.information(self.widget_login,"Success","Register Successfull")
            
    #---------welcome
    def welcome(self):
        self.widget_welcome.show()
        self.widget_register_details.hide()
        self.widget_register.hide()
        self.widget_login.hide()
        self.widget_forget.hide()
        self.widget_qrpay.hide()
        self.frame.show()

    def logout(self):
        QMessageBox.information(self.widget_qrpay,"Succcessful","Successfylly Logout")
        self.widget_welcome.show()
        self.widget_register_details.hide()
        self.widget_register.hide()
        self.widget_login.hide()
        self.widget_forget.hide()
        self.widget_qrpay.hide()
        self.frame.show()

    def account(self):
        email = self.l_email.text()
        find = db.child('Employ')
        upi = find.order_by_child("email").equal_to(email).get()
        for employe in upi.each():
            s_shop = employe.val()['shop']
            s_email = employe.val()['email']
            s_phone = employe.val()['contact']
            s_upi = employe.val()['upi']
            s_wo_name = employe.val()['f_name']
            self.profile_shop_name.setText(s_shop)
            self.profile_shop_email.setText(s_email)
            self.profile_shop_phone.setText(s_phone)
            self.profile_shop_upi.setText(s_upi)
            self.profile_shop_wo_name.setText(s_wo_name)
        self.profile_save.setEnabled(False)
        self.q_widget_profile.show()
        self.q_c_widget.hide()           
        self.q_p_widget.hide()
        self.q_qr_widget.hide()
        self.dateTimeEdit.hide()
        self.line.hide()
        self.line_2.hide()
        self.pushButton.hide()
        self.q_acc_ount.hide()
        self.q_amount.hide()
        self.q_c.hide()
        self.q_clear.hide()
        self.q_customer_Phone.hide()
        self.q_customer_name.hide()
        self.q_label.hide()
        self.q_log_out.hide()
        self.q_old_details.hide()
        self.q_payment.hide()
        self.q_qr_generate.hide()
        self.q_reference.hide()
        self.q_save.hide()
        self.q_upi.hide()

    def profile_close(self):
        self.q_widget_profile.hide()
        self.q_c_widget.hide()           
        self.q_p_widget.show()
        self.q_qr_widget.hide()
        self.dateTimeEdit.show()
        self.line.show()
        self.line_2.show()
        self.pushButton.show()
        self.q_acc_ount.show()
        self.q_amount.show()
        self.q_c.show()
        self.q_clear.show()
        self.q_customer_Phone.show()
        self.q_customer_name.show()
        self.q_label.show()
        self.q_log_out.show()
        self.q_old_details.show()
        self.q_payment.show()
        self.q_qr_generate.show()
        self.q_reference.show()
        self.q_save.show()
        self.q_upi.show()

    def history_details(self):
        self.widget_search.hide()
        self.widget_history.show()
        self.q_widget_profile.hide()
        self.q_c_widget.hide()           
        self.q_p_widget.hide()
        self.q_qr_widget.hide()
        self.dateTimeEdit.hide()
        self.line.hide()
        self.line_2.hide()
        self.pushButton.hide()
        self.q_acc_ount.hide()
        self.q_amount.hide()
        self.q_c.hide()
        self.q_clear.hide()
        self.q_customer_Phone.hide()
        self.q_customer_name.hide()
        self.q_label.hide()
        self.q_log_out.hide()
        self.q_old_details.hide()
        self.q_payment.hide()
        self.q_qr_generate.hide()
        self.q_reference.hide()
        self.q_save.hide()
        self.q_upi.hide()
        self.load_data()

    def close_history(self):
        self.widget_history.hide()          
        self.q_p_widget.show()
        self.dateTimeEdit.show()
        self.line.show()
        self.line_2.show()
        self.pushButton.show()
        self.q_acc_ount.show()
        self.q_amount.show()
        self.q_c.show()
        self.q_clear.show()
        self.q_customer_Phone.show()
        self.q_customer_name.show()
        self.q_label.show()
        self.q_log_out.show()
        self.q_old_details.show()
        self.q_payment.show()
        self.q_qr_generate.show()
        self.q_reference.show()
        self.q_save.show()
        self.q_upi.show()

    def load_data(self):
        db = fire.database()
        email = self.l_email.text()
        details = db.child('Payment details').order_by_child("email").equal_to(email).get()
        row = 0
        tablerow=0
        for find in details.each():
            all = find.val()
            row+=1
            self.history_tableWidget.setRowCount(row)
            amount = all['amount']
            customer = all['customer']
            customer_phone = all['customer_phone']
            date = all['date']
            payment = all['payment']
            reference = all['reference']
            upi = all['upi']
            p = (amount,customer,customer_phone,date,payment,reference,upi)
            self.history_tableWidget.setItem(tablerow,0,QTableWidgetItem(p[0]))
            self.history_tableWidget.setItem(tablerow,1,QTableWidgetItem(p[1]))
            self.history_tableWidget.setItem(tablerow,2,QTableWidgetItem(p[2]))
            self.history_tableWidget.setItem(tablerow,3,QTableWidgetItem(p[3]))
            self.history_tableWidget.setItem(tablerow,4,QTableWidgetItem(p[4]))
            self.history_tableWidget.setItem(tablerow,5,QTableWidgetItem(p[5]))
            self.history_tableWidget.setItem(tablerow,6,QTableWidgetItem(p[6]))
            tablerow+=1

    def search_details(self):
        self.widget_history.hide()
        self.widget_search.show()
        self.q_widget_profile.hide()
        self.q_c_widget.hide()           
        self.q_p_widget.hide()
        self.q_qr_widget.hide()
        self.dateTimeEdit.hide()
        self.line.hide()
        self.line_2.hide()
        self.pushButton.hide()
        self.q_acc_ount.hide()
        self.q_amount.hide()
        self.q_c.hide()
        self.q_clear.hide()
        self.q_customer_Phone.hide()
        self.q_customer_name.hide()
        self.q_label.hide()
        self.q_log_out.hide()
        self.q_old_details.hide()
        self.q_payment.hide()
        self.q_qr_generate.hide()
        self.q_reference.hide()
        self.q_save.hide()
        self.q_upi.hide()
        self.search_data()

    def search_data(self):
        db = fire.database()
        email = self.l_email.text()
        customer_name = self.search_name.text()
        details = db.child('Payment details').order_by_child("email").equal_to(email).order_by_child('customer').equal_to(customer_name).get()
        row = 0
        tablerow=0
        for find in details.each():
            all = find.val()
            row+=1
            self.search_tableWidget.setRowCount(row)
            amount = all['amount']
            customer = all['customer']
            customer_phone = all['customer_phone']
            date = all['date']
            payment = all['payment']
            reference = all['reference']
            upi = all['upi']
            p = (amount,customer,customer_phone,date,payment,reference,upi)
            self.search_tableWidget.setItem(tablerow,0,QTableWidgetItem(p[0]))
            self.search_tableWidget.setItem(tablerow,1,QTableWidgetItem(p[1]))
            self.search_tableWidget.setItem(tablerow,2,QTableWidgetItem(p[2]))
            self.search_tableWidget.setItem(tablerow,3,QTableWidgetItem(p[3]))
            self.search_tableWidget.setItem(tablerow,4,QTableWidgetItem(p[4]))
            self.search_tableWidget.setItem(tablerow,5,QTableWidgetItem(p[5]))
            self.search_tableWidget.setItem(tablerow,6,QTableWidgetItem(p[6]))
            tablerow+=1

    def close_search(self):
        self.search_name.setText('')
        p=('','','','','','','')
        row=0
        self.search_tableWidget.setItem(row,0,QTableWidgetItem(p[0]))
        self.search_tableWidget.setItem(row,1,QTableWidgetItem(p[1]))
        self.search_tableWidget.setItem(row,2,QTableWidgetItem(p[2]))
        self.search_tableWidget.setItem(row,3,QTableWidgetItem(p[3]))
        self.search_tableWidget.setItem(row,4,QTableWidgetItem(p[4]))
        self.search_tableWidget.setItem(row,5,QTableWidgetItem(p[5]))
        self.search_tableWidget.setItem(row,6,QTableWidgetItem(p[6]))
        row+=1
        self.widget_search.hide()         
        self.q_p_widget.show()
        self.dateTimeEdit.show()
        self.line.show()
        self.line_2.show()
        self.pushButton.show()
        self.q_acc_ount.show()
        self.q_amount.show()
        self.q_c.show()
        self.q_clear.show()
        self.q_customer_Phone.show()
        self.q_customer_name.show()
        self.q_label.show()
        self.q_log_out.show()
        self.q_old_details.show()
        self.q_payment.show()
        self.q_qr_generate.show()
        self.q_reference.show()
        self.q_save.show()
        self.q_upi.show()

    def upi_update(self):
        QMessageBox.information(self.q_widget_profile,"Update","You Can Update Your Name, Shop Name, UPI, Phone Number only")
        self.profile_shop_upi.setReadOnly(False)
        self.profile_shop_wo_name.setReadOnly(False)
        self.profile_shop_name.setReadOnly(False)
        self.profile_shop_phone.setReadOnly(False)
        self.profile_save.setEnabled(True)

    def upi_save(self):
        upi = self.profile_shop_upi.text()
        shop = self.profile_shop_name.text()
        name = self.profile_shop_wo_name.text()
        phone = self.profile_shop_phone.text()
        email = self.l_email.text()
        emai = email.removesuffix('@gmail.com')
        db.child('Employ').child(emai).update({'upi' : upi,'shop' : shop,'f_name' : name,'contact' : phone})
        self.profile_shop_upi.setReadOnly(True)
        self.profile_shop_wo_name.setReadOnly(True)
        self.profile_shop_name.setReadOnly(True)
        self.profile_shop_phone.setReadOnly(True)
        s = smtplib.SMTP('smtp.gmail.com', 587)           
        s.starttls()#security           
        s.login("email", "password")#login smtp    #See Requirements        
        msg=MIMEMultipart()#message
        msg['From'] = "email" #See Requirements
        msg['To'] = email
        msg['Subject'] = "UPDATE ACCOUNT"
        day = self.dateTimeEdit.dateTime().toString('MM/dd/yyyy  h:mm:ss')
        message = 'Hello, '+'\n\n\t\tWe Noticed a New Login,\t at '+day+'\n\nYou HAVE UPDATE YOUR ACCOUNT ''\n\n\nThanks,\n\nYour QrPay team'
        msg.attach(MIMEText(message, 'plain'))               
        s.sendmail("email", email, msg.as_string()) #See Requirements
        QMessageBox.information(self.q_widget_profile,"Update","Your Account successfully update")
        self.profile_close()
        QMessageBox.information(self.widget_qrpay,"Warning","Please logout to get update of your Account")

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.profile_update.clicked.connect(self.upi_update)
        self.profile_save.clicked.connect(self.upi_save)

        self.history_tableWidget.setColumnWidth(0,70)
        self.history_tableWidget.setColumnWidth(1,200)
        self.history_tableWidget.setColumnWidth(2,140)
        self.history_tableWidget.setColumnWidth(3,160)
        self.history_tableWidget.setColumnWidth(4,120)
        self.history_tableWidget.setColumnWidth(5,120)
        self.history_tableWidget.setColumnWidth(6,135)

        self.search_tableWidget.setColumnWidth(0,70)
        self.search_tableWidget.setColumnWidth(1,200)
        self.search_tableWidget.setColumnWidth(2,140)
        self.search_tableWidget.setColumnWidth(3,160)
        self.search_tableWidget.setColumnWidth(4,120)
        self.search_tableWidget.setColumnWidth(5,120)
        self.search_tableWidget.setColumnWidth(6,135)

        self.history_search.clicked.connect(self.search_details)
        self.search_search.clicked.connect(self.search_details)
        self.search_close.clicked.connect(self.close_search)

        self.widget_welcome.show()
        self.widget_register_details.hide()
        self.widget_register.hide()
        self.widget_login.hide()
        self.widget_forget.hide()
        self.widget_qrpay.hide()
        self.frame.show()

        self.w_login.clicked.connect(self.login)
        self.w_register.clicked.connect(self.register)
        self.l_login.clicked.connect(self.login_function)
        self.l_forget.clicked.connect(self.forget_function)
        self.l_back.clicked.connect(self.welcome)
        self.f_submit.clicked.connect(self.send_otp)
        self.f_resend.clicked.connect(self.resend_otp)
        self.f_back.clicked.connect(self.login)
        self.s_register.clicked.connect(self.register_function)
        self.s_back.clicked.connect(self.welcome)
        self.r_register.clicked.connect(self.register_details)
        self.r_back.clicked.connect(self.register)

        self.q_old_details.clicked.connect(self.history_details)
        self.history_close.clicked.connect(self.close_history)

        self.q_c.clicked.connect(self.calculator)
        self.q_qr_generate.clicked.connect(self.Gene_rate)
        self.pushButton.clicked.connect(self.pr_total)
        self.q_clear.clicked.connect(self.screen_clear)  
        self.q_save.clicked.connect(self.save_data) 

        self.q_log_out.clicked.connect(self.logout)
        self.q_acc_ount.clicked.connect(self.account)
        self.q_profile_close_2.clicked.connect(self.profile_close)

        self.q_c_close.clicked.connect(self.calculator_close)
        self.q_c_ac.clicked.connect(self.c)       
        self.q_c_c.clicked.connect(self.backscpace)
        self.q_c_add.clicked.connect(lambda:self.cal('+'))
        self.q_c_div.clicked.connect(lambda:self.cal('/'))
        self.q_c_mul.clicked.connect(lambda:self.cal('*'))
        self.q_c_sub.clicked.connect(lambda:self.cal('-'))
        self.q_c_enter.clicked.connect(self.equal)
        self.q_c_nine.clicked.connect(lambda:self.cal('9'))
        self.q_c_eight.clicked.connect(lambda:self.cal('8'))
        self.q_c_seven.clicked.connect(lambda:self.cal('7'))  
        self.q_c_six.clicked.connect(lambda:self.cal('6'))
        self.q_c_five.clicked.connect(lambda:self.cal('5'))
        self.q_c_four.clicked.connect(lambda:self.cal('4'))
        self.q_c_three.clicked.connect(lambda:self.cal('3'))
        self.q_c_two.clicked.connect(lambda:self.cal('2'))
        self.q_c_one.clicked.connect(lambda:self.cal('1'))
        self.q_c_zero.clicked.connect(lambda:self.cal('0'))
        self.q_c_dot.clicked.connect(lambda:self.cal('.'))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())

