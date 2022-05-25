import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics

class ML():
    
    # constructor
    def __init__(self, df = pd.DataFrame()):
        self.df = df
        self.orig_df = df
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []
        
    # splits in training and testing datasets 
    def train_test_split(self, test_size = .2, target_column_name = ''): 
        X = self.df.drop([target_column_name], axis=1)
        y = self.df[target_column_name]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size = test_size, random_state = 22)
     
    # special version of one hot encoding required because text column is more than 1 word in each column
    # tokenization was done to each column and max amount of features can be added using word frequency as the determining factor
    # parameters are a text column and feature amounts
    def special_one_hot_encoder(self, column = [], feature_amount = -1):
        
        # gets a list of words from text column sorted by highest word frequency 
        ordered_feature_list = list(column.str.split(expand=True).stack().value_counts().index)[:feature_amount]
        
        # creates a dataframe of 0's of correct size and column names
        enc_df = pd.DataFrame(0, index=range(len(self.df.index)), columns=ordered_feature_list)
        
        # loops through column checking if each word in each row for one hot encoding
        column_list = list(column)
        for i in range(0, len(column_list)):        
            row_word_list = column_list[i].split() # tokenization step
            for word in row_word_list: 
                if(word in ordered_feature_list): # if word in column list 
                    enc_df.at[i, word] = 1 # make cell value 1
          
        # return encoded dataframe
        return enc_df
     
    # one hot encoding for a text column 
    def one_hot_encode_text_column(self, column_name_list = [], feature_amount_list = []):
        
        # loops through text column names
        for i in range(0, len(column_name_list)):
            
            # gets desired text column from dataframe and drops it as well
            column = self.df[column_name_list[i]]
            self.df = self.df.drop(column_name_list[i], 1)
            
            # one hot encodes text column into a different encoded dataframe
            enc_df = self.special_one_hot_encoder(column, feature_amount_list[i])
            
            # adds encoded dataframe to original dataframe at the start and drops unnecessary index columns that are added 
            self.df = pd.concat([enc_df.reset_index(), self.df.reset_index()], axis=1)
            self.df = self.df.drop('index', 1)
    
    # analysis using ML models on data
    def ML_analysis(self):
        
        # create a model pipeline and appends various models for testing
        model_pipeline = []
        model_pipeline.append(LogisticRegression())
        model_pipeline.append(RandomForestClassifier())
        model_pipeline.append(SVC())
        model_pipeline.append(KNeighborsClassifier())
        model_pipeline.append(GaussianNB())
        
        # lists for output
        model_list = ['Logistic Regression', 'Random Forest', 'SVC', 'KNN', 'Naive Bayes']
        acc_list = []
        auc_list = []
        
        # loops through models
        for model in model_pipeline:
            model.fit(self.X_train, self.y_train) # fit model
            y_pred = model.predict(self.X_test) # predict using model
            
            # metrics for accuracy
            acc_list.append(metrics.accuracy_score(self.y_test, y_pred))
            fpr, tpr, _thresholds = metrics.roc_curve(self.y_test, y_pred)
            auc_list.append(round(metrics.auc(fpr, tpr),2))
         
        # dataframe of accuracy results     
        results_df = pd.DataFrame({'Model': model_list, 'Accuracy': acc_list, 'AUC': auc_list})
        
        # return results dataframe
        return results_df
        
# some simple exploratory analysis
def exploratory_analysis(df = pd.DataFrame()):  
    
    # prints info about columns inlcuding data type and non null count for columns
    df.info()
    
    # creates a correlation matrix that can be found in plots
    correlation = df.corr()
    sns.heatmap(correlation, cmap = "GnBu", annot = True)
    
    # formatting
    print('\n')

def main():
    
    # read in excel file as dataframe and drop rows that are null
    df = pd.read_excel('') 
    
    # takes dataframe as parameter and has a couple exploratory analysis methods to look at 
    exploratory_analysis(df)
    
    ML_obj = ML(df)
    
    # one hot encoding that takes list of text column names and list of respective max amount of features as parameters
    # if all unique features from column are wanted put -1 or arbitrarily high number 
    ML_obj.one_hot_encode_text_column(column_name_list = ['Name', 'Website', 'Category'], feature_amount_list = [-1, -1, -1])
    
    # splits data into train test split and takes test size and target column name as parameter
    ML_obj.train_test_split(test_size = .2, target_column_name = 'Feasability')
    
    # run ML analysis using multiple models on dataframe and print accuracy results
    print(ML_obj.ML_analysis())
    
main()