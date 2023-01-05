import re
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.svm import LinearSVC


def read(file):
    data = []
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            label = ' '.join(line[1:line.find("]")].strip().split())
            text = line[line.find("]") + 1:].strip()
            data.append([label, text])
    return data


file = 'final_text.txt'
data = read(file)
print("Number of instances: {}".format(len(data)))


# 2 tokenizer function to generate the features of an input sentence

def ngram(token, n):
    output = []
    for i in range(n - 1, len(token)):
        ngram = ' '.join(token[i - n + 1:i + 1])
        output.append(ngram)
    return output


def create_feature(text, nrange=(1, 1)):
    text_features = []
    text = text.lower()
    text_alphanum = re.sub('[^a-z0-9#]', ' ', text)
    for n in range(nrange[0], nrange[1] + 1):
        text_features += ngram(text_alphanum.split(), n)
    text_punc = re.sub('[a-z0-9]', ' ', text)
    text_features += ngram(text_punc.split(), 1)
    return Counter(text_features)


# function to store labels, labels will be based on emotions such as Fear, Anger, Sad, Nostalgia, Calm, Joy

def convert_label(item, name):
    items = list(map(float, item.split()))
    label = ""
    for idx in range(len(items)):
        if items[idx] == 1:
            label += name[idx] + " "

    return label.strip()


emotions = ["joy", "fear", "anger", "sadness", "calmness", "nostalgia", "guilt"]

X_all = []
y_all = []
for label, text in data:
    y_all.append(convert_label(label, emotions))
    X_all.append(create_feature(text, nrange=(1, 4)))

X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=0.2, random_state=123)


def train_test(clf, X_train, X_test, y_train, y_test):
    clf.fit(X_train, y_train)
    train_acc = accuracy_score(y_train, clf.predict(X_train))
    test_acc = accuracy_score(y_test, clf.predict(X_test))
    return train_acc, test_acc


from sklearn.feature_extraction import DictVectorizer

vectorizer = DictVectorizer(sparse=True)
X_train = vectorizer.fit_transform(X_train)
X_test = vectorizer.transform(X_test)

lsvc = LinearSVC(random_state=123)

# train and test them
print("| {:25} | {} | {} |".format("Classifier", "Training Accuracy", "Test Accuracy"))
print("| {} | {} | {} |".format("-" * 25, "-" * 17, "-" * 13))
lsvc_name = lsvc.__class__.__name__
train_acc, test_acc = train_test(lsvc, X_train, X_test, y_train, y_test)
print("| {:25} | {:17.7f} | {:13.7f} |".format(lsvc_name, train_acc, test_acc))

l = ["joy", "fear", "anger", "sadness", "calmness", "nostalgia", "guilt"]
l.sort()
label_freq = {}
for label, _ in data:
    label_freq[label] = label_freq.get(label, 0) + 1

# print the labels and their counts in sorted order
for l in sorted(label_freq, key=label_freq.get, reverse=True):
    print("{:10}({})  {}".format(convert_label(l, emotions), l, label_freq[l]))


#combines and returns the final prediction
def final(text):
    features = create_feature(text, nrange=(1, 4))
    features = vectorizer.transform(features)
    prediction = lsvc.predict(features)[0]
    return prediction

