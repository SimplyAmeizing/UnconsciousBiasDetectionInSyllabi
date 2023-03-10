import os
import sys
import PyPDF2
import pandas as pd
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
nltk.download('words')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')


currentDirPath = os.getcwd()

inputDirPath = currentDirPath + '/SvmAndBERT/SyllabiResults'

#reclassify this later
classficationDict = {}
ct = 0
for filename in os.listdir(inputDirPath):
    ct += 1
    if filename[:4] == 'Bias':
        classficationDict[filename] = 1
    else:
        classficationDict[filename] = 0

wordSet = set(words.words())
stop_words = set(stopwords.words('english'))

syllabiParsed = []
targetValues = []
for fileName in os.listdir(inputDirPath):
    file = os.path.join(inputDirPath, fileName)
    lemmatizer = WordNetLemmatizer()

    if file[-4:] == '.txt' and os.path.isfile(file):
        targetValues.append(classficationDict[fileName])
        tempDict = set()
        finSyllabus = ""
        with open(file, encoding='utf-8') as f:
            for line in f:
                for word in line.split():
                    if(word.isalpha() and (word in wordSet)):
                        word = word.lower()
                        if(word not in stop_words):
                            finWord = lemmatizer.lemmatize(word)
                            if(finWord not in tempDict):
                                finSyllabus += finWord + " "
                            tempDict.add(finWord)
        syllabiParsed.append(finSyllabus)

tfidf = TfidfVectorizer()

result = tfidf.fit_transform(syllabiParsed)
result = pd.DataFrame(result.toarray())

X = np.array(result)
y = np.array(targetValues)

clf = svm.SVC(probability=True)
clf.fit(X, y)

print()
print("Training Score (accuracy: 1.0 = 100%) = ",end="")
print(clf.score(X,y),"\n")

####################################################################################
# Necessary functions
####################################################################################

# testFileToVec: Convert test txt file to vectors
def testFileToVec(file, tfidf):
    tempDict = set()
    lemmatizer = WordNetLemmatizer()
    finSyllabus = ""
    testFileParased = []
    with open(file, encoding='utf-8') as f:
        for line in f:
            for word in line.split():
                if(word.isalpha() and (word in wordSet)):
                    word = word.lower()
                    if(word not in stop_words):
                        finWord = lemmatizer.lemmatize(word)
                        if(finWord not in tempDict):
                            finSyllabus += finWord + " "
                        tempDict.add(finWord)
    testFileParased.append(finSyllabus)

    result = tfidf.transform(testFileParased)
    result = pd.DataFrame(result.toarray())

    X = np.array(result)
    return X


# getSpamProbability: Get bias probaility 
def getBiasProbability(file, testVec):
    print("Bias test: ", file)
    print("   Answer                          = ", clf.predict(testVec))
    print("   NotBiased vs Biased probability = ", clf.predict_proba(testVec)) 
    if clf.predict(testVec)[0] == 1:
        print(clf.predict(testVec))
        print("It is biased")
    elif clf.predict(testVec)[0] == 0:
        print(clf.predict(testVec))
        print("It is not biased")
    print("")

####################################################################################
# Testing
####################################################################################

for fileName in os.listdir(currentDirPath + "/SvmAndBERT/testSyllabiTxt"):
    if file[-4:] == '.txt' and os.path.isfile(file):
        print(fileName)
        file1 = "testSyllabiTxt/" + fileName
        test1 = testFileToVec(currentDirPath + '/SvmAndBERT/' + file1, tfidf)

        getBiasProbability(file1, test1)

        