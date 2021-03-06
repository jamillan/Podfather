from  data_process   import * 

from sklearn.feature_extraction.text import TfidfVectorizer
import time
import tweepy 
import random
import unirest



CONSUMER_KEY = "MY CONSUMER_KEY"
CONSUMER_SECRET = "MY CONSUMER_SECRET"
ACCESS_TOKEN = "MY ACCESS TOKEN"
ACCESS_TOKEN_SECRET = "MY ACCESS TOKEN SECRET"


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)





tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
tfidf_train = tfidf_vectorizer.fit_transform(data)


# BOT class is in charge of deploying a podcast tweetbot. It listens to tweets of users and
# proceeds to performs cosine similarity (TF-IDF), LDA, and
# detection of user's friends to finally provide urls of podcasts that matched the sentiment
# interests of users.

class bot():
    
    #constructor class
    def __init__(self, _tfidf_vectorizer= None):
            
				#Check if TF_IDF has been created correctly
        if _tfidf_vectorizer == None:
            raise RuntimeError('need to create the tfifd_vectorizer infrastructure of the podcasts')
        

        self. tfidf_vectorizer = _tfidf_vectorizer;
        
		#Funtion To linearlize user tweets and use cosine similarity to find closest podcast to user tweet
    def get_from_tfidf(self,user ='kanyewest',nbr_tweets = 3):

        #get 10 usertwets and linearize them
        user_tweets = pd.read_csv(user + '_tweets.csv')
        user_tweets = user_tweets.text.values[:10]

        #vectorize the user's tweets
        all_X_test = tfidf_vectorizer.transform(user_tweets)

        #weigh tweets based on how new they are
        weights = range(1,len(all_X_test.A));
        weights = sorted(weights,reverse=True)


        X_test = tfidf_vectorizer.transform(user_tweets)
        final_vect = X_test[0]

        #container of podcasts descriptions, podcasts ulrs  and podcast infor
        podcast_descriptions = []
        final_urls = []
        all_pod_candidates = []
        all_pod_descriptions = []


        for idx,vec_X in enumerate(X_test[:]):


           # weight = weights[idx]

            
            final_vect = vec_X + final_vect

           #cosine similarity
            a= np.dot(vec_X,tfidf_train.T)
            a_sort = np.argsort(a.A)
            max_vals_idx =  a_sort.flatten()[::-1][:10]

            #add candidates to list description
            for idx in max_vals_idx:
                podcast_descriptions.append(data[idx])

            #localize the information of tweets
            urls  = final_df.loc[max_vals_idx].website_url.values.tolist()
            all_pod_candidates  = all_pod_candidates + urls
            all_pod_descriptions = all_pod_descriptions + final_df.loc[max_vals_idx].content2.values.tolist()
            final_urls = final_urls + random.sample(urls,5)

        #select recommendations and administer information of it
        final_pods = random.sample(final_urls,nbr_tweets)
        print("Pocast Match based on Twitter Posting: " + '\n')
        for idx,_final_url in enumerate(final_pods):
            print("Match Number " + str(idx) +' :' + '\n')
            index = all_pod_candidates.index(_final_url)
            print(all_pod_descriptions[index]);
            print(' ');
        
        return final_pods,podcast_descriptions , max_vals_idx;
    

    
    def get_from_hashtag(self,all_hashtags):

        #this functions looks at who the user is following and connects to
        #listen notes to check if it can find a podcast based who the user is
        # following

        #decompose the user' friends name into two tokens based on the assumption
        # that friends' names are two joined Capitalized tokens each.
        
        all_bi_tokens = []
        for h_tag in all_hashtags:

            trial_bitoken = split_hashtag(h_tag)
           # print(trial_bitoken)
            if len(trial_bitoken) > 1:
                all_bi_tokens.append(trial_bitoken)

        print(all_bi_tokens)
        if len(all_bi_tokens) > 0:
            random.shuffle(all_bi_tokens)

        else:
            #If we are here we did not find bitokens
            #the tweetbot handles this circumstance by submitting popular podcasts
            return [],None,None




        for i in range(len(all_bi_tokens)):
            
            #
            hash_signal = all_bi_tokens[i]
            final_hash_signal = hash_signal[0]
            h_tag_user = "@" + hash_signal[0]
            check_hash = hash_signal[0]

            for j in range(1,len(hash_signal)):

                final_hash_signal = final_hash_signal + "+" + hash_signal[j]
                h_tag_user = h_tag_user + hash_signal[j]
                check_hash = check_hash + hash_signal[j]

            #print candidate celebrity
            print(check_hash)
            #check if this is a celebrity and then connect to listen notes
						
            #If we have a name of a potential celebrity
            #check first that it is a celebrity and connect to his/her account
            if check_hash in all_hashtags:

            #check how many friends he/she has
                try:

                    user = api.get_user(h_tag_user)


                except tweepy.error.TweepError as e:
                    time.sleep(180)
                    user = api.get_user(h_tag_user)
                try:
                    #nbr of frinds
                    nbr_friends = user.followers_count



                except tweepy.error.TweepError as e:
                    time.sleep(180)
                    nbr_friends = user.followers_count

                #celebrity?
                if nbr_friends < 3000:
                    #if not then look for another target friend
                    print('not celebrity')
                    continue;

                else:
                    
                    #if so then connect to Listen Notes and extract a podcast episode from this celebrity
                    #blindly trust Listen Notes
                    print(final_hash_signal)
                    response = unirest.get("https://listennotes.p.mashape.com/api/v1/search?genre_ids=68%2C110&language=English&len_max=50&len_min=2&offset=0&only_in=Only+search+in+these+fields&published_after=1390190241000&published_before=1490190241000&q=" + final_hash_signal + "&sort_by_date=0&type=episode",
                                headers={
                                "X-Mashape-Key": "",
                                "Accept": "application/json"
                                          }
                                        )

                    listen_notes_pods = response.body['results']

                    #if we have a connection then return url results
                    response_listen_notes=[]
                    if len(listen_notes_pods)> 0:
                        print('found')
                        rand_pod = random.choice(listen_notes_pods)
                      #  print(rand_pod)
                        response_listen_notes.append(rand_pod[u'audio'])
                        return response_listen_notes, h_tag_user,final_hash_signal
                    else:
                        continue




            else:

                continue;


        #if we here we did not find any celebrity
        #
        return [],None,None  
    
    def get_from_listen_notes(self, descriptions):
        #find most common words 'buzz words' and connect
        #to listen notes to find podcast with combination of common words

        Xtr = tfidf_vectorizer.transform(descriptions)
        features = tfidf_vectorizer.get_feature_names()

        buzz_words = []
				
        for i in range(30):
            a = top_feats_in_doc(Xtr, features, row_id=i, top_n=50)
            word = a.feature.values.tolist()[0]
            buzz_words.append(word)

        final_string = set(buzz_words)
        buzz_words = list(final_string)
        final_string = random.choice(buzz_words)
        for i in range(1):

            trial_word = random.choice(buzz_words)
            final_string = final_string + "+" + trial_word

        response = unirest.get("https://listennotes.p.mashape.com/api/v1/search?genre_ids=68%2C100&language=English&len_max=60&len_min=2&offset=0&only_in=Only+search+in+these+fields&published_after=1390190241000&published_before=1490190241000&q=" + final_string + "&sort_by_date=0&type=episode",
          headers={
            "X-Mashape-Key": "",
            "Accept": "application/json"
          }
        )

        listen_notes_pods = response.body['results']


        response_listen_notes=[]
        if len(listen_notes_pods)> 0:
            rand_pod = random.choice(listen_notes_pods)
            response_listen_notes.append(rand_pod[u'audio'])

        return response_listen_notes;

    
    def listen_notes_favorite(self, n='All'):
        #These code snippets use an open-source library. http://unirest.io/python
        #find most popular podcast from listen notes
        response = unirest.get("https://listennotes.p.mashape.com/api/v1/best_podcasts?page=1",
                           headers={
                           "X-Mashape-Key": "",
                           "Accept": "application/json"
                           }
                           )
        
        listen_notes_pods = response.body['channels']
       # print(listen_notes_pods[1]['website'])
        response_listen_notes=[]
        if len(listen_notes_pods) > 5:
           
           for i in range(3):
               response_listen_notes.append(listen_notes_pods[i][u'website'])

        else:
    
            for i in range(len(listen_notes_pods)):
                response_listen_notes.append(listen_notes_pods[i][u'website'])
    
        url_string = str();
        if n == 'All' or n == 0:
            
            for i in response_listen_notes:
                url_string = url_string + " " + str(i)

        else:
            for i in range(n):
                _url = response_listen_notes[i]
                url_string = url_string + " " + str(_url)

            return url_string
    
    

    def run(self):
		#kernel to run the tweet bot
		# infinite loop to read the podfather's timeline and
		# 
        
        #loop through twwets in timeline
        stop_name = str()
        #loop through twwets in timeline
        nbr_loops = 0
        #initial_time = time.time()

        while True:
            #Check after some time how much loops are performed in 4 hours
            if nbr_loops % 1309==0:
                
                #print("loop: " + str(i))
                print("loop in multiple of 4 hours: " + str(int(nbr_loops/1309.)))
            
            nbr_loops += 1;
         
            #Read timeline
            try:
                #loop_initial_time = time.time()
                public_tweets = api.mentions_timeline(count=10)
                #time_file = open('time.dat','a')
                loop_final_time = time.time()
                #time_file.write(str(loop_final_time - loop_initial_time) + "\n")
                #time_file.flush()
                #time_file.close()
            except tweepy.error.TweepError as e:
                
                time.sleep(5*60)
      #          loop_initial_time = time.time()
                public_tweets = api.mentions_timeline(count=10)
       #         time_file = open('time.dat','a')
        #        loop_final_time = time.time()
                #time_file.write(str(loop_final_time - loop_initial_time) + "\n")
                #time_file.flush()
                #time_file.close()
            
            #Check who was the last user
            final_name,finalstamp = get_last_user()
            
            #look through the tweets sent to the tweetbot
            #It will stop once it finds the last user/sender
            
            for idx,tweet in enumerate(public_tweets):
                
                #print("found tweet :" + str(idx))
                #  print(tweet.text)
                #break on other tweets
                
                
                #split tweet to get username
                try:
                    buffer_str =str(tweet.text).split()
                except tweepy.error.TweepError as e:
                    time.sleep(180)
                    buffer_str =str(tweet.text).split()
                
                #get into first tweet
                #and store the timestamp to find out who was the last user
                if idx ==0:
                    sn = str()
                    try:
                        #user = api.get_user(tweet.id)
                        #user screen name
                        sn = tweet.user.screen_name
                        my_file = open('last_user.dat','w')
                        my_file.write(sn + " " + str(tweet.created_at))
                        my_file.close()
                    except tweepy.error.TweepError as e:
                        time.sleep(180)
                        
                        #user screen name
                        sn = tweet.user.screen_name
                        my_file = open('last_user.dat','w')
                        my_file.write(sn + " " + str(tweet.created_at))
                        my_file.flush()
                        my_file.close()

                if idx >=0:
                    #user info
                    #Get name
                    sn = str()
                    try:
                        #user = api.get_user(tweet.id)
                        #user screen name
                        sn = tweet.user.screen_name
                    except tweepy.error.TweepError as e:
                        time.sleep(180)
                    
                    #user screen name
                    sn = tweet.user.screen_name
                    # print(sn)
                    
                    #Get tweet info to check if it is a new tweet or an old one
                    timestamp_tweet = tweet.created_at
                    timestamp_tweet = pd.Timestamp(timestamp_tweet)
                    timestamp_tweet = timestamp_tweet.to_pydatetime()
                    
                    check_stamp= different_timestamp(timestamp_tweet,finalstamp)
                    
                    #Check if it is the last user from last batch
                    if sn == final_name and not check_stamp:
                        # print("username " + str(sn) + " userstamp " + " " + str(timestamp_tweet) )
                       
                        time.sleep(11.8);
                        break;
                
                    #new tweet, send reply to user
                    else:
                        
                        #New User Great
                        print(" ********ATTENTION***********")
                        print(" ")
                        print(" ***New User: " + str(sn))
                        print(" ")
                        
                        #get tweet, and friends from user
                        try:
                            all_friends,all_tweets = get_user_tweets(sn)
                        except tweepy.error.TweepError as e:
                            time.sleep(180)
                            all_friends,all_tweets = get_user_tweets(sn)
                        
                        
                        # Too few Twitter activity by user
                        # send most popular
                        if sn != "PFather101" and len(all_tweets) < 12:
                            print('*****Two Few Twitter Activity: Select most Popular Podcasts for user: ' + str(sn))
                            try:
                                # print("here")
                                
                                podcast_recommendations = self.listen_notes_favorite(3)
                                m = "@" + sn + " listen "  + podcast_recommendations
                                s = api.update_status(m, tweet.id)
                                continue;
                            
                            
                            except tweepy.error.TweepError as e:
                                time.sleep(180)
                                podcast_recommendations = self.listen_notes_favorite(3)
                                m = "@" + sn + " listen "  + podcast_recommendations
                                s = api.update_status(m, tweet.id)
                                continue;
                    
                    
                    
                        ####In the following we try get podcast recommendation based on who Twitter posting, following, buzz words

                        #Use tdidf to get podcasts basse on what they post
                        print("******selecting recommendations based on Twitter Activity for user: " + str(sn))
                        print(" ")
                        
                        #In the following we use the LP infrastructure to select the tweets for recommendations
                        
                        #First use TF-IDF
                        tfidf_urls, podcast_descriptions, max_vals_idx = self.get_from_tfidf(sn)
                        favorite_podcast_url = self.listen_notes_favorite()

                        #Now Use the celebrities the user follows
                        #get podcasts basse on who they follow
                        #url_hashtag,hashtags,signal_hashtags = get_from_hashtag(all_friends)
                        url_hashtag,hashtags,signal_hashtags = self.get_from_hashtag(all_friends)
                            #get podcast based on buzz words

                        # Now select those based on Buzz Words
                        buzzwords_urls = self.get_from_listen_notes(podcast_descriptions)


                        #now create twitter message to user based on the podcast we obtained
                        podcast_recommendations = str()
                        podcast_recommendations_list = []

                        #try those matching posting, else pick a popular one
                        if len(tfidf_urls) > 0:
                            
                            for _podcast in tfidf_urls:
                                try:
                                    podcast_recommendations = _podcast + " " + podcast_recommendations
                                    podcast_recommendations_list.append(_podcast)
                                
                                #Dealing with potential Errors
                                except TypeError:
                                    _podcast_rec = self.listen_notes_favorite(1)
                                    podcast_recommendations = _podcast_rec + " " + podcast_recommendations
                                    podcast_recommendations_list.append(_podcast_rec);

                        else:
                            
                            #If we here NLP did not find anything so send the user a popular podcast
                            _podcast_rec = self.listen_notes_favorite(3)
                            podcast_recommendations = _podcast_rec + " " + podcast_recommendations
                            podcast_recommendations_list.append(_podcast_rec);



                        #try those based on who the user is following, else pick a popular one

                        if len(url_hashtag) > 0:
                            
                            try:
                                podcast_recommendations = url_hashtag[0] + " " + podcast_recommendations
                                podcast_recommendations_list.append(url_hashtag[0]);
                            
                            #Dealing with potential Errors
                            except TypeError:
                                _podcast_rec = self.listen_notes_favorite(1)
                                podcast_recommendations = _podcast_rec + " " + podcast_recommendations
                                podcast_recommendations_list.append(_podcast_rec);
                        else:
                            
                            #If we here NLP did not find anything so send the user a popular podcast
                            _podcast_rec = self.listen_notes_favorite(1)
                            podcast_recommendations = _podcast_rec + " " + podcast_recommendations
                            podcast_recommendations_list.append(_podcast_rec);


                        #try those on buzz words in the pool of recommendations, else pick a popular one
                        if len(buzzwords_urls) >0:
                            try:
                                podcast_recommendations = buzzwords_urls[0] + " " + podcast_recommendations
                                podcast_recommendations_list.append(buzzwords_urls[0]);
                            #Dealing with potential Errors
                            except TypeError:
                                
                                _podcast_rec = self.listen_notes_favorite(1)
                                podcast_recommendations = _podcast_rec + " " + podcast_recommendations
                                podcast_recommendations_list.append(_podcast_rec);
                        else:
                            #If we here NLP did not find anything so send the user a popular podcast
                            _podcast_rec = self.listen_notes_favorite(1)
                            podcast_recommendations = _podcast_rec + " " + podcast_recommendations
                            podcast_recommendations_list.append(_podcast_rec);


                        #***Sending Reply To User******************
                        #***Sending Reply To User******************
                        #***Sending Reply To User******************

                        if len(podcast_recommendations_list) > 0:
                            try:
                                m = "@" + sn + " listen "  + podcast_recommendations
                                s = api.update_status(m, tweet.id)
                                print("sent following recommendations : " + str(sn) + "\n")
                                print(m)
                                print(' ')
                            except tweepy.error.TweepError as e:
                                time.sleep(180)
                                m = "@" + sn + " listen "  + podcast_recommendations
                                s = api.update_status(m, tweet.id)
                                print("sent following recommendations : " + str(sn) + '\n')
                                print(m)
                                print(' ')

                        #In case we did not find anything send most popular to user
                        else:
                            try:
                                favorite_urls = self.listen_notes_favorite()
                                m = "@" + sn + " listen "  + favorite_urls
                                print("sent following recommendations : " + str(sn) + '\n')
                                s = api.update_status(m, tweet.id)
                                print(m)
                                print(' ')
                            
                            except tweepy.error.TweepError as e:
                                time.sleep(180)
                                favorite_urls = self.listen_notes_favorite()
                                m = "@" + sn + " listen "  + favorite_urls
                                s = api.update_status(m, tweet.id)
                                print("sent following recommendations : " + str(sn) + '\n')
                                print(m)
                                print(' ')
                
    

                    idx= idx+1
            
                        

if __name__ == "__main__":

        # This is an example of how to run the podfather once this module has
        # been imported to local enviroment
		print('Creating Tweetbot')

		
		my_bot = bot(tfidf_vectorizer)
		my_bot.run()
