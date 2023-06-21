import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

folder_path = './resources/'
files = os.listdir(folder_path)

positive_cases = []
negative_cases = []

for file_name in files:
    # These two files are training our model for Positive cases to identify HUMAN names
    if file_name in ['firstnames.txt', 'lastnames.txt']:   
      file_path = os.path.join(folder_path, file_name)
      if os.path.isfile(file_path):
          with open(file_path, 'r', errors='ignore') as file:
              file_contents = file.readlines()
          words = [word[:(len(word) - 1)].lower() for word in file_contents]
          positive_cases += words
    # These files are training our model for Negative cases to identify a words other than HUMAN names
    else:
      file_path = os.path.join(folder_path, file_name)
      if os.path.isfile(file_path):
          with open(file_path, 'r', errors='ignore') as file:
              file_contents = file.readlines()
          words = [word[:(len(word) - 1)].lower() for word in file_contents]
          negative_cases += words

positive_cases = list(set(positive_cases))
negative_cases = list(set(negative_cases))

positive_case_result = [1 for _ in range (len(positive_cases))]
negative_case_result = [0 for _ in range (len(negative_cases))]

total_cases = positive_cases + negative_cases
results = positive_case_result + negative_case_result

data = pd.DataFrame({"Name": total_cases, "Label": results})

train_data, val_data, train_labels, val_labels = train_test_split(data["Name"], data["Label"], test_size=0.01, random_state=42)

# Creating a CountVectorizer to convert names into numerical features
vectorizer = CountVectorizer(lowercase=True, analyzer="char")
train_features = vectorizer.fit_transform(train_data)
val_features = vectorizer.transform(val_data)

# Training a logistic regression model
model = LogisticRegression(max_iter=1000)
model.fit(train_features, train_labels)

# Predicting labels for the validation set
# val_predictions = model.predict(val_features)

# Evaluating the model
# accuracy = accuracy_score(val_labels, val_predictions)
# print("Validation Accuracy:", accuracy)

# pdf_text = ['harshvi']
# X = vectorizer.transform(pdf_text)
# print(model.predict(X))
