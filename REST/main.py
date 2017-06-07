#Authors: Brandon Kyriss, Richard Menzel, Ava Cordero, Laura Wagner, Matthew Ruglio-Kormann
# Group: Project B, Group 9
# Date:   
# Title: Job REST API main.py

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import webapp2
import json
import time

# Define a job entity
class Job(ndb.Model):
    id = ndb.StringProperty()                           # Randomly generated identifier 
    posterName = ndb.StringProperty(required=True)      # Name of the posting party
    jobTitle = ndb.StringProperty(required=True)        # Title for the job
    jobDescription = ndb.StringProperty(required=True)  # Description of the job
    reputationScore = ndb.FloatProperty()               # Cumulative reputation score (may eventually come from user instead)
    payRate = ndb.FloatProperty()                       # Rate of pay
    isHourly = ndb.BooleanProperty()                    # Is pay hourly? If not, lumpSum.
    timeEstimate = ndb.StringProperty()                 # How much time should the job take?
    city = ndb.StringProperty()                         # City where the job will be performed
    state = ndb.StringProperty()                        # State where the job will be performed
    streetAddress = ndb.StringProperty()                # Street addy where the job will be preformed
    isInProgress = ndb.BooleanProperty()                # Is the job open or taken?
    datePosted = ndb.StringProperty()                   # Date of posting creation
    #posterID = ndb.StringProperty()                    # Will be added after User Accounts Set
    #assignedTo = ndb.StringProperty()                  # Will be added after User Accounts Set

# Define a user entity
class User(ndb.Model):
    id = ndb.StringProperty()                           # randomly generated identifier 
    realName = ndb.StringProperty(required=True)        # actual name (for display purposes) - to align with job posting?
    username = ndb.StringProperty(required=True)        # unique username
    password = ndb.StringProperty(required=True)        # this would be encrypted or hashed in real use
    email = ndb.StringProperty(required=True)           # account email for communication, registration, verification, etc.
    reputationScoreSeeker = ndb.FloatProperty()         # cumulative reputation score - derived from ratingAggregate/ratingCount
    reputationScorePoster = ndb.FloatProperty()         # cumulative reputation score - derived from ratingAggregate/ratingCount
    ratingCountSeeker = ndb.FloatProperty()             # automatically incremented with each review
    ratingCountPoster = ndb.FloatProperty()             # automatically incremented with each review
    ratingAggregateSeeker = ndb.FloatProperty()         # combined raw score of all reviews
    ratingAggregatePoster = ndb.FloatProperty()         # combined raw score of all reviews
    city = ndb.StringProperty()                         # user city
    state = ndb.StringProperty()                        # user state
    streetAddress = ndb.StringProperty()                # user street address
    zip = ndb.StringProperty()                          # user zip code to allow for tailored results
    dateJoined = ndb.StringProperty()                   # member since...




# Handler for requests regarding job entities /job
class JobHandler(webapp2.RequestHandler):

    # Add a new job posting to the database
    # datePosted set to current datetime
    # isInProgress defauts to 'false'
    # If not rating is available / as a placeholder before User exists, rating will default to 0
    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'


    def post(self):
        # Load up our new job object from the post request payload
        jobData = json.loads(self.request.body)
        newJob = Job(posterName=jobData['poster_name'], 
                     jobTitle=jobData['job_title'],
                     jobDescription=jobData['job_description'],
                     reputationScore=jobData['reputation_score'],
                     payRate=jobData['pay_rate'],
                     isHourly=jobData['is_hourly'],
                     timeEstimate=jobData['time_estimate'],
                     city=jobData['city'],
                     state=jobData['state'],
                     streetAddress=jobData['street_address'])
        # Default isInProgress to False and set datePosted to current date

        newJob.isInProgress = False
        newJob.datePosted = time.strftime("%m/%d/%Y")

        # Leave the id blank until an id is generated
        newJob.id = ''
        newJob.put()

        # Set the self urlsafe string as the job id
        newJob.id = newJob.key.urlsafe()
        newJob.put()

        # Load the job into adictionary so we can dump this fool to a JSON string for testing
        jobDict = newJob.to_dict()
        jobDict['self'] = '/job/' + newJob.key.urlsafe()

        # If the new entry was created without issue, return a 201 Created
        self.response.status = '201 Created'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/csv'
        #Return some test stuff so we know what was posted
        self.response.write(json.dumps(jobDict))


    # Get a list of all jobs or a single job by id
    def get(self, id=None):
        # If an id is passed as a param, load the id
        if id:
            job = ndb.Key(urlsafe=id).get()
            
            if job == None:
                # If no job is returend for the target ID, send a 404 response
                self.response.status = '404 Not Found'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('No job with id:{0} was found'.format(id))
            else:
                # If the id is found, return the posting as a JSON string
                job_dict = job.to_dict()
                job_dict['self'] = "/job/" + id

                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write(json.dumps(job_dict))
               
        else:
            # Get all avail jobs if no id is provided
            found = False
            jobList = ""
            query = Job.query()   # Set up a query on the db

            # Fetch first 1000 jobs
            for job in query.fetch(1000):
                # If there are jobs in the db, load em' up
                found = True
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
                if found == False:
                    # If the db is empty, return a 404
                    self.response.status = '404 Not Found'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                    self.response.headers['Content-Type'] = 'text/csv'
                    self.response.write('No jobs were found')
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
            if found == True:
                # There is likely a better way to do this, but this is how I am formatting the JSON string 
                # to contain multiple objects
                jobList = "[" + jobList.replace("}{","},{") + "]"
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write(jobList)
            else:
                self.response.status = '404 Not Found'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('No jobs were found')


    # Delete a job         
    def delete(self, id=None):
        if id:
            job = ndb.Key(urlsafe=id).get() 
            if job == None: 
                self.response.status = '404 Not Found'  
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'                   
                self.response.write('No job with id:{0} was found. Cannot delete.'.format(id))
            else:
                thisId = job.id
                thisTitle = job.jobTitle 
                job.key.delete()
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('Job:{0}, id:{1} was deleted'.format(thisTitle,thisId))
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'

    # Change an attribute of a job
    def patch(self, id=None):
        if id:
            job = ndb.Key(urlsafe=id).get() 
            if job == None:   
                self.response.status = '404 Not Found'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'                   
                self.response.write('No job with id:{0} was found. Cannot modify.'.format(id))
            else:
                dataChanged = False
                thisId = job.id
                thisTitle = job.jobTitle
                jobData = json.loads(self.request.body)
                if 'job_title' in jobData:
                    job.jobTitle = jobData['job_title']
                    dataChanged = True
                if 'poster_name' in jobData:
                    job.posterName = jobData['poster_name']
                    dataChanged = True
                if 'job_description' in jobData:
                    job.jobDescription = jobData['job_description']
                    dataChanged = True
                if 'pay_rate' in jobData:
                    job.payRate = jobData['pay_rate']
                    dataChanged = True
                if 'is_hourly' in jobData:
                    job.isHourly = jobData['is_hourly']
                    dataChanged = True
                if 'time_estimate' in jobData:
                    job.timeEstimate = jobData['time_estimate']
                    dataChanged = True
                if 'city' in jobData:
                    job.city = jobData['city']
                    dataChanged = True
                if 'state' in jobData:
                    job.state = jobData['state']
                    dataChanged = True
                if 'street_address' in jobData:
                    job.streetAddress = jobData['street_address']
                    dataChanged = True
                if 'date_posted' in jobData:
                    job.datePosted = jobData['date_posted']
                    dataChanged = True
                job.put()
                if dataChanged == True:
                    self.response.status = '201 Created'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                    self.response.headers['Content-Type'] = 'text/csv'
                    self.response.write('Job id:{1} was modified'.format(thisTitle,thisId))
                else:
                    self.response.status = '404 Not Found'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                    self.response.headers['Content-Type'] = 'text/csv'
                    self.response.write('No valid property was modified')
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('An id is required to modify a job posting')


# Once user ids are incorporated, handle here. Here we assign a user id to the job object for assignedTo
class JobAssignmentHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

        # Change 
    def put(self, id=None):
        if id:  
            job = ndb.Key(urlsafe=id).get() 
            if job == None:   
                self.response.status = '404 Not Found'    
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'               
                self.response.write('No job with id:{0} was found. Cannot assign.'.format(id))
            else:
                if job.isInProgress == True:
                    self.response.status = '403 Forbidden'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                    self.response.headers['Content-Type'] = 'text/csv'
                else:
                    job.isInProgress = True
                    job.put()
                    self.response.status = '201 Created'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                    self.response.headers['Content-Type'] = 'text/csv'
                    #self.response.write('Job id:{1} was modified'.format(thisTitle,thisId))
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('An id is required to assign a job posting - {0} {1}'.format(status, id))

# Once user ids are incorporated, handle here. Here we free a user id from the job object (assignedTo)
class JobUnassignmentHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

        # Change 
    def put(self, id=None):
        if id:  
            job = ndb.Key(urlsafe=id).get() 
            if job == None:   
                self.response.status = '404 Not Found'  
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                self.response.headers['Content-Type'] = 'text/csv'                 
                self.response.write('No job with id:{0} was found. Cannot assign.'.format(id))
            else:
                if job.isInProgress == False:
                    self.response.status = '403 Forbidden'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                    self.response.headers['Content-Type'] = 'text/csv'
                else:
                    job.isInProgress = False
                    job.put()
                    self.response.status = '201 Created'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
                    self.response.headers['Content-Type'] = 'text/csv'
                    #self.response.write('Job id:{1} was modified'.format(thisTitle,thisId))
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('An id is required to assign a job posting - {0} {1}'.format(status, id))

class JobCityFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        filterCity = jobData['city']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 1000 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if job.city.lower() == filterCity.lower():
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')

class JobStateFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        filterState = jobData['state']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 1000 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if job.state.lower() == filterState.lower():
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')

class JobCityStateFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        filterState = jobData['state']
        filterCity = jobData['city']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 1000 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if job.state.lower() == filterState.lower() and job.city.lower() == filterCity.lower():
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')


class JobPayRateFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        jobHourly = jobData['hourly']
        jobRate = jobData['payrate']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 1000 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if job.payRate >= jobRate and job.isHourly == jobHourly:
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')


class JobHourlyFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        jobHourly = jobData['hourly']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 1000 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if job.isHourly == jobHourly:
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')
						
class JobMinimumRatingFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        filterRating = jobData['reputation_score']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 100 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if job.reputationScore >= filterRating:
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')

class JobLocationRatingFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        filterRating = jobData['reputation_score']
        filterState = jobData['state']
        filterCity = jobData['city']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 100 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if (job.reputationScore >= filterRating) and (job.city.lower() == filterCity.lower()) and (job.state.lower() == filterState.lower()):
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')

class JobKeywordHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        keywordFilter = jobData['keyword']

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 100 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if (keywordFilter.lower() in job.jobTitle.lower()) or (keywordFilter.lower() in job.jobDescription.lower()):
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')

class JobDateFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self, id=None):
        # Get contents of the request body
        jobData = json.loads(self.request.body)
        dateFilter = time.strptime(jobData['date'],"%m/%d/%Y") 

        jobList = ""
        query = Job.query()   # Set up a query on the db

        # Fetch first 100 jobs
        for job in query.fetch(1000):
            # If there are jobs in the db, load em' up
            found = True
            if dateFilter <= time.strptime(job.datePosted,"%m/%d/%Y"):
                jobDict = job.to_dict()
                jobDict['self'] = "/job/" + job.key.urlsafe()
         
                # Add the job to our JSON string
                jobList = jobList + json.dumps(jobDict)
        if found == True and len(jobList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            jobList = "[" + jobList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(jobList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No jobs were found')




######################################################
#                   USER Handlers                    #
######################################################


# Handler for requests regarding user entities /user
class UserHandler(webapp2.RequestHandler):


    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'


    # Add a new user to the database
    # dateJoined set to current datetime
    # rating fields will default to 0
    def post(self):
    # Load up our new user object from the post request payload
        userData = json.loads(self.request.body)
        newUser = User(realName=userData['real_name'], 
    				   username=userData['username'],
    				   password=userData['password'],
    				   email=userData['email'],
    				   city=userData['city'],
    				   state=userData['state'],
    				   streetAddress=userData['street_address'],
    				   zip=userData['zip'])
    											 
        # Default rating fields to 0 and set dateJoined to current date
        newUser.reputationScorePoster = 0
    	newUser.ratingCountPoster = 0
    	newUser.ratingAggregatePoster = 0
        newUser.reputationScoreSeeker = 0
        newUser.ratingCountSeeker = 0
        newUser.ratingAggregateSeeker = 0
        newUser.dateJoined = time.strftime("%d/%m/%Y")

        # Leave the id blank until an id is generated
        newUser.id = ''
        newUser.put()

        # Set the self urlsafe string as the user id
        newUser.id = newUser.key.urlsafe()
        newUser.put()

        # Load the user into a dictionary so we can dump this fool to a JSON string for testing
        userDict = newUser.to_dict()
        userDict['self'] = '/user/' + newUser.key.urlsafe()

        # If the new entry was created without issue, return a 201 Created
        self.response.status = '201 Created'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'text/csv'
        #Return some test stuff so we know what was posted
        self.response.write(json.dumps(userDict))


    # Get a list of all users or a single user by id
    def get(self, id=None):
        # If an id is passed as a param, load the id
        if id:
            user = ndb.Key(urlsafe=id).get()
            
            if user == None:
                # If no user is returned for the target ID, send a 404 response
                self.response.status = '404 Not Found'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('No user with id:{0} was found'.format(id))
            else:
                # If the id is found, return the posting as a JSON string
                user_dict = user.to_dict()
                user_dict['self'] = "/user/" + id

                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write(json.dumps(user_dict))
               
        else:
            # Get all avail users if no id is provided
            found = False
            userList = ""
            query = User.query()   # Set up a query on the db

            # Fetch first 1000 users -- this has the potential to be arbitrarily low
            for user in query.fetch(1000):
                # If there are users in the db, load em' up
                found = True
                userDict = user.to_dict()
                userDict['self'] = "/user/" + user.key.urlsafe()
                if found == False:
                    # If the db is empty, return a 404
                    self.response.status = '404 Not Found'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers['Content-Type'] = 'text/csv'
                    self.response.write('No users were found')
                # Add the user to our JSON string
                userList = userList + json.dumps(userDict)
            if found == True:
                # There is likely a better way to do this, but this is how I am formatting the JSON string 
                # to contain multiple objects
                userList = "[" + userList.replace("}{","},{") + "]"
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write(userList)
            else:
                self.response.status = '404 Not Found'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('No users were found')


    # Delete a user         
    def delete(self, id=None):
        if id:
            user = ndb.Key(urlsafe=id).get() 
            if user == None: 
                self.response.status = '404 Not Found'  
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'                   
                self.response.write('No user with id:{0} was found. Cannot delete.'.format(id))
            else:
                thisId = user.id
                thisUsername = user.username 
                user.key.delete()
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('User:{0}, id:{1} was deleted'.format(thisUsername,thisId))
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers['Content-Type'] = 'text/csv'

    # Change an attribute of a user profile
    def patch(self, id=None):
        if id != None:
            user = ndb.Key(urlsafe=id).get() 

            
            if user == None:   
                self.response.status = '404 Not Found'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'                   
                self.response.write('No user with id:{0} was found. Cannot modify.'.format(id))
            else:
                thisId = user.id
                thisUsername = user.username
                userData = json.loads(self.request.body)
                if 'username' in userData:
                    user.username = userData['username']
                if 'password' in userData:
                    user.password = userData['password']
                if 'real_name' in userData:
                    user.realName = userData['real_name']
                if 'email' in userData:
                    user.email = userData['email']
                if 'rating_count_seeker' in userData:
                    user.ratingCountSeeker = userData['rating_count_seeker']
                if 'rating_aggregate_seeker' in userData:
                    user.ratingAggregateSeeker = userData['rating_aggregate_seeker']
                if 'rating_count_poster' in userData:
                    user.ratingCountPoster = userData['rating_count_poster']
                if 'rating_aggregate_poster' in userData:
                    user.ratingAggregatePoster = userData['rating_aggregate_poster']
                if 'city' in userData:
                    user.city = userData['city']
                if 'state' in userData:
                    user.state = userData['state']
                if 'street_address' in userData:
                    user.streetAddress = userData['street_address']
                if 'zip' in userData:
                    user.zip = userData['zip']
                user.put()
                self.response.status = '201 Created'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('User id:{1} was modified'.format(thisUsername,thisId))
            
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('An id is required to modify a user account')

class UserUsernameFilterHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'

    def post(self):
        # Get contents of the request body
        userData = json.loads(self.request.body)
        filterUsername = userData['username']

        userList = ""
        query = User.query()   # Set up a query on the db

        # Fetch first 100 users
        for user in query.fetch(1000):
            # If there are users in the db, load em' up
            found = True
            if user.username.lower() == filterUsername.lower():
                userDict = user.to_dict()
                userDict['self'] = "/user/" + user.key.urlsafe()
         
                # Add the job to our JSON string
                userList = userList + json.dumps(userDict)
        if found == True and len(userList) > 0:
            # There is likely a better way to do this, but this is how I am formatting the JSON string 
            # to contain multiple objects
            userList = "[" + userList.replace("}{","},{") + "]"
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write(userList)
        else:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('No users were found')


class UserScoreHandler(webapp2.RequestHandler):

    def options(self):
        self.response.status = '200'
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, PATCH, DELETE")
        self.response.headers.add_header("Access-Control-Allow-Headers", "Content-Type")
        self.response.headers['Content-Type'] = 'text/html'


    def put(self, id=None):
        try:
            if id:  
                user = ndb.Key(urlsafe=id).get() 
                if user == None:   
                    self.response.status = '404 Not Found'    
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers['Content-Type'] = 'text/csv'               
                    self.response.write('No user with id:{0} was found. Cannot assign.'.format(id))
                else:
                    seekerScore = 0.0
                    posterScore = 0.0
                    userData = json.loads(self.request.body)
    			    #this should update the user's reputation score
                    if 'seekerScore' in userData:
                        seekerScore = userData['seekerScore']
                    elif 'posterScore' in userData:
                        posterScore = userData['posterScore']
                    else:
                        self.response.status = '403 Forbidden'    
                        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                        self.response.headers['Content-Type'] = 'text/csv'               
                        self.response.write('Invalid key in JSON string')
                        return

                    # Handle seeker score
                    if seekerScore != 0.0:        
    				    user.ratingCountSeeker = user.ratingCountSeeker + 1
    				    user.ratingAggregateSeeker = user.ratingAggregateSeeker + seekerScore
    				    user.reputationScoreSeeker = user.ratingAggregateSeeker / user.ratingCountSeeker
                    if posterScore != 0.0:        
                        user.ratingCountPoster = user.ratingCountPoster + 1
                        user.ratingAggregatePoster = user.ratingAggregatePoster + posterScore
                        user.reputationScorePoster = user.ratingAggregatePoster / user.ratingCountPoster

                    user.put()
                    self.response.status = '201 Created'
                    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                    self.response.headers['Content-Type'] = 'text/csv'
    			
            else:
                self.response.status = '404 Not Found'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers['Content-Type'] = 'text/csv'
                self.response.write('An id is required to update a reputation score - {0} {1}'.format(status, id))
        except:
            self.response.status = '404 Not Found'
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers['Content-Type'] = 'text/csv'
            self.response.write('Invalid put payload recieved')

# Inherits from webapp2.RequestHandler
class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write("Welcome to Post-Skynet Job Posting Board: API Guide Coming Soon...")
        self.response.write("\n\nFor now, bow to your machine overlords.")
     

# Code to add support for patch verb
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/job/assign/(.*)', JobAssignmentHandler),
    ('/job/unassign/(.*)', JobUnassignmentHandler),
    ('/job/location/rating', JobLocationRatingFilterHandler),
    ('/job/date', JobDateFilterHandler),
    ('/job/keyword', JobKeywordHandler),
    ('/job/rating', JobMinimumRatingFilterHandler),
    ('/job/citystate', JobCityStateFilterHandler),
    ('/job/payrate', JobPayRateFilterHandler),
    ('/job/hourly', JobHourlyFilterHandler),
    ('/job/city', JobCityFilterHandler),
    ('/job/state', JobStateFilterHandler),
    ('/job/(.*)', JobHandler),
    ('/job', JobHandler),
    ('/user/username', UserUsernameFilterHandler),
    ('/user/score/(.*)', UserScoreHandler),
    ('/user/(.*)', UserHandler),
    ('/user', UserHandler)
], debug=True)
