from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
import json
from web3 import Web3, HTTPProvider
from datetime import datetime
global details
details = ''
global user_id
def readDetails(contract_type):
global details
details = ""
print(contract_type+"======================")
blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = 'BankContract.json' #bank contract contract code
deployed_contract_address = '0x1DD4fb45C1cdC8C3f32cbaA60464c8107D4D4058' #hash address to access bank contract
 with open(compiled_contract_path) as file:
contract_json = json.load(file)  # load contract info as JSON
contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
file.close()
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
if contract_type == 'adduser':
details = contract.functions.getUsers().call()
if contract_type == 'account':
details = contract.functions.getBankAccount().call()
if len(details) > 0:
if 'empty' in details:
details = details[5:len(details)]
print(details)    
def saveDataBlockChain(currentData, contract_type):
global details
global contract
details = ""
blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]
 compiled_contract_path = 'BankContract.json' #bank contract file
deployed_contract_address = '0x1DD4fb45C1cdC8C3f32cbaA60464c8107D4D4058' #bank contract address
 with open(compiled_contract_path) as file:
 contract_json = json.load(file)  # load contract info as JSON
contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
file.close()
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
readDetails(contract_type)
if contract_type == 'adduser':
details+=currentData
msg = contract.functions.addUsers(details).transact()
tx_receipt = web3.eth.waitForTransactionReceipt(msg)
if contract_type == 'account':
details+=currentData
 msg = contract.functions.bankAccount(details).transact()
tx_receipt = web3.eth.waitForTransactionReceipt(msg)
def SendAmountAction(request):
global details
if request.method == 'POST':
sender = request.POST.get('t1', False)
balance = request.POST.get('t2', False)
receiver = request.POST.get('t3', False)
amount = request.POST.get('t4', False)
amount = float(amount)
balance = float(balance)
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if balance > amount:
data = sender+"#"+str(amount)+"#"+str(timestamp)+"#Sent To "+receiver+"\n"
saveDataBlockChain(data,"account")
data = receiver+"#"+str(amount)+"#"+str(timestamp)+"#Received From "+sender+"\n"
saveDataBlockChain(data,"account")
context= {'msg':'Money sent to '+receiver}
return render(request, 'UserScreen.html', context)
else:
context= {'msg':'insufficient balance'}
return render(request, 'UserScreen.html', context)
def SendAmount(request):
if request.method == 'GET':
global user_id
readDetails("account")
deposit = 0
wd = 0
rows = details.split("\n")
for i in range(len(rows)-1):
arr = rows[i].split("#")
if arr[0] == user_id:
if arr[3] == 'Self Deposit' or "Received From " in arr[3]:
deposit = deposit + float(arr[1])
else:
wd = wd + float(arr[1])
deposit = deposit - wd         
output = '<tr><td><font size="3" color="black">Username</td><td><input type="text" name="t1" size="20" value='+user_id+' readonly/></td></tr>'
output+='<tr><td><fontsize="3" color="black">Available&nbsp;Balance</td><td><inputtype="text"name="t2"size="20" value='+str(deposit)+' readonly/></td></tr>'
output+='<tr><td><fontsize="3" color="black">Choose&nbsp;Receiver&nbsp;Name</td><td><select name="t3">'
readDetails("adduser")
 rows = details.split("\n")
for i in range(len(rows)-1):
arr = rows[i].split("#")
 if arr[0] == "adduser":
if arr[1] != user_id:
output += '<option value="'+arr[1]+'">'+arr[1]+'</option>'
output += "</select></td></tr>"
context= {'msg1':output}
return render(request, 'SendAmount.html', context)
def ViewBalance(request):
if request.method == 'GET':
global user_id
output = '<table border=1 align=center width=100%>'
font = '<font size="3" color="black">'
arr = ['Username','Amount','Transaction Date',"Transaction Status"]
output += "<tr>"
for i in range(len(arr)):
output += "<th>"+font+arr[i]+"</th>"
readDetails("account")
rows = details.split("\n")
deposit = 0
wd = 0
for i in range(len(rows)-1):
arr = rows[i].split("#")
if arr[0] == user_id:
output += "<tr><td>"+font+arr[0]+"</td>"
output += "<td>"+font+arr[1]+"</td>"
output += "<td>"+font+arr[2]+"</td>"
output += "<td>"+font+arr[3]+"</td>"
if arr[3] == 'Self Deposit' or "Received From " in arr[3]:
deposit = deposit + float(arr[1])
else:
wd = wd + float(arr[1])
deposit = deposit - wd
output += "<tr><td>"+font+"Current Balance : "+str(deposit)+"</td>"
context= {'msg':output}
return render(request, 'ViewBalance.html', context)
def LoginAction(request):
global details
global user_id
if request.method == 'POST':
username = request.POST.get('t1', False)
password = request.POST.get('t2', False)
status = 'none'
readDetails("adduser")
rows = details.split("\n")
for i in range(len(rows)-1):
arr = rows[i].split("#")
if arr[0] == "adduser":
if arr[1] == username and arr[2] == password:
status = 'success'
user_id = username
break
if status == 'success':
file = open('session.txt','w')
file.write(username)
file.close()
context= {'msg':"Welcome "+username}
return render(request, 'UserScreen.html', context)
else:
context= {'msg':'Invalid login details'}
return render(request, 'Login.html', context)
def DepositAction(request):
global details
if request.method == 'POST':
username = request.POST.get('t1', False)
amount = request.POST.get('t2', False)
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
data = username+"#"+amount+"#"+str(timestamp)+"#Self Deposit\n"
saveDataBlockChain(data,"account")
context= {'msg':'Money added to user account '+username}
return render(request, 'Deposit.html', context)
def SignupAction(request):
global details
if request.method == 'POST':
username = request.POST.get('t1', False)
password = request.POST.get('t2', False)
contact = request.POST.get('t3', False)
email = request.POST.get('t4', False)
address = request.POST.get('t5', False)
gender = request.POST.get('t6', False)
record = 'none'
readDetails("adduser")
rows = details.split("\n")
for i in range(len(rows)-1):
arr = rows[i].split("#")
if arr[0] == "adduser":
if arr[1] == username:
record = "exists"break
if record == 'none':
data = "adduser#"+username+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+gender+"\n"
saveDataBlockChain(data,"adduser")
context= {'msg':'Signup process completd and record saved in Blockchain'}
return render(request, 'Signup.html', context)
else:
context= {'msg':username+'Username already exists'}
return render(request, 'Signup.html', context)
def Signup(request):
if request.method == 'GET':
return render(request, 'Signup.html', {})
def Deposit(request):
if request.method == 'GET':
global user_id
output = '<tr><td><font size="3" color="black">Username</td><td><input type="text" name="t1" size="20" value='+user_id+' readonly/></td></tr>'
context= {'msg1':output}
return render(request, 'Deposit.html', context)
def Logout(request):
if request.method == 'GET':
return render(request, 'index.html', {})
def index(request):
if request.method == 'GET':
return render(request, 'index.html', {})
def Login(request):
if request.method == 'GET':
return render(request, 'Login.html', {})
