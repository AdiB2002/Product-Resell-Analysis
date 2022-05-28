import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import pickle

class ML():
    
    # constructor
    def __init__(self, df = pd.DataFrame()):
        self.df = df
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []
        
    # splits in training and testing datasets 
    def train_test_split(self, test_size = .2, target_column_name = ''): 
        X = self.df.drop([target_column_name], axis=1)
        y = self.df[target_column_name]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size = test_size, random_state = 22)
    
    # analysis using ML models on data (for model accuracy testing)
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
        cm_list = []
        
        # loops through models
        for model in model_pipeline:
            model.fit(self.X_train, self.y_train) # fit model
            y_pred = model.predict(self.X_test) # predict using model
            
            # metrics for accuracy
            acc_list.append(metrics.accuracy_score(self.y_test, y_pred))
            fpr, tpr, _thresholds = metrics.roc_curve(self.y_test, y_pred)
            auc_list.append(round(metrics.auc(fpr, tpr),2))
            cm_list.append(confusion_matrix(self.y_test, y_pred))
        
        # confusion matrix code and can be viewed in Plots
        fig = plt.figure(figsize = (18,10))
        for i in range(len(cm_list)):
            cm = cm_list[i]
            model = model_list[i]
            sub = fig.add_subplot(2, 3, i+1).set_title(model)
            cm_plot = sns.heatmap(cm, annot=True, cmap='Blues_r')
            cm_plot.set_xlabel('Predicted Values')
            cm_plot.set_ylabel('Actual Values')
         
        # dataframe of accuracy results     
        results_df = pd.DataFrame({'Model': model_list, 'Accuracy': acc_list, 'AUC': auc_list})
        
        # return results dataframe
        return results_df
    
    # training an ML model 
    def ML_training(self):
        
        # creates models and fits it to training data
        LR = LogisticRegression()
        LR.fit(self.X_train, self.y_train)
        
        # returns the model
        return LR
    
    # prediction using ML on future game data 
    def ML_prediction(self, model = '', future_game_df_copy = pd.DataFrame()):
        
        # gets the predictions as a list using inputted model
        y_pred = model.predict(self.df.iloc[:, 0:-1])
        
        # adds predictions to results column and returns future game schedule
        future_game_df_copy['Result'] = y_pred
        return future_game_df_copy
        
# some simple exploratory analysis
def exploratory_analysis(df = pd.DataFrame()):  
    
    # prints info about columns inlcuding data type and non null count for columns
    df.info()
    
    # creates a correlation matrix that can be found in plots
    correlation = df.corr()
    sns.heatmap(correlation, cmap = "GnBu", annot = True)

# preparing the data for machine learning
def data_preparation(team_stats_df=pd.DataFrame(), game_data_df=pd.DataFrame()):
    
    # manually resetting the team stats index because it includes clubs cities and the game data doesn't have that
    team_stats_df.index = ['Diamondbacks', 'Braves', 'Orioles',
       'Red Sox', 'Cubs', 'White Sox',
       'Reds', 'Guardians', 'Rockies',
       'Tigers', 'Astros', 'Royals',
       'Angels', 'Dodgers', 'Marlins',
       'Brewers', 'Twins', 'Mets',
       'Yankees', 'Athletics', 'Phillies',
       'Pirates', 'Padres', 'Mariners',
       'Giants', 'Cardinals', 'Rays',
       'Rangers', 'Blue Jays', 'Nationals',
       'League Average']
    
    # gets all the home teams and creates the home columns list
    home_teams = list(game_data_df['Home_Team'])
    home_columns = []
    
    # loops through the columns of team stats adding Home_ to the front of each column name
    for column in list(team_stats_df.columns):
        home_columns.append('Home_' + column)
    
    # creates the dataframe for all home team data 
    home_team_df = pd.DataFrame(columns=home_columns)
    
    # loops through home teams adding each teams data to the home team dataframe 
    for home_team in home_teams:
        home_team_list = list(team_stats_df.loc[[home_team]].iloc[0])
        home_team_df.loc[len(home_team_df)] = home_team_list
    
    # everything that was done for home needs to be done for away as well
    away_teams = list(game_data_df['Away_Team'])
    away_columns = []
    for column in list(team_stats_df.columns):
        away_columns.append('Away_' + column)
    away_team_df = pd.DataFrame(columns=away_columns)
    for away_team in away_teams:
        away_team_list = list(team_stats_df.loc[[away_team]].iloc[0])
        away_team_df.loc[len(away_team_df)] = away_team_list
    
    # creates a combined dataframe with home and away team data
    combined_df = pd.concat([home_team_df, away_team_df], axis=1, join="inner")
    
    # one hot encoder for team names
    encoder = OneHotEncoder(sparse=False)
    
    # dataframe of home teams
    df = pd.DataFrame({'Home_Team': home_teams})
    
    # one hot encoded dataframe for home teams
    home_enc_df = pd.DataFrame(encoder.fit_transform(df), columns=encoder.get_feature_names(['Home']))
    
    # what was done for home is done for away as well
    df = pd.DataFrame({'Away_Team': away_teams})
    away_enc_df = pd.DataFrame(encoder.fit_transform(df), columns=encoder.get_feature_names(['Away']))
    
    # combines home and away encoded dataframes
    combined_enc_df = pd.concat([home_enc_df, away_enc_df], axis=1, join="inner")
    
    # combines the encoded dataframe and the team data
    combined_df = pd.concat([combined_enc_df, combined_df], axis=1, join="inner")
    
    # inserts the week column into the dataframe
    combined_df.insert(loc=0, column='Week', value=list(game_data_df['Week']))
    
    # adds results column into the dataframe
    # try except is needed because converting all values to integer for training but for predicting this throws an error
    try:
        result_list = [int(i) for i in list(game_data_df['Result'])]
    except:
        result_list = list(game_data_df['Result'])
    
    # inserts results column into the dataframe
    combined_df.insert(loc=len(combined_df.columns), column='Result', value=result_list)

    # returns the combined dataframe
    return combined_df

# saves ML model
def save_ML_model(model = '', file = ''):
    pickle.dump(model, open(file, 'wb'))

# loads and returns a ML model 
def load_ML_model(file = ''):
    model = pickle.load(open(file, 'rb'))
    return model  
    
def main():
    
    # reads in the team stats which can be downloaded and converted to csv manually at https://www.baseball-reference.com/leagues/majors/2022.shtml
    team_stats_df = pd.read_csv('C:/Computer Science/MLB Game Prediction/Team Statistics.csv', index_col=0)
    
    # gets the game data
    game_data_df = pd.read_csv('C:/Computer Science/MLB Game Prediction/MLB Game Data.csv')
    
    # separates future game data from game data 
    future_game_df = game_data_df[game_data_df['Result']=='No Result']
    
    # makes a copy of future game data that will be exported because its teams won't have been one hot encoded 
    future_game_df_copy = future_game_df.copy()
    
    # separates past game data from game data 
    game_data_df = game_data_df[game_data_df['Result']!='No Result']
    
    # prepares data from ML and will take the two parameters team statistics and either game data or future game data 
    # taking game data so going to be training model(s)
    df = data_preparation(team_stats_df, game_data_df)
    
    # creates a ML object
    ML_obj = ML(df)
    
    # train test split that takes test size and target column name as parameters 
    ML_obj.train_test_split(test_size=.2, target_column_name='Result')
    
    # tests multiple ML model accuracies and prints them out
    #print(ML_obj.ML_analysis())
    
    # training a model that takes no parameters and returns the trained model
    model = ML_obj.ML_training()
    
    # saves a ML model and takes a model and file as parameters
    #save_ML_model(model, 'C:/Computer Science/MLB Game Prediction/Trained MLB Model.pkl')
    
    # loads and returns a saved model and takes file as a parameter
    #model = load_ML_model('C:/Computer Science/MLB Game Prediction/Trained MLB Model.pkl')
    
    # this time taking future game data so going to be predicting data
    pred_df = data_preparation(team_stats_df, future_game_df)
    
    # changes dataframe to pred_df in ML object
    ML_obj.df = pred_df
    
    # predicts data and takes a model and future game data copy as parameters while returning a prediction dataframe for exporting
    prediction_df = ML_obj.ML_prediction(model, future_game_df_copy)
    
    # exports df to csv
    prediction_df.to_csv('C:/Computer Science/MLB Game Prediction/MLB Prediction Data.csv', index = False) 
    
main()