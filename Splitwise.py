from flask import Flask, redirect, url_for, request, render_template, session
from flask_mail import Mail, Message
import sqlite3 as sql
from random import randint
import sys, os, math


app=Flask(__name__)
app.secret_key = 'any random string'

#conn = sql.connect('database.db')
#curr=conn.cursor()
#conn.execute('CREATE TABLE groups (GroupName TEXT, Member TEXT, Amount REAL, Direction TEXT,OtherMember TEXT)')
#curr.execute("INSERT INTO  groups (GroupName, Member, Amount, Direction,OtherMember) VALUES (?,?,?,?,?)",("","",0.0,"","",))
#conn.commit()
#conn.close()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

global_name=global_email=global_pass=global_rand=global_current_user=global_groupname=""

def friends():
	global global_current_user
	list=[]
	con=sql.connect('database.db')
	cur = con.cursor()
	cur.execute("SELECT * FROM users")
	rows=cur.fetchall()
	string="Databases/" + global_current_user + ".db"
	conn=sql.connect(string)
	curr=conn.cursor()
	for i in range (0,len(rows)):
		val=rows[i]
		curr.execute("SELECT * FROM transactions WHERE  FriendName = ?", (val[0],))
		value=curr.fetchone()
		#print(type(str(value)))
		#print(type(global_current_user))
		if value != None and str(value[0]) != global_current_user:
			list.append(val[0])
			#print(global_current_user)
			#print(value)
	conn.close()
	con.close()
	return list

#generic
@app.route('/')
def homepage():
	if 'username' in session:
		global global_current_user
		global_current_user=session['username']
		return render_template("welcome.html",result=global_current_user,connection=None,list=friends())
	return render_template('index.html',error=None)

@app.route('/returntohome',methods=['POST'])
def returntohome():
	return redirect(url_for('homepage'))

@app.route('/',methods=['POST'])
def result():
	try:
		if request.method=='POST':
			name=request.form['ID']
			password=request.form['Password']
			con=sql.connect("database.db")
			cur = con.cursor()
			val=None
			cur.execute("SELECT * FROM users WHERE name = ?", (name,))
			val=cur.fetchone()
			error=None
			if val == None or val[2] != password:
				error="Username and Password don't match"
				return render_template("index.html",error=error)
			else:	
				global global_current_user
				session['username']=name
				global_current_user=name
				
				return render_template("welcome.html",result=name,connection=None,list=friends())
			con.close()	
	except:
		con.rollback();

@app.route('/sign_up',methods=['POST'])
def Signup():
	return render_template("signup.html",error=None)

@app.route('/commit_details',methods=['POST'])
def commit_details():
	global global_name
	global global_rand
	global global_pass
	global global_email
	global_name=request.form['Name']
	global_email=request.form['ID']
	global_pass=request.form['Password1']
	pass2=request.form['Password2']
	error=None
	try:
		con=sql.connect("database.db")
		cur = con.cursor()
		val=None
		val2=None
		cur.execute("SELECT * FROM users WHERE Name = ?", (global_name,))
		val=cur.fetchone()
		cur.execute("SELECT * FROM users WHERE Email = ?", (global_email,))
		val2=cur.fetchone()
		if global_name == "users":
			error="Username cannot be users."
			return render_template("signup.html",error=error)
		elif val!=None and val2!=None:
			error="Username already taken.Given Email ID already has an associated account."
			return render_template("signup.html",error=error)
		elif val!=None:
			error="Username already taken."
			return render_template("signup.html",error=error)
		elif val2!=None:
			error="Given Email ID already has an associated account."
			return render_template("signup.html",error=error)	
		elif global_pass != pass2:
			error="Passwords do not match."
			return render_template("signup.html",error=error)
		elif global_pass == "":
			error="Password cannot be blank"
			return render_template("signup.html",error=error)
		elif global_email[len(global_email)-10:len(global_email)] != "@gmail.com":
			error="Not a valid Gmail ID"
			return render_template("signup.html",error=error)
		elif global_name == "":
			error="Username cannot be blank!"
			return render_template("signup.html",error=error)	
		else:
			global_rand=randint(1000,10000)
			msg = Message('Splitwise Verification email', sender = 'itprojectver@gmail.com', recipients = [global_email])
			msg.body = "Your verification code is " + str(global_rand) + "."
			mail.send(msg)
			return render_template("verification.html",check=None,email=global_email)	
	except:
		con.rollback()	

@app.route('/verify',methods=['POST'])
def verify():
	code=request.form['Code']
	global global_name
	global global_rand
	global global_pass
	global global_email
	if code == str(global_rand):
		try:
			con=sql.connect("database.db")
			cur = con.cursor()	
			cur.execute("INSERT INTO users (Name,Email,Password)	VALUES (?,?,?)",(global_name,global_email,global_pass))
			con.commit()
			con.close()
			try:
				string= "Databases/" + global_name + ".db"
				conn = sql.connect(string)
				curr=conn.cursor()
				curr.execute('CREATE TABLE transactions (FriendName TEXT, Amount REAL, Direction TEXT)')
				curr.execute('CREATE TABLE history (FriendName TEXT, Amount REAL, Direction TEXT)')
				conn.commit()
				currr=conn.cursor()
				currr.execute('INSERT INTO transactions (FriendName,Amount,Direction)	VALUES (?,?,?)',(global_name,0,"to"))
				currr.execute('INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)',(global_name,0,"to"))
				conn.commit()
				conn.close()
			except:
				conn.rollback();
			return redirect(url_for('homepage'))		
		except:
			con.rollback();	
	else:
		return render_template("verification.html",check="Verification code does not match. Please try again.")

@app.route('/logout',methods=['POST'])
def logout():
	session.pop('username','None')
	return redirect(url_for('homepage'))

@app.route('/list')
def display():
	global global_current_user
	alist=[]
	try:
		con=sql.connect('database.db')
		cur = con.cursor()
		cur.execute("SELECT * FROM users")
		rows=cur.fetchall()
		string="Databases/" + global_current_user + ".db"
		conn=sql.connect(string)
		curr=conn.cursor()
		for i in range (0,len(rows)):
			val=rows[i]
			curr.execute("SELECT * FROM transactions WHERE  FriendName = ?", (val[0],))
			value=curr.fetchone()
			if value == None:
				alist.append(val[0])
		conn.close()
		con.close()	
		return render_template("list.html",rows=alist)	
	except:
		con.rollback()	
		conn.rollback()

@app.route('/addfriend',methods=['POST'])
def addfriend():
	fri=request.form.getlist('friend')
	#print(fri)
	try:
		global global_current_user		
		string="Databases/" + global_current_user + ".db"
		con=sql.connect(string)
		cur = con.cursor()
		for friend in fri:
			cur.execute("INSERT INTO transactions (FriendName,Amount,Direction)	VALUES (?,?,?)",(friend,0,"to",))
			strr="Databases/" + friend + ".db"
			conn=sql.connect(strr)
			curr=conn.cursor()
			curr.execute("INSERT INTO transactions (FriendName,Amount,Direction)	VALUES (?,?,?)",(global_current_user,0,"to",))
			conn.commit()
			conn.close()
		con.commit()
		con.close()
		return redirect(url_for('display'))
	except:
		con.rollback();		

@app.route('/updateuseraccounts',methods=['POST'])
def updateuseraccounts():
	global global_current_user
	strr="Databases/" + global_current_user + ".db"
	try:
		name=request.form.getlist('name')
		amount=request.form['amount']
		amount=float(amount)
		select=request.form['select']
		con=sql.connect(strr)
		cur = con.cursor()	
		for element in name:
			#print("Entered")
			cur.execute("SELECT Amount FROM transactions WHERE FriendName=?",(element,))
			amt1=cur.fetchone()
			amt=amt1[0]
			cur.execute("SELECT Direction FROM transactions WHERE FriendName=?",(element,))
			direc=cur.fetchone()
			dire=str(direc[0])
			#print(type(amt))
			#print(type(amount))
			if dire=="to" and select=="to":
				var=amount+amt
				cur.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(element,amount,"paid you",))
				cur.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,element,))
			elif dire=="by" and select=="by":
				var=amount+amt
				cur.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(element,amount,"You paid",))
				cur.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,element,))
			elif dire=="to" and select=="by":
				if amt<amount:
					var=amount-amt
					v="by"
					cur.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(element,amount,"You paid",))
					cur.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,element,))
					cur.execute("UPDATE transactions SET Direction=? WHERE FriendName=?",(v,element,))
				else:	
					var=amt-amount
					cur.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(element,amount,"You paid",))
					cur.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,element,))
			elif dire=="by" and select=="to":
				cur.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(element,amount,"paid you",))
				if amt<amount:
					var=amount-amt
					v="to"
					cur.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,element,))
					cur.execute("UPDATE transactions SET Direction=? WHERE FriendName=?",(v,element,))
				else:	
					var=amt-amount
					cur.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,element,))
			con.commit()
			#2nd Database
			string="Databases/" + element + ".db"
			try:
				conn=sql.connect(string)
				curr=conn.cursor()
				#print("Entered")
				curr.execute("SELECT Amount FROM transactions WHERE FriendName=?",(global_current_user,))
				if select=="to":
					select="by"
				else:
					select="to"
				curr.execute("SELECT Amount FROM transactions WHERE FriendName=?",(global_current_user,))
				amt1=curr.fetchone()
				amt=amt1[0]
				curr.execute("SELECT Direction FROM transactions WHERE FriendName=?",(global_current_user,))
				direc=curr.fetchone()
				dire=str(direc[0])
				#print(type(amt))
				#print(type(amount))
				if dire=="to" and select=="to":
					var=amount+amt
					curr.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(global_current_user,amount,"paid you",))
					curr.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,global_current_user,))
				elif dire=="by" and select=="by":
					curr.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(global_current_user,amount,"You paid",))
					var=amount+amt
					curr.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,global_current_user,))
				elif dire=="to" and select=="by":
					curr.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(global_current_user,amount,"You paid",))
					if amt<amount:
						var=amount-amt
						v="by"
						curr.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,global_current_user,))
						curr.execute("UPDATE transactions SET Direction=? WHERE FriendName=?",(v,global_current_user,))
					else:	
						var=amt-amount
						curr.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,global_current_user,))
				elif dire=="by" and select=="to":
					curr.execute("INSERT INTO history (FriendName,Amount,Direction)	VALUES (?,?,?)",(global_current_user,amount,"paid you",))
					if amt<amount:
						var=amount-amt
						v="to"
						curr.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,global_current_user,))
						curr.execute("UPDATE transactions SET Direction=? WHERE FriendName=?",(v,global_current_user,))
					else:	
						var=amt-amount
						curr.execute("UPDATE transactions SET Amount=? WHERE FriendName=?",(var,global_current_user,))
				conn.commit()
				conn.close()
				if select=="to":
					select="by"
				else:
					select="to"	
			except:
				conn.rollback()	
		con.close()
		return render_template("welcome.html",result=global_current_user,connection="Transaction added.",list=friends())	
	except:
		con.rollback()		

@app.route('/display')
def func():
	global global_current_user
	string="Databases/" + global_current_user + ".db"
	con=sql.connect(string)
	cur=con.cursor()
	cur.execute("SELECT * FROM transactions")
	var=cur.fetchall()
	#print(var)
	name=[]
	count=0
	for element in var:
		alist=[]
		#print(element)
		if str(element[0]) != global_current_user and float(element[1]) != 0.0:
			alist.append(str(element[0]))
			alist.append(float(element[1]))
			alist.append(str(element[2]))
			name.append(alist)
	return render_template("display.html",name=name)		

@app.route('/transactions')
def transact():
	global global_current_user
	strr="Databases/" + global_current_user + ".db"
	con=sql.connect(strr)
	cur=con.cursor()
	cur.execute("SELECT * FROM history")
	var=cur.fetchall()
	alist=[]
	for element in var:
		if element[0] != global_current_user:
			if element[2]=="You paid":
				alist.append(element[2] + " " + element[0] + " Rs. " + str(element[1]))
			else:
				alist.append(element[0] + " " + element[2] + " Rs. " + str(element[1]))
	return render_template("transactions.html",alist=alist)	

@app.route('/create')
def creategroup():
	return render_template("create.html",list=friends(),error= None)

@app.route('/create',methods=['POST'])
def create():
	groupname=request.form["Name"]	
	global global_current_user
	names=request.form.getlist("name")
	#print(names)
	if len(names) == 0:
		return render_template("create.html",list=friends(),error="Group cannot be empty")
	elif groupname =="":
		return render_template("create.html",list=friends(),error="Groupname cannot be empty")
	names.append(global_current_user)
	try:	
		con=sql.connect("database.db")
		cur=con.cursor()
		cur.execute("SELECT * FROM groups WHERE GroupName=?",(groupname,))
		var=cur.fetchone()
		if var != None:
			return render_template("create.html",list=friends(),error="Group Name already taken")		
		for element1 in names:
			for element2 in names:
				if element2 != element1:
					cur.execute("INSERT INTO groups  (GroupName,Member,Amount,Direction,OtherMember)	VALUES (?,?,?,?,?)",(groupname,element1,0.0,"to",element2,))
		con.commit()
		con.close()
	except:
		con.rollback()	
	return render_template("welcome.html",result=None,connection=None,list=friends())	

@app.route('/groups')
def groups():
	global global_current_user
	try:
		con=sql.connect("database.db")
		cur=con.cursor()
		cur.execute("SELECT * FROM groups WHERE Member=?",(global_current_user,))
		var=cur.fetchall()
		z=[]
		for element in var:
			z.append(element[0])
		#print(type(var))
		z=list(set(z))
		#print(var)
		con.close()
		return render_template("groups.html",list=z)
	except:
		con.rollback()	

@app.route('/groups/<gname>')
def details(gname=None):
	global global_current_user
	con=sql.connect("database.db")
	#print(gname)
	global global_groupname
	global_groupname=gname
	cur=con.cursor()
	cur.execute("SELECT * FROM groups WHERE GroupName=?",(gname,))
	var=cur.fetchall()
	alist=[]
	for element in var:
		string=""
		if element[3]=="to" and element[2] !=0.0:
			string=string + element[1] + " needs to pay Rs. " + str(element[2]) + " to " + element[4]
			alist.append(string)
#		elif element[2] != 0.0:
#			string=string + element[1] + " needs to receive Rs. " + str(element[2]) + " from " element[4]
#			alist.append(string)
	if len(alist) == 0:
		alist.append("All accounts are balanced.")		
	z=friends()
	z.append(global_current_user)	
	return render_template("details.html",alist=alist,list=z,error=None)

@app.route('/groupscalc', methods=['POST'])		
def calc():
	global global_current_user
	global global_groupname
	name=request.form['Name']
	amount=request.form['amount']
	names=request.form.getlist('name')
	alist=[]
	z=friends()
	try:
		conn=sql.connect("database.db")
		curr=conn.cursor()
		curr.execute("SELECT * FROM groups WHERE GroupName=?",(global_groupname,))
		var=curr.fetchall()
		for element in var:
			string=""
			if element[3]=="to" and element[2] !=0.0:
				string=string + element[1] + " needs to pay Rs. " + str(element[2]) + " to " + element[4]
				alist.append(string)
		z.append(global_current_user)
		conn.close()
	except:
		conn.rollback()			
	if name =="":
		return render_template("details.html",alist=alist,list=z,error="Name cannot be blank")
	elif amount == "":	
		return render_template("details.html",alist=alist,list=z,error="Amount cannot be blank")
	elif len(names)	== 0:
		return render_template("details.html",alist=alist,list=z,error="Transaction cannot be empty")
	amount=float(amount)
	for element in names:
		if element == "Everyone":
			con=sql.connect('database.db')
			cur=con.cursor()
			cur.execute("SELECT * FROM groups WHERE GroupName=? and Member=?",(global_groupname,global_current_user,))
			var=cur.fetchall()
			length=len(var)+1
			amount=amount/length
			cur.execute("SELECT * FROM groups WHERE GroupName=?",(global_groupname,))
			z=cur.fetchall()
			for ele in z:
				amt=ele[2]
				if ele[1] == name and ele[4] != name: 
					if ele[3] == "to":
						if amt<amount:	
							cur.execute("UPDATE groups SET Amount=? WHERE OtherMember=? and Member=?",(amount-amt,element,name,))
							cur.execute("UPDATE groups SET Direction=? WHERE OtherMember=? and Member=?",("by",element,name,))
						else:
							cur.execute("UPDATE groups SET Amount=? WHERE OtherMember=? and Member=?",(amt-amount,element,name,))
					else:
						cur.execute("UPDATE groups SET Amount=? WHERE OtherMember=? and Member=?",(amount+amt,name,element,))
				elif ele[1] != name and ele[4] == name:
					if ele[3] == "by":
						if amount<amt:
							cur.execute("UPDATE groups SET Amount=? WHERE OtherMember=? and Member=?",(amount-amt,element,name,))
							cur.execute("UPDATE groups SET Direction=? WHERE OtherMember=? and Member=?",("to",element,name,))
						else:
							cur.execute("UPDATE groups SET Amount=? WHERE OtherMember=? and Member=?",(amt-amount,element,name,))
					else:
						cur.execute("UPDATE groups SET Amount=? WHERE OtherMember=? and Member=?",(amount+amt,name,element,))
			#z=(-1 + math.sqrt(1 + 8*length))/2.0
			#piece=amount/z
	return render_template("details.html",alist=alist,list=z,error=None)		

if __name__ == '__main__':
	app.run(debug=True)	