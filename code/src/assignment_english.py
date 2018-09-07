import re,sys,os
f1=open('../src/'+sys.argv[1],"r")
f2=open('../src/'+sys.argv[2],"r")
cfg={}
pcfg={}
rules={}
score=[]



#------------------------------------------------------ splitting input and output
def parse_train(s):
	arr=[]
	word=""
	count=0
	for i in s:
		if(i=='(' or i==')'):	
			if(word==""):
				arr.append(i)
			else:
				arr.append(word)
				arr.append(i)
				word=""
		elif i==' ':
			if word!="":
				arr.append(word)
				word=""
		else:
			word+=i
	#print arr
	return arr
def parse_test(s):
	arr=[]
	s=s.replace("\n","")
	s=s.split(" ")
	for i in s:
		j=i.split("_")
		if len(j)==2:
			arr.append([j[1],j[0],1.0])
	#print arr
	#print s
	return arr,len(s)


#-------------------------------------------------------- create cfg 
def create_cfg(a):
    global cfg
   #print a
    ans=[]
    tag=a[1]
    if(a[2]!='('):
	#print "came"
        ans.append(a[2].lower())
	####------------------- commnet if need VB -> (verb) kind of rules
	return tag
    else:
        count=0
        arr=[]
        for i in range(2,len(a)):
            arr.append(a[i])
            if a[i]=='(':
                count+=1
            elif a[i]==')':
                count-=1
            if count==-1:
                break
            if(count==0):
		  #print ' '.join(arr)
                ans.append(create_cfg(arr))
                arr=[]
	    #print ' '.join(arr),count
    #print ans
    try:
            #if ans not in cfg[tag]:
            cfg[tag].append(ans)
    except:
        cfg[tag]=[ans]
    return tag


#---------------------------------------------------------------

def cfg_to_pcfg():
	global cfg,pcfg
	k=cfg.keys()
	for i in k:
		s={}
		pcfg[i]=[]
		l=len(cfg[i]);
		for j in cfg[i]:
			try:
				if s[str(j)]:
					continue;
			except:
				t=cfg[i].count(j)*1.0/l
				pcfg[i].append([j,round(t,5)])
				s[str(j)]=1

def convert_cnf_single():
	global pcfg
	k=cfg.keys()
	added=True
	while added:
		added=False
		k=pcfg.keys()
		for i in k:
			a=[]
			for j in pcfg[i]:
				if(len(j[0])>1):
					a.append(j)
				if len(j[0])==1:
					#print i,' -----> ',j
					t=j[0][0]
					try:
						for l in pcfg[t]:
							#print l,
							tt=j[1]*l[1]
							a.append([l[0],round(tt,5)])
							flag=False
							for tt in pcfg[i]:
								#print tt
								for ttt in tt:
									#print "\n**** ",l[0],ttt
									if l[0]==ttt:
										flag=True
							if not flag:
								added=True
						#print
					except:
						a.append(j)
					#print i,' ----->',a,t
					#print
			pcfg[i]=a




def convert_cnf_long():
	global pcfg,rules
	kk=pcfg.keys()
	ct=0
	for i in kk:
		rules[i]=[]
		for j in pcfg[i]:
			if (len(j[0]))>2:
			#	print '--------------------- ' , i
				count=len(j[0])
				arr=j[0]
			#	print arr
				for k in range(count-2,0,-1):
					rules[i+'_'+str(ct)]=[[[arr[-2],arr[-1]],1.0]]
					arr=arr[:-2]+[i+'_'+str(ct)]
					#print i+'_'+str(k),' --> ',pcfg[i+'_'+str(k)]
					ct+=1
				rules[i].append([arr,j[1]])
				#print i,' --> ',pcfg[i]
			else:
				rules[i].append(j)

#------------------------------      CYK ALGORITHM    --------------------------------------
def CYK(p,n):
	global rules,score
	back=[]
	for i in range(n):
		score.append([])
		back.append([])
		for j in range(n+1):
			score[i].append({})
			back[i].append({})
			if(i+1==j):
				score[i][j]={p[i][0]:[[p[i][1]],p[i][2]]}
				#print score[i][j]
				added=True
				while added:
					added=False
					for k in rules.keys():
						for l in rules[k]:
							for m in score[i][j].keys():	
								if l[0][0]==m and len(l[0])==1:
									#print m,k,l,
									#added=True
									prob=score[i][j][m][1]*l[1]
									try:
										if score[i][j][k][1] < prob:
											added=True
											score[i][j][k]=[l[0],prob]
											back[i][j][k]=l[0]
											#score[i][j][k]
									except:
										added=True
										score[i][j][k]=[l[0],prob]
										back[i][j][k]=l[0]
									#print added,k,' --> ',score[i][j][k]
				#print score[i][j]
	#print score
	for span in range(2,n+1):
		for begin in range(0,n+1-span):
			end=begin+span
			for split in range(begin+1,end):
				#print begin,end,split
				for k in rules.keys():
					for l in rules[k]:
						for m in score[begin][split].keys():
							#print score[split][end]
							for o in score[split][end].keys():
								if len(l[0])==2 and l[0][0]==m and l[0][1]==o:
									#print k,m,o,l
									prob=score[begin][split][m][1]*l[1]*score[split][end][o][1]
									try:
										if prob > score[begin][end][k][1]:
											score[begin][end][k]=[l[0],prob]
											back[begin][end][k]=[split,l[0][0],l[0][1]]
									except:
										score[begin][end][k]=[l[0],prob]
										back[begin][end][k]=[split,l[0][0],l[0][1]]
			added=True
			while added:
				added=False
				for k in rules.keys():
					for l in rules[k]:
						for m in score[begin][end].keys():	
							if l[0][0]==m and len(l[0])==1:
								#print m,k,l,
								#added=True
								prob=score[begin][end][m][1]*l[1]
								try:
									if score[begin][end][k][1] < prob:
										added=True
										score[begin][end][k]=[l[0],prob]
										back[begin][end][k]=[l[0]]
										#score[i][j][k]
								except:
									added=True
									score[begin][end][k]=[l[0],prob]
									back[begin][end][k]=l[0]
	t=None
	m=-1
	for i in range(n):
		for j in range(0,n+1):
			#print score[i][j],' ----' ,
			if j==n and i==0:
				for k in score[i][j].keys():
					#print score[i][j][k][1]
					if(score[i][j][k][1]>m):
						m=score[i][j][k][1]
						t=k
					
					string=buildTree(score,back,n,0,n,k)
					ans='(TOP'+' '+string+') ' + str(score[0][n][k][1])
					print ans
	
		#print
	#print score[0][n][t],back[0][n][t],t,0,n
	#	break

	if t==None:
		ans="NO TREE POSSIBLE WITH GRAMMAR"
	else:
		print "                     ################# BEST PARSE TREE ########################"
		string=buildTree(score,back,n,0,n,t)
		ans='(TOP'+' '+string+')'
	print ans
	print "-"*100
	'''
	for i in range(n):
		for j in range(n+1):
			print back[i][j],
		print 
	'''
	return ans
							
#-------------------------------------------------------- GET THE TREE FORMAT 
def buildTree(score,back,n,begin,end,k):
	#print '*************    ',k
	t=score[begin][end]
	try:
		p=back[begin][end][k]
	except:
		#print t
		return '('+k+' '+t[k][0][0]+')'
	#print t,p
	if(len(t)==0):
		return "NO TREE POSSIBLE WITH GRAMMAR"
	else:
		if(len(p)==3):
			split=p[0]
			st='('+k+' '+buildTree(score,back,n,begin,split,p[1])+' '+buildTree(score,back,n,split,end,p[2])+')'
		elif(len(p)==1):
			#print "came ****** ",t
			st='('+k+' '+buildTree(score,back,n,begin,end,p[0])+')'
	return st



#------------------------------ GET CFG RULES FROM FILE ------------------------------------

for line in f1:
        line=line[:-1]
        st=parse_train(line)
	if len(st)>0:
        	create_cfg(st)
'''
st=raw_input()
st=parse_train(st)
#print st
create_cfg(st)
'''


#print cfg
cfg_to_pcfg()
convert_cnf_single()
#print pcfg
convert_cnf_long()

#print rules
'''
for i in rules.keys():
	for j in rules[i]:
		print i,'  -->  ',j[0],'               ',j[1] 
	print
'''
for line in f2:
	line=line.replace("\n","")
	st,n=parse_test(line)
	score=[]
	try:
		CYK(st,n)
	except:
		print "ERORR "
	

'''
st="Greg_NNP works_VBZ in_IN a_DT bank_NN ._."
st="I_PRP work_VBP in_IN a_DT post_NN office_NN ._."
st="I_PRP 'm_VBP afraid_JJ ._."
p,n=parse_test(st)
#print p,n
score=[]
CYK(p,n)
'''


