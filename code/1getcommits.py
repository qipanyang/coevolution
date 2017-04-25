import os
import shutil

rootpath = "/home/seitest/louyiling/ICSE/regressiontest"
subjectListPath = rootpath + "/needHandleSubjectList.txt"
subjectUrlListPath = rootpath + "/subject_url_list.txt"
workableSubjectListPath = rootpath + '/workablesubList.txt'
commitRootPath = rootpath  + "/projects"

#get the subject list from the file
def getSubjectList(inputFile):
	subjectList = []
	readInputFile = open(inputFile)
	for line in readInputFile:
		line = line.strip()
		subjectList.append(line)
	readInputFile.close()
	return subjectList

def getRootUrl(inputFilePath, subjectName):
	rootUrl = ""
	inputFile = open(inputFilePath)
	for line in inputFile:
		lineList = line.strip().split(' ')
		if(lineList[0] == subjectName):
			rootUrl = lineList[2]
			break
	inputFile.close()
	return rootUrl

def getRootUrlList(inputFilePath, subjectList):
	rootUrlList = {}
	for subject in subjectList:
		rootUrl = getRootUrl(inputFilePath, subject)
		if rootUrl == '':
			print 'error no Url for subject ' + subject
			continue
		rootUrlList[subject] = rootUrl
	return rootUrlList

def singlemodule(originalpath):
	srcpath1 = originalpath + '/src/main'
	srcpath2 = originalpath + '/src/test'
	if os.path.exists(srcpath1) and os.path.exists(srcpath2):
		return True
	else:
		return False

if __name__ == '__main__':


	subjectList = []
	subjectList = getSubjectList(subjectListPath)
	rootUrlList = getRootUrlList(subjectUrlListPath, subjectList)
	
	
	
	#print rootUrlList
	#allSubjectCommitIDList = getAllSubjectCommitIDList(urlCommitListPath, subjectList, rootUrlList)
	#print allSubjectCommitIDList
	
	
	subject_ID = 0
	
	for subject in subjectList:
		subject_ID = subject_ID + 1
		if subject_ID < 1:
			continue
		print 'download for subject ' + subject
		
		#mk dir subject name
		subjectPath = commitRootPath + '/' + subject
		if os.path.exists(subjectPath):
			shutil.rmtree(subjectPath)
		
		os.mkdir(subjectPath)
		originalpath = subjectPath + '/original'
		os.mkdir(originalpath)
		
		
		downloadcmd = 'git clone ' + rootUrlList[subject] + '.git ' + originalpath
		os.system(downloadcmd)
		
		os.chdir(originalpath)
		if singlemodule(originalpath) == False:
			os.chdir(commitRootPath)
			shutil.rmtree(subjectPath)
			continue
		
		
		
		#gethistorycmd = 'git log --first-parent --no-merges >> ' + originalpath + '/historyList.txt'
		gethistorycmd = 'git log --first-parent -p >> ' + originalpath + '/historyList.txt'
		os.system(gethistorycmd)
		
		
		
		writelog = open(originalpath + '/modList.txt', 'w')
		
		
		commitList = []
		logList = []
		readfile = open(originalpath + '/historyList.txt')
		currentcommit = ""
		tmpfile = ""
		workable = False # whether is java file modification
		logstring = "" #record the file and line number
		for line in readfile:
			line = line.strip()
			if line.startswith('commit '):
				if currentcommit != '' and logstring != '':
					commitList.append(currentcommit)
					writelog.write('commit ' + currentcommit + '\n')
					writelog.write(logstring)
				tmpcmd = line.split(' ')[1]
				currentcommit = tmpcmd
				workable = False
				logstring = ""
			elif line.startswith('diff --git'):
				if line.endswith('.java') and ('/src/main/' in line or '/src/test/' in line): # java modification 
					workable = True
					tmps = line.replace('diff --git a', '')
					tmpfile = tmps.split(' ')[0]
					#logstring =  logstring + 'diff ' + tmps + ' '
				else:
					workable = False # not java modification
			elif workable and line.startswith('@@ -'):
				tmps = line.replace('@@ -', '')
				#print 'my' + tmps
				tmps = tmps.split('@@')[0]
				#print 'test' + tmps
				tmps = tmps.strip()
				tmps = tmps.split('+')[1]
				tmps = tmps.strip()
				begin = int(tmps.split(',')[0])
				end = begin + int(tmps.split(',')[1])
				logstring = logstring + 'diff ' + tmpfile  + ' ' + str(begin) + ' ' + str(end) + '\n'
		readfile.close()
		writelog.close()
		
		
		
		writefile = open(originalpath + '/commitList.txt', 'w')
		for item in commitList:
			writefile.write(item + '\n')
		writefile.close()
		commitSum = 0
		if len(commitList) < 100:
			os.chdir(commitRootPath)
			shutil.rmtree(subjectPath)
			continue
		writeworkablesub = open(workableSubjectListPath, 'a')
		writeworkablesub.write(subject +'\n')
		writeworkablesub.close()
		commitSum = 100
		for i in range(0, commitSum):
			print 'check out commit v' + str(commitSum - i)
			tmpcommit = commitList[i]
			os.chdir(originalpath)
			checkoutcmd = 'git checkout ' + tmpcommit
			os.system(checkoutcmd)
			copycmd = 'cp -rf ' + originalpath + ' ' + subjectPath + '/v' + str(commitSum - i)
			os.system(copycmd)
			writeid = open(subjectPath + '/v' + str(commitSum - i) + '/commitID.txt', 'w')
			writeid.write(tmpcommit +'\n')
			writeid.close()
