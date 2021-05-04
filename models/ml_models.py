# Get all data for specific category
import requests
import random
import pandas as pd
from sklearn import tree,ensemble,naive_bayes
import operator
import numpy as np
import json

global item_name
item_name = "title" #"tool_name" #title
global item_id
item_id = "movie_id" #"tool_id" #movie_id
global uri
uri =  "http://127.0.0.1:5000"#"https://selectify-mvp.herokuapp.com"#f"http://127.0.0.1:5000"


class trainer:
    def __init__(self,category_id,uri,data_endpoint,question_endpoint,movies_endpoint):
        self.uri = uri
        self.data_endpoint = data_endpoint
        self.question_endpoint = question_endpoint
        self.item_endpoint = movies_endpoint
      
        self.category_id = str(category_id)
        
        # Get data
        self._get_training_data()
        
        # Fit inital model
        self.simple_model = self._simple_fit(self.X_train, self.y_train)
        # Fit model with noise data
        self.model = self._fit(self.noisy_X_train,self.noisy_y_train)
        
        #questions mapping
        self.questions_mapping = {e["id"]:e["question"] for e in self.questions_data}
        
        # item answer mapping
        self.item_question_mapping = []
        for e in self.items:
            self.item_question_mapping.append({
                "id":e["id"],
                "name":e[item_name],
                "answers": self._reformat_items(e["id"])
            })
        # item dict
        self.item_dict = {e["id"]:e[item_name] for e in self.items}
        
    def _retrieve_paginated_data(self,endpoint):
        data = []
        keep_going = True
        page = 1
        
        while keep_going:
            print("GET ",self.uri+endpoint+f"?page={page}")
            res = json.loads(requests.get(self.uri+endpoint+f"?page={page}").text)
            if not res["success"]:
                break
            # add data
            data += res["data"]
            # Gext next movie page
            page +=1
        return(data)
    
    def _reformat_items(self,item_id):
        return(self.train_df.iloc[self.train_df.index == item_id,].to_dict("r")[0])
    
    def _get_training_data(self,index_col =item_id,columns=["question_id"], values ="answer" ):
        #Get answer data
        self.data = self._retrieve_paginated_data(self.data_endpoint+self.category_id)
        #Get questions (Specific)
        self.questions_data = self._retrieve_paginated_data(self.question_endpoint+self.category_id)

        #Get items
        self.items = self._retrieve_paginated_data(self.item_endpoint+self.category_id)
        
        #Transform to sklearn trainingsset
        #Generate trainingsdata without noise
        df = pd.DataFrame.from_dict(self.data)
        
        self.train_df = df.pivot_table(index=index_col,columns=columns,values=values)
        self.y_train = pd.get_dummies(pd.DataFrame(self.train_df.index.to_list(), columns=[self.train_df.index.name]), columns=[self.train_df.index.name] ).to_numpy()
        self.X_train = self.train_df.to_numpy()
        #Get feature and target names / ids
        self.y_ids = self.train_df.index.to_numpy()
        self.X_ids = self.train_df.columns
        
        #Generate trainingsdata without noise
        self.noisy_train_df = self._generate_noisy_data(self.train_df)
        self.noisy_y_train = pd.get_dummies(pd.DataFrame(self.noisy_train_df.index.to_list(), 
                                                         columns=[self.noisy_train_df.index.name]), 
                                                            columns=[self.noisy_train_df.index.name] ).to_numpy()
        self.noisy_X_train = self.noisy_train_df.to_numpy()
        
    def _generate_noisy_data(self,df,additional_samples_per_tool=10,n_replace_min=2,n_replace_max=5):
        new_df = df
        for j,row in df.iterrows():
            i = 0
            while i<additional_samples_per_tool:
                i+=1
                new = self._replaceRandom(row,np.random.randint(n_replace_min,n_replace_max))
                new = pd.Series(data = new,name=row.name,index = row.index)
                new_df=new_df.append(new)
        return(new_df)
    
    def _replaceRandom(self,arr, num):
        temp = np.asarray(arr)   # Cast to numpy array
        shape = temp.shape       # Store original shape
        temp = temp.flatten()    # Flatten to 1D
        inds = np.random.choice(temp.size, size=num)   # Get random indices
        temp[inds] = -1        # Fill with something
        temp = temp.reshape(shape)                     # Restore original shape
        return temp
        
    def _simple_fit(self,X_train, y_train,random_state=1992):
        ################ Fits an overfitting decisionTree that cannot handel noise well ################
        model = tree.DecisionTreeClassifier(random_state=random_state)#tree.DecisionTreeClassifier(random_state=random_state,max_features="sqrt",max_depth=3)#,max_depth=5 ,max_features="sqrt")
        model.fit(X_train, y_train)
        return(model)
    
    def _fit(self,X_train, y_train,random_state=1992):
        ################ Fits a RandomForest that can handle noise well ################
        model = ensemble.RandomForestClassifier(random_state=random_state)#tree.DecisionTreeClassifier(random_state=random_state,max_features="sqrt",max_depth=3)#,max_depth=5 ,max_features="sqrt")
        model.fit(X_train, y_train)
        
        return(model)


class finder:
    def __init__(self,trainer,use_model = "advanced",responses_so_far=[]):
        ########################
        # trainer --- training object that is being generated with class trainer and contains the trained model
        # use_model --- if = base the basic decision tree model is used that was trained without noisy data ['base','advanced']
        # responses_so_far -- list of dicts of the form {answer_id:answer}
        ########################
        self.trainer = trainer
        self.responses_so_far = {list(item.keys())[0]:list(item.values())[0] for item in responses_so_far}
        self.use_model = use_model
        self.questions_asked_so_far = [list(e.keys())[0] for e in responses_so_far]
        
        # Generate prior for predictions
        if self.use_model == "base":
            self.prior = np.array([[0.5]*self.trainer.X_train.shape[1]])
        elif self.use_model == "advanced":
            self.prior = np.array([[-1]*self.trainer.X_train.shape[1]])

        # Update prior with responses so far
        for q_id in self.questions_asked_so_far:
            idx = np.where(self.trainer.X_ids == q_id)
            self.prior[0][idx] = self.responses_so_far[q_id]

        #Select prediction model to be used
        if self.use_model not in ["base","advanced"]:
            raise ValueError("Please specify a correct parameter for <use_model>")
        if self.use_model == "base":
            self.pred_model = self.trainer.simple_model
        elif self.use_model == "advanced":
            self.pred_model = self.trainer.model
            
        # Get question importance
        self._get_question_importance(self.pred_model)

        # Init available questions
        self.available_questions = {}
        for key in self.feature_imp:
            # check responses so far
            if key in self.questions_asked_so_far:
                continue
            else:
                self.available_questions.update({key:self.feature_imp[key]})
            
    def _get_question_importance(self,model):
        # Feature importance
        self.feature_imp = {}
        scores = model.feature_importances_
        for i,e in enumerate(self.trainer.X_ids):
            try:
                self.feature_imp[e] = scores[i]
            except:
                continue
        #print(len(self.feature_imp))
    def _add_answer(self,question_id,answer):
        # Remove currently asked question from available questions
        self.available_questions.pop(question_id)
        # Update prior
        idx = np.where(self.trainer.X_ids == question_id)
        self.prior[0][idx] = answer

    def _predict(self):
        #print(self.prior)
        # predict
        pred = self.pred_model.predict_proba(self.prior)
        pred = [el[:,1] for el in pred]

        results = {}
        # generate item id mapping on pred probability
        for i,e in enumerate(pred):
            results[self.trainer.y_ids[i]]=e[0]
        
        # get max probability item
        best_idx = max(results.items(), key=operator.itemgetter(1))[0]
        
        #Choose next question
        next_question_id = self._choose_best_next_Question()
        if next_question_id:
            return({"all_results":results,"best_item_id":best_idx,"best_item_prob":results[best_idx],
                    "next_question_id":next_question_id,
                    "next_question_text":self.trainer.questions_mapping[next_question_id]})
        else:
            return({"all_results":results,"best_item_id":best_idx,"best_item_prob":results[best_idx],
                    "next_question_id":None,
                    "next_question_text":None})
    
    def _choose_best_next_Question(self):
        try:
            best_q = max(self.available_questions.items(), key=operator.itemgetter(1))[0]
            #self.available_questions.pop(best_q, None)
            return(best_q)
        except:
            return(None)

      
    
        